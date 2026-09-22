from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.job import Job, JobScore
from app.models.application import Application, ApplicationEvent
from app.schemas.analytics import FunnelStage, FunnelSummaryRates, FunnelResponse


class FunnelEngine:
    """Calculates multi-stage conversion funnel and drop-off analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_funnel_metrics(self) -> FunnelResponse:
        # 1. Total Jobs Discovered
        jobs_query = select(func.count(Job.id))
        jobs_res = await self.db.execute(jobs_query)
        discovered_count = jobs_res.scalar_one() or 0

        # 2. Jobs Shortlisted (score >= 60 or fit_category in AUTO_PREPARE, HIGH_PRIORITY, GOOD)
        shortlisted_query = (
            select(func.count(JobScore.id))
            .select_from(JobScore)
            .where(
                or_(
                    JobScore.total_score >= 60,
                    JobScore.fit_category.in_(["AUTO_PREPARE", "HIGH_PRIORITY", "GOOD"])
                )
            )
        )
        shortlisted_res = await self.db.execute(shortlisted_query)
        shortlisted_count = shortlisted_res.scalar_one() or 0

        # 3. Applications Prepared (has reached at least ready/review state)
        prepared_statuses = [
            "RESUME_READY", "READY_TO_APPLY", "AWAITING_APPROVAL",
            "APPLYING", "APPLIED", "INTERVIEW", "OFFER"
        ]
        prepared_query = (
            select(func.count(Application.id))
            .select_from(Application)
            .where(Application.status.in_(prepared_statuses))
        )
        prepared_res = await self.db.execute(prepared_query)
        prepared_count = prepared_res.scalar_one() or 0

        # 4. Applications Submitted / Applied
        applied_statuses = ["APPLIED", "INTERVIEW", "OFFER"]
        applied_query = (
            select(func.count(Application.id))
            .select_from(Application)
            .where(Application.status.in_(applied_statuses))
        )
        applied_res = await self.db.execute(applied_query)
        applied_count = applied_res.scalar_one() or 0

        # 5. Interview Stage (status is INTERVIEW/OFFER or has interview_scheduled event)
        interview_apps_query = (
            select(Application.id)
            .where(Application.status.in_(["INTERVIEW", "OFFER"]))
        )
        interview_apps_res = await self.db.execute(interview_apps_query)
        interview_ids = set(interview_apps_res.scalars().all())

        event_interview_query = (
            select(ApplicationEvent.application_id)
            .where(ApplicationEvent.event_type.in_(["interview_scheduled", "interview"]))
        )
        event_interview_res = await self.db.execute(event_interview_query)
        interview_ids.update(event_interview_res.scalars().all())
        interview_count = len(interview_ids)

        # 6. Offer Stage (status is OFFER or has offer_received event)
        offer_apps_query = (
            select(Application.id)
            .where(Application.status == "OFFER")
        )
        offer_apps_res = await self.db.execute(offer_apps_query)
        offer_ids = set(offer_apps_res.scalars().all())

        event_offer_query = (
            select(ApplicationEvent.application_id)
            .where(ApplicationEvent.event_type.in_(["offer_received", "offer"]))
        )
        event_offer_res = await self.db.execute(event_offer_query)
        offer_ids.update(event_offer_res.scalars().all())
        offer_count = len(offer_ids)

        # Build Stage Breakdown
        stage_definitions = [
            ("DISCOVERED", "Jobs Discovered", discovered_count),
            ("SHORTLISTED", "Shortlisted Opportunities", shortlisted_count),
            ("PREPARED", "Applications Prepared", prepared_count),
            ("APPLIED", "Applications Submitted", applied_count),
            ("INTERVIEW", "Interviews Secured", interview_count),
            ("OFFER", "Offers Received", offer_count),
        ]

        stages: List[FunnelStage] = []
        prev_count = None

        for idx, (key, name, count) in enumerate(stage_definitions):
            if prev_count is None or prev_count == 0:
                drop_off_count = 0
                drop_off_pct = 0.0
                conversion_pct = 100.0 if count > 0 else 0.0
            else:
                drop_off_count = max(0, prev_count - count)
                drop_off_pct = round((drop_off_count / prev_count) * 100.0, 1)
                conversion_pct = round(min(100.0, (count / prev_count) * 100.0), 1)

            stages.append(
                FunnelStage(
                    key=key,
                    name=name,
                    count=count,
                    drop_off_count=drop_off_count,
                    drop_off_pct=drop_off_pct,
                    conversion_pct=conversion_pct,
                )
            )
            prev_count = count

        # Summary Rates
        match_to_app = round((applied_count / shortlisted_count), 3) if shortlisted_count > 0 else 0.0
        app_to_interview = round((interview_count / applied_count), 3) if applied_count > 0 else 0.0
        interview_to_offer = round((offer_count / interview_count), 3) if interview_count > 0 else 0.0
        overall = round((offer_count / applied_count), 3) if applied_count > 0 else 0.0

        summary_rates = FunnelSummaryRates(
            match_to_application_rate=match_to_app,
            application_to_interview_rate=app_to_interview,
            interview_to_offer_rate=interview_to_offer,
            overall_conversion_rate=overall,
        )

        return FunnelResponse(stages=stages, summary_rates=summary_rates)

