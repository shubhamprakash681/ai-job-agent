import json
from typing import Any
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.candidate import CandidateProfile
from app.models.application import Application, ApplicationEvent
from app.schemas.monitoring import (
    FollowupItem,
    FollowupListResponse,
    FollowupDraftRequest,
    FollowupDraftResponse,
    EmailParseRequest,
    EmailParseResponse,
    EmailApplyMatchRequest,
    NotificationResponse,
    NotificationListResponse,
)
from app.services.monitoring.followup_engine import FollowupEngine, calculate_followup_status
from app.services.monitoring.email_parser import EmailParser
from app.services.monitoring.status_manager import StatusManager
from app.services.monitoring.notifier import Notifier

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/followups", response_model=FollowupListResponse)
async def get_followups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FollowupListResponse:
    """
    List active submitted applications with aging indicators (7-day, 14-day, 30-day stale).
    """
    # Fetch candidate profile
    prof_res = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = prof_res.scalar_one_or_none()
    if not profile:
        return FollowupListResponse(
            items=[],
            total_needing_followup=0,
            seven_day_count=0,
            fourteen_day_count=0,
            stale_count=0,
        )

    # Query applications with job info
    query = (
        select(Application, Job)
        .join(Job, Application.job_id == Job.id)
        .where(
            Application.candidate_id == profile.id,
            Application.status.in_(["APPLIED", "INTERVIEW"]),
        )
        .order_by(Application.applied_at.asc().nulls_last())
    )
    results = (await db.execute(query)).all()

    items: list[FollowupItem] = []
    c_7 = 0
    c_14 = 0
    c_stale = 0

    for app, job in results:
        days, f_type, action = calculate_followup_status(app.applied_at)
        if f_type == "7_DAY":
            c_7 += 1
        elif f_type == "14_DAY":
            c_14 += 1
        elif f_type == "30_DAY_STALE":
            c_stale += 1

        items.append(
            FollowupItem(
                application_id=app.id,
                job_id=job.id,
                job_title=job.title,
                company=job.company or "Unknown Company",
                applied_at=app.applied_at,
                days_since_applied=days,
                status=app.status,
                followup_type=f_type,
                suggested_action=action,
            )
        )

    return FollowupListResponse(
        items=items,
        total_needing_followup=c_7 + c_14,
        seven_day_count=c_7,
        fourteen_day_count=c_14,
        stale_count=c_stale,
    )


@router.post("/followups/{application_id}/draft", response_model=FollowupDraftResponse)
async def draft_followup_email(
    application_id: int,
    request: FollowupDraftRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FollowupDraftResponse:
    """
    Generate a tailored, grounded follow-up email draft for a specific application.
    """
    app_res = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = app_res.scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} not found.",
        )

    job_res = await db.execute(select(Job).where(Job.id == application.job_id))
    job = job_res.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated job not found.",
        )

    draft = FollowupEngine.generate_draft(
        application=application,
        job=job,
        tone=request.tone,
        recipient_name=request.recipient_name,
        recipient_email=request.recipient_email,
        custom_instructions=request.custom_instructions,
    )

    # Log follow-up event
    event = ApplicationEvent(
        application_id=application.id,
        event_type="FOLLOWUP_DRAFTED",
        event_data=json.dumps({
            "tone": request.tone,
            "days_since_applied": draft.days_since_applied,
            "subject": draft.subject,
        }),
    )
    db.add(event)
    await db.commit()

    return draft


@router.post("/email/parse", response_model=EmailParseResponse)
async def parse_recruiter_email(
    request: EmailParseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmailParseResponse:
    """
    Parse an incoming recruiter email to extract meeting links, dates, and
    classify intent. Matches against existing candidate applications.
    """
    parsed = EmailParser.parse_email(
        raw_email_text=request.raw_email_text,
        sender=request.sender,
        subject=request.subject,
    )

    # Fetch candidate's active applications to match
    prof_res = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = prof_res.scalar_one_or_none()
    if profile:
        apps_query = (
            select(Application.id, Job.company, Job.title, Application.status)
            .join(Job, Application.job_id == Job.id)
            .where(Application.candidate_id == profile.id)
        )
        apps_data = [
            {"id": row[0], "company": row[1], "title": row[2], "status": row[3]}
            for row in (await db.execute(apps_query)).all()
        ]
        matched_id, rationale = EmailParser.match_to_applications(parsed, apps_data)
        parsed.suggested_application_id = matched_id
        parsed.match_rationale = rationale

    return parsed


@router.post("/email/apply")
async def apply_email_match(
    request: EmailApplyMatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Confirm an email match to an application, log the communication event,
    and optionally update application status.
    """
    app_res = await db.execute(
        select(Application).where(Application.id == request.application_id)
    )
    application = app_res.scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {request.application_id} not found.",
        )

    status_manager = StatusManager(db)

    # If status change is requested (e.g. to INTERVIEW or REJECTED)
    if request.new_status and request.new_status != application.status:
        try:
            await status_manager.update_status(
                application=application,
                user_id=current_user.id,
                target_status=request.new_status,
                reason=f"Email classification: {request.classification}",
                notes=request.notes,
                interview_details=request.event_metadata,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        # Just record email event
        event = ApplicationEvent(
            application_id=application.id,
            event_type="EMAIL_RECEIVED",
            event_data=json.dumps({
                "classification": request.classification,
                "notes": request.notes,
                "metadata": request.event_metadata,
            }),
        )
        db.add(event)
        await db.commit()
        await db.refresh(application)

    return {
        "success": True,
        "application_id": application.id,
        "status": application.status,
        "message": "Email matched and application updated successfully.",
    }


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationListResponse:
    """
    List in-app notifications and unread alert count.
    """
    notifier = Notifier(db)
    items = await notifier.list_notifications(user_id=current_user.id, unread_only=unread_only)
    unread_count = await notifier.get_unread_count(user_id=current_user.id)

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in items],
        unread_count=unread_count,
        total=len(items),
    )


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    notifier = Notifier(db)
    success = await notifier.mark_as_read(notification_id, current_user.id)
    return {"success": success}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    notifier = Notifier(db)
    count = await notifier.mark_all_as_read(current_user.id)
    return {"updated_count": count}

