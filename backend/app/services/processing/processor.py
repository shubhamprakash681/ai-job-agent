import json
from typing import Any
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.job import Job, JobScore
from app.services.processing.classifier import (
    ClassificationResult,
    get_job_classifier,
)
from app.services.processing.prefilter import run_prefilters

logger = structlog.get_logger(__name__)


class JobProcessor:
    """
    Orchestrates the job processing pipeline:
    1. Zero-cost deterministic prefilters (experience limit, location sanity, fraud indicators).
    2. Deep classification & fit assessment via LLM / rule heuristic.
    3. Creation and update of JobScore and AuditLog.
    """

    def __init__(self):
        self.classifier = get_job_classifier()

    async def process_job(
        self,
        job_id: int,
        db: AsyncSession,
    ) -> tuple[Job, JobScore, dict[str, Any]]:
        """
        Process a single job through prefiltering and classification.
        """
        job = await db.get(Job, job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")

        # 1. Run Prefilters
        prefilter_res = run_prefilters(job)

        # Check for existing score
        score_stmt = select(JobScore).where(JobScore.job_id == job.id)
        res = await db.execute(score_stmt)
        score = res.scalar_one_or_none()

        if not prefilter_res.passed:
            # Job rejected by deterministic prefilter
            job.status = "rejected_prefilter"
            rejection_reason = prefilter_res.rejection_reason or "Failed pre-filter sanity checks"

            if not score:
                score = JobScore(
                    job_id=job.id,
                    total_score=0,
                    role_relevance=0,
                    core_skills=0,
                    distributed_systems=0,
                    experience_fit=0,
                    location_score=0,
                    job_quality=0,
                    fit_category="REJECT",
                    recommended_variant="java-backend",
                    strengths="[]",
                    gaps="[]",
                    risks=json.dumps([rejection_reason]),
                    reasoning=rejection_reason,
                    llm_score=0,
                )
                db.add(score)
            else:
                score.total_score = 0
                score.fit_category = "REJECT"
                score.reasoning = rejection_reason
                score.risks = json.dumps([rejection_reason])
                score.llm_score = 0

            # Audit log
            audit = AuditLog(
                action="JOB_PREFILTER_REJECTED",
                entity_type="job",
                entity_id=job.id,
                details=json.dumps({
                    "reason": rejection_reason,
                    "flags": prefilter_res.flags,
                }),
            )
            db.add(audit)
            await db.commit()
            await db.refresh(job)
            await db.refresh(score)

            return (
                job,
                score,
                {
                    "status": "rejected_prefilter",
                    "passed_prefilter": False,
                    "reason": rejection_reason,
                },
            )

        # 2. Run Classification
        classification = await self.classifier.classify(job, db=db)

        # Calculate breakdown scores
        role_rel = 25 if classification.role_category != "UNRELATED" else 5
        core_sk = min(25, max(10, len(classification.matched_skills) * 5))
        dist_sys = 20 if classification.role_category == "DISTRIBUTED_SYSTEMS" else 10
        exp_fit = 15 if classification.experience_fit in ["EXCELLENT", "ACCEPTABLE"] else 5
        loc_sc = 10 if not prefilter_res.warnings else 5
        job_qual = 10

        all_risks = classification.red_flags + prefilter_res.warnings

        if not score:
            score = JobScore(
                job_id=job.id,
                total_score=classification.fit_score,
                role_relevance=role_rel,
                core_skills=core_sk,
                distributed_systems=dist_sys,
                experience_fit=exp_fit,
                location_score=loc_sc,
                job_quality=job_qual,
                llm_score=classification.fit_score,
                fit_category=classification.fit_category,
                recommended_variant=classification.recommended_variant,
                strengths=json.dumps(classification.matched_skills),
                gaps=json.dumps(classification.missing_skills),
                risks=json.dumps(all_risks),
                reasoning=classification.reasoning,
            )
            db.add(score)
        else:
            score.total_score = classification.fit_score
            score.role_relevance = role_rel
            score.core_skills = core_sk
            score.distributed_systems = dist_sys
            score.experience_fit = exp_fit
            score.location_score = loc_sc
            score.job_quality = job_qual
            score.llm_score = classification.fit_score
            score.fit_category = classification.fit_category
            score.recommended_variant = classification.recommended_variant
            score.strengths = json.dumps(classification.matched_skills)
            score.gaps = json.dumps(classification.missing_skills)
            score.risks = json.dumps(all_risks)
            score.reasoning = classification.reasoning

        # Update job status if classified as REJECT
        if classification.fit_category == "REJECT":
            job.status = "rejected_fit"
        else:
            job.status = "active"

        # If job skills empty, enrich with extracted technologies
        if not job.skills and classification.primary_technologies:
            job.skills = json.dumps(classification.primary_technologies)

        # Audit log
        audit = AuditLog(
            action="JOB_CLASSIFIED",
            entity_type="job",
            entity_id=job.id,
            details=json.dumps({
                "role_category": classification.role_category,
                "fit_category": classification.fit_category,
                "fit_score": classification.fit_score,
                "variant": classification.recommended_variant,
            }),
        )
        db.add(audit)

        await db.commit()
        await db.refresh(job)
        await db.refresh(score)

        return (
            job,
            score,
            {
                "status": "classified",
                "passed_prefilter": True,
                "classification": classification.model_dump(),
            },
        )

    async def process_pending_jobs(
        self,
        db: AsyncSession,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Batch process all active jobs that do not yet have a JobScore.
        """
        # Find active jobs without score
        stmt = (
            select(Job)
            .outerjoin(JobScore, Job.id == JobScore.job_id)
            .where(JobScore.id.is_(None))
            .where(Job.status == "active")
            .limit(limit)
        )
        result = await db.execute(stmt)
        pending_jobs = result.scalars().all()

        processed = 0
        passed = 0
        rejected = 0
        job_ids = []

        for job in pending_jobs:
            try:
                _, score, res = await self.process_job(job.id, db)
                processed += 1
                job_ids.append(job.id)
                if res.get("passed_prefilter") and score.fit_category != "REJECT":
                    passed += 1
                else:
                    rejected += 1
            except Exception as e:
                logger.error("Failed to process job in batch", job_id=job.id, error=str(e))

        return {
            "total_processed": processed,
            "passed": passed,
            "rejected": rejected,
            "job_ids": job_ids,
        }


_processor_instance: JobProcessor | None = None


def get_job_processor() -> JobProcessor:
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = JobProcessor()
    return _processor_instance

