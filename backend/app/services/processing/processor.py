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
from app.services.scoring.scorer import get_job_scorer

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

        # 3. Run Multi-Dimensional Scoring Engine (Phase 5)
        scorer = get_job_scorer()
        scoring = scorer.score_job(
            job=job,
            role_category=classification.role_category,
            llm_score=classification.fit_score,
        )

        all_risks = list(dict.fromkeys(scoring.risks + classification.red_flags + prefilter_res.warnings))
        all_strengths = list(dict.fromkeys(scoring.strengths + classification.matched_skills))
        all_gaps = list(dict.fromkeys(scoring.gaps + classification.missing_skills))

        full_reasoning = scoring.reasoning
        if classification.reasoning and classification.reasoning not in full_reasoning:
            full_reasoning = f"{full_reasoning} AI Notes: {classification.reasoning}"

        if not score:
            score = JobScore(
                job_id=job.id,
                total_score=scoring.total_score,
                role_relevance=scoring.role_relevance,
                core_skills=scoring.core_skills,
                distributed_systems=scoring.distributed_systems,
                experience_fit=scoring.experience_fit,
                location_score=scoring.location_score,
                job_quality=scoring.job_quality,
                llm_score=classification.fit_score,
                fit_category=scoring.fit_category,
                recommended_variant=scoring.recommended_variant,
                strengths=json.dumps(all_strengths),
                gaps=json.dumps(all_gaps),
                risks=json.dumps(all_risks),
                reasoning=full_reasoning,
            )
            db.add(score)
        else:
            score.total_score = scoring.total_score
            score.role_relevance = scoring.role_relevance
            score.core_skills = scoring.core_skills
            score.distributed_systems = scoring.distributed_systems
            score.experience_fit = scoring.experience_fit
            score.location_score = scoring.location_score
            score.job_quality = scoring.job_quality
            score.llm_score = classification.fit_score
            score.fit_category = scoring.fit_category
            score.recommended_variant = scoring.recommended_variant
            score.strengths = json.dumps(all_strengths)
            score.gaps = json.dumps(all_gaps)
            score.risks = json.dumps(all_risks)
            score.reasoning = full_reasoning

        # Update job status if score indicates IGNORE
        if scoring.fit_category == "IGNORE":
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

