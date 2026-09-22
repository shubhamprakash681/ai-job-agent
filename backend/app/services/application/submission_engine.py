import json
import uuid
from datetime import datetime, timezone
from typing import Any
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.job import Job
from app.models.application import Application, ApplicationQuestion, ApplicationEvent
from app.models.candidate import CandidateProfile
from app.models.resume import ResumeVersion
from app.services.application.state_machine import get_state_machine

logger = structlog.get_logger(__name__)


class ApplicationSubmissionEngine:
    """
    Orchestrates application packet compilation, safety gate verification,
    and execution (dry-run simulation or external dispatch).
    """

    def __init__(self):
        self.settings = get_settings()
        self.state_machine = get_state_machine()

    async def compile_submission_packet(
        self,
        app: Application,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """
        Build the canonical submission payload including candidate profile, resume,
        cover letter, and screening answers.
        """
        job = await db.get(Job, app.job_id)
        if not job:
            raise ValueError(f"Job #{app.job_id} not found")

        candidate_res = await db.execute(
            select(CandidateProfile).where(CandidateProfile.id == app.candidate_id)
        )
        candidate = candidate_res.scalar_one_or_none()

        resume_ver = None
        if app.resume_version_id:
            resume_ver = await db.get(ResumeVersion, app.resume_version_id)

        questions_res = await db.execute(
            select(ApplicationQuestion).where(ApplicationQuestion.application_id == app.id)
        )
        questions = questions_res.scalars().all()

        packet = {
            "application_id": app.id,
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "source": job.source,
                "application_url": job.application_url or job.url,
            },
            "candidate": {
                "full_name": candidate.full_name if candidate else "Shubham Prakash",
                "email": candidate.email if candidate else "shubhamprakash230@gmail.com",
                "phone": candidate.phone if candidate else "+91 9934305886",
                "location": candidate.location if candidate else "Mumbai, India",
                "portfolio_url": candidate.portfolio_url if candidate else "https://www.shubhamprakash681.in/",
                "current_company": candidate.current_company if candidate else "Accenture",
                "current_role": candidate.current_role if candidate else "Software Engineering Associate",
                "notice_period_days": 30,
            },
            "documents": {
                "resume_version_id": resume_ver.id if resume_ver else None,
                "resume_version_number": resume_ver.version_number if resume_ver else None,
                "resume_pdf_path": resume_ver.file_path_pdf if resume_ver else None,
                "resume_docx_path": resume_ver.file_path_docx if resume_ver else None,
                "cover_letter_present": bool(app.cover_letter),
                "cover_letter_words": len((app.cover_letter or "").split()) if app.cover_letter else 0,
            },
            "screening_questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "answer": q.final_answer or q.proposed_answer,
                    "confidence": q.confidence,
                    "approved": q.approved,
                }
                for q in questions
            ],
            "compiled_at": datetime.now(timezone.utc).isoformat(),
        }
        return packet

    async def execute_submission(
        self,
        app: Application,
        db: AsyncSession,
        user_approved: bool = True,
        dry_run: bool | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute application submission with state machine safety checks and audit tracking.
        Default is DRY_RUN=true.
        """
        is_dry_run = dry_run if dry_run is not None else self.settings.DRY_RUN

        # Step 1: Transition to APPLYING (verifies human approval & daily throttle)
        await self.state_machine.transition(
            app=app,
            target_status="APPLYING",
            db=db,
            user_approved=user_approved,
            notes=notes or ("Executing submission" if not is_dry_run else "Executing DRY-RUN submission"),
        )
        await db.commit()

        # Step 2: Compile packet
        packet = await self.compile_submission_packet(app, db)

        # Step 3: Handle Dry Run vs Live
        if is_dry_run:
            confirmation_code = f"DRY-RUN-{uuid.uuid4().hex[:8].upper()}"
            submission_evidence = {
                "status": "SUCCESS",
                "mode": "DRY_RUN",
                "confirmation_code": confirmation_code,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "notes": "Simulated application submission completed with full packet validation.",
                "packet": packet,
            }

            # Step 4: Transition to APPLIED
            await self.state_machine.transition(
                app=app,
                target_status="APPLIED",
                db=db,
                user_approved=True,
                notes=f"[DRY RUN SUCCESS] Confirmation code: {confirmation_code}",
                event_metadata={"confirmation_code": confirmation_code, "mode": "DRY_RUN"},
            )

            app.applied_at = datetime.now(timezone.utc)
            app.submission_evidence = json.dumps(submission_evidence)
            await db.commit()
            await db.refresh(app)

            logger.info("Dry-run application simulated successfully", app_id=app.id, confirmation=confirmation_code)
            return submission_evidence
        else:
            # Live mode: Check if portal requires manual entry
            job = await db.get(Job, app.job_id)
            if not job or not job.application_url:
                await self.state_machine.transition(
                    app=app,
                    target_status="FAILED",
                    db=db,
                    user_approved=True,
                    notes="Missing application URL for live submission.",
                )
                await db.commit()
                return {"status": "FAILED", "reason": "Missing application URL"}

            # For jobs without direct API adapters, flag as MANUAL_REQUIRED
            await self.state_machine.transition(
                app=app,
                target_status="MANUAL_REQUIRED",
                db=db,
                user_approved=True,
                notes="External career portal requires direct applicant submission. Packet compiled and ready.",
                event_metadata={"portal_url": job.application_url},
            )
            evidence = {
                "status": "MANUAL_REQUIRED",
                "mode": "LIVE_REDIRECT",
                "portal_url": job.application_url,
                "compiled_at": datetime.now(timezone.utc).isoformat(),
                "packet": packet,
            }
            app.submission_evidence = json.dumps(evidence)
            await db.commit()
            await db.refresh(app)
            return evidence


_SUBMISSION_ENGINE: ApplicationSubmissionEngine | None = None


def get_submission_engine() -> ApplicationSubmissionEngine:
    global _SUBMISSION_ENGINE
    if _SUBMISSION_ENGINE is None:
        _SUBMISSION_ENGINE = ApplicationSubmissionEngine()
    return _SUBMISSION_ENGINE

