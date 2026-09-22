import json
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.models.job import Job, JobScore
from app.models.candidate import CandidateProfile
from app.models.resume import ResumeVersion
from app.models.application import Application, ApplicationQuestion, ApplicationEvent
from app.schemas.application import (
    ApplicationResponse,
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationQuestionResponse,
    ApplicationQuestionUpdateRequest,
    ApplicationEventResponse,
    ApplicationApproveRequest,
    ApplicationRejectRequest,
    ApplicationPrepareRequest,
)
from app.schemas.common import MessageResponse
from app.api.deps import get_current_user
from app.services.application.state_machine import get_state_machine
from app.services.application.question_engine import get_question_engine
from app.services.application.submission_engine import get_submission_engine
from app.services.resume.tailor import get_resume_tailor
from app.services.cover_letter.generator import get_cover_letter_generator

router = APIRouter()


@router.get("", response_model=ApplicationListResponse)
@router.get("/", response_model=ApplicationListResponse, include_in_schema=False)
async def list_applications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    min_score: int | None = Query(None, ge=0, le=100),
    search: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplicationListResponse:
    """
    List all applications with rich filters (status, minimum job score, keyword search),
    enriching with target job company, role title, and daily limit stats.
    """
    settings = get_settings()
    state_machine = get_state_machine()

    query = select(Application, Job).join(Job, Application.job_id == Job.id)
    count_query = select(func.count(Application.id)).join(Job, Application.job_id == Job.id)

    if status and status != "all":
        query = query.where(Application.status == status)
        count_query = count_query.where(Application.status == status)

    if min_score is not None:
        query = query.where(Application.job_score >= min_score)
        count_query = count_query.where(Application.job_score >= min_score)

    if search:
        search_filter = or_(
            Job.title.ilike(f"%{search}%"),
            Job.company.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(Application.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    rows = result.all()

    items: list[ApplicationResponse] = []
    for app, job in rows:
        app_resp = ApplicationResponse.model_validate(app)
        app_resp.job_title = job.title
        app_resp.job_company = job.company
        items.append(app_resp)

    daily_count = await state_machine.get_today_applications_count(db)

    return ApplicationListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        daily_count=daily_count,
        daily_limit=settings.DAILY_APPLICATION_LIMIT,
    )


@router.get("/{app_id}", response_model=ApplicationDetailResponse)
async def get_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplicationDetailResponse:
    """
    Retrieve full application packet: job details, tailored resume version,
    cover letter, screening questions, and event audit timeline.
    """
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.refresh(app)

    job = await db.get(Job, app.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Associated Job not found")

    # Resume version info
    resume_ver = None
    if app.resume_version_id:
        resume_ver = await db.get(ResumeVersion, app.resume_version_id)

    # Questions
    q_res = await db.execute(
        select(ApplicationQuestion)
        .where(ApplicationQuestion.application_id == app.id)
        .order_by(ApplicationQuestion.id.asc())
    )
    questions = q_res.scalars().all()

    # Events
    ev_res = await db.execute(
        select(ApplicationEvent)
        .where(ApplicationEvent.application_id == app.id)
        .order_by(ApplicationEvent.id.desc())
    )
    events = ev_res.scalars().all()

    parsed_evidence = None
    if app.submission_evidence:
        try:
            parsed_evidence = json.loads(app.submission_evidence)
        except Exception:
            pass

    detail = ApplicationDetailResponse(
        id=app.id,
        job_id=app.job_id,
        candidate_id=app.candidate_id,
        status=app.status,
        resume_version_id=app.resume_version_id,
        cover_letter=app.cover_letter,
        application_url=app.application_url or job.application_url or job.url,
        applied_at=app.applied_at,
        job_score=app.job_score,
        notes=app.notes,
        submission_evidence=app.submission_evidence,
        job_title=job.title,
        job_company=job.company,
        job_location=job.locations,
        job_description=job.description,
        resume_version_number=resume_ver.version_number if resume_ver else None,
        resume_pdf_path=resume_ver.file_path_pdf if resume_ver else None,
        questions=[ApplicationQuestionResponse.model_validate(q) for q in questions],
        events=[ApplicationEventResponse.model_validate(e) for e in events],
        submission_evidence_parsed=parsed_evidence,
        created_at=app.created_at,
        updated_at=app.updated_at,
    )
    return detail


@router.post("/prepare/{job_id}", response_model=ApplicationDetailResponse)
async def prepare_application_endpoint(
    job_id: int,
    req: ApplicationPrepareRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplicationDetailResponse:
    """
    Bundle a target job, tailored resume, and cover letter into an application packet,
    generate and answer screening questions, and advance status to AWAITING_APPROVAL.
    """
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get or create candidate profile
    prof_res = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = prof_res.scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=current_user.full_name or "Shubham Prakash",
            email=current_user.email,
            location="Mumbai, India",
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    # 1. Ensure Tailored Resume exists
    tailor = get_resume_tailor()
    variant_id = req.variant_id if req else None
    resume_ver = await tailor.tailor_for_job(job=job, variant_id=variant_id, db=db)

    # 2. Ensure Cover Letter exists
    tone = req.tone if req else "technical"
    custom_instructions = req.custom_instructions if req else None
    cl_generator = get_cover_letter_generator()
    cl_res = await cl_generator.generate_cover_letter(
        job=job,
        tone=tone,
        custom_instructions=custom_instructions,
        db=db,
    )

    # 3. Find or create Application record
    app_res = await db.execute(
        select(Application).where(
            Application.job_id == job_id,
            Application.candidate_id == profile.id,
        )
    )
    app = app_res.scalar_one_or_none()

    # Get score if available
    score_res = await db.execute(select(JobScore).where(JobScore.job_id == job_id))
    score = score_res.scalar_one_or_none()
    total_score = score.total_score if score else 70

    if not app:
        app = Application(
            job_id=job_id,
            candidate_id=profile.id,
            status="DISCOVERED",
            resume_version_id=resume_ver.id,
            cover_letter=cl_res.content_markdown,
            application_url=job.application_url or job.url,
            job_score=total_score,
        )
        db.add(app)
        await db.commit()
        await db.refresh(app)
    else:
        app.resume_version_id = resume_ver.id
        app.cover_letter = cl_res.content_markdown
        app.job_score = total_score
        await db.commit()

    # 4. Generate & Save Screening Questions
    q_engine = get_question_engine()
    existing_q_res = await db.execute(
        select(ApplicationQuestion).where(ApplicationQuestion.application_id == app.id)
    )
    existing_questions = existing_q_res.scalars().all()

    if not existing_questions:
        generated_questions = q_engine.generate_screening_packet(job, profile)
        for gq in generated_questions:
            db_q = ApplicationQuestion(
                application_id=app.id,
                question=gq.question,
                proposed_answer=gq.proposed_answer,
                final_answer=gq.proposed_answer,
                answer_source=gq.answer_source,
                confidence=gq.confidence,
                requires_human=gq.requires_human,
                approved=not gq.requires_human,
            )
            db.add(db_q)
        await db.commit()

    # 5. Transition to AWAITING_APPROVAL
    state_machine = get_state_machine()
    # If in DISCOVERED, advance through RESUME_READY to AWAITING_APPROVAL
    if app.status in ["DISCOVERED", "SHORTLISTED", "ANALYZING"]:
        app.status = "RESUME_READY"
    if app.status in ["RESUME_READY", "READY_TO_APPLY"]:
        await state_machine.transition(
            app=app,
            target_status="AWAITING_APPROVAL",
            db=db,
            user_approved=True,
            notes="Application packet bundled and queued for human approval.",
        )
        await db.commit()
        await db.refresh(app)

    return await get_application(app.id, current_user, db)


@router.post("/{app_id}/approve", response_model=dict[str, Any])
async def approve_application_endpoint(
    app_id: int,
    req: ApplicationApproveRequest = Body(default_factory=ApplicationApproveRequest),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Explicit human approval gate:
    Validates daily limits, executes submission (DRY_RUN simulation by default),
    and records submission evidence and status transitions.
    """
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    submission_engine = get_submission_engine()
    try:
        evidence = await submission_engine.execute_submission(
            app=app,
            db=db,
            user_approved=req.user_approved,
            dry_run=req.dry_run,
            notes=req.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission error: {str(e)}")

    return {
        "message": f"Application #{app_id} approved and submitted successfully.",
        "status": app.status,
        "evidence": evidence,
    }


@router.post("/{app_id}/reject", response_model=MessageResponse)
async def reject_application_endpoint(
    app_id: int,
    req: ApplicationRejectRequest = Body(default_factory=ApplicationRejectRequest),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Reject or withdraw an application, recording reason in audit events.
    """
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    state_machine = get_state_machine()
    try:
        await state_machine.transition(
            app=app,
            target_status="REJECTED",
            db=db,
            user_approved=True,
            notes=req.reason or "Application rejected by candidate.",
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return MessageResponse(message=f"Application #{app_id} transitioned to REJECTED.")


@router.post("/{app_id}/questions/{question_id}", response_model=ApplicationQuestionResponse)
async def update_question_endpoint(
    app_id: int,
    question_id: int,
    req: ApplicationQuestionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplicationQuestionResponse:
    """
    Update or approve a proposed screening question answer.
    """
    q = await db.get(ApplicationQuestion, question_id)
    if not q or q.application_id != app_id:
        raise HTTPException(status_code=404, detail="Question not found")

    q.final_answer = req.final_answer
    q.approved = req.approved
    await db.commit()
    await db.refresh(q)

    return ApplicationQuestionResponse.model_validate(q)
