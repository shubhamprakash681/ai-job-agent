from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.db.session import get_db
from app.models.user import User
from app.models.job import Job, JobScore
from app.models.application import Application, ApplicationEvent
from app.api.deps import get_current_user
from app.schemas.analytics import (
    FunnelResponse,
    BreakdownsResponse,
    TimelineResponse,
    LLMUsageResponse,
    LearningLoopResponse,
    DashboardSummaryResponse,
)
from app.services.analytics.funnel_engine import FunnelEngine
from app.services.analytics.breakdown_engine import BreakdownEngine
from app.services.analytics.learning_loop import LearningLoopAdvisor
from app.services.analytics.cost_tracker import LLMCostTracker
from app.services.analytics.timeline_engine import TimelineEngine

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns real dashboard KPI summary metrics directly from the database."""
    # 1. Total Jobs
    total_jobs_res = await db.execute(select(func.count(Job.id)))
    total_jobs = total_jobs_res.scalar_one() or 0

    # 2. New Jobs Today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    new_jobs_res = await db.execute(select(func.count(Job.id)).where(Job.created_at >= today_start))
    new_jobs_today = new_jobs_res.scalar_one() or 0

    # 3. High Priority Jobs (score >= 70 or fit_category in AUTO_PREPARE, HIGH_PRIORITY)
    hp_res = await db.execute(
        select(func.count(JobScore.id)).where(
            or_(
                JobScore.total_score >= 70,
                JobScore.fit_category.in_(["AUTO_PREPARE", "HIGH_PRIORITY"])
            )
        )
    )
    high_priority_jobs = hp_res.scalar_one() or 0

    # 4. Applications Counts
    pending_res = await db.execute(
        select(func.count(Application.id)).where(
            Application.status.in_(["RESUME_READY", "READY_TO_APPLY", "AWAITING_APPROVAL"])
        )
    )
    applications_pending = pending_res.scalar_one() or 0

    submitted_res = await db.execute(
        select(func.count(Application.id)).where(
            Application.status.in_(["APPLIED", "INTERVIEW", "OFFER"])
        )
    )
    applications_submitted = submitted_res.scalar_one() or 0

    total_apps_res = await db.execute(select(func.count(Application.id)))
    applications_total = total_apps_res.scalar_one() or 0

    # 5. Interviews Count
    interview_res = await db.execute(
        select(func.count(Application.id)).where(
            Application.status.in_(["INTERVIEW", "OFFER"])
        )
    )
    interview_count = interview_res.scalar_one() or 0

    # 6. Response Rate
    response_rate = round((interview_count / applications_submitted), 3) if applications_submitted > 0 else 0.0

    # 7. Top Companies
    comp_res = await db.execute(
        select(Job.company)
        .where(Job.company.isnot(None))
        .group_by(Job.company)
        .order_by(func.count(Job.id).desc())
        .limit(5)
    )
    top_companies = [row[0] for row in comp_res.all() if row[0]]

    # 8. Top Cities
    breakdown_eng = BreakdownEngine(db)
    loc_breakdown = await breakdown_eng._get_location_breakdown()
    top_cities = [loc.location for loc in loc_breakdown[:5] if loc.location != "Unspecified"]

    return DashboardSummaryResponse(
        total_jobs=total_jobs,
        new_jobs_today=new_jobs_today,
        high_priority_jobs=high_priority_jobs,
        applications_pending=applications_pending,
        applications_submitted=applications_submitted,
        applications_total=applications_total,
        interview_count=interview_count,
        response_rate=response_rate,
        top_companies=top_companies,
        top_cities=top_cities,
    )


@router.get("/funnel", response_model=FunnelResponse)
async def get_funnel(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculates multi-stage conversion funnel and drop-off analytics."""
    engine = FunnelEngine(db)
    return await engine.get_funnel_metrics()


@router.get("/breakdowns", response_model=BreakdownsResponse)
async def get_breakdowns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Computes breakdowns across job sources, resume variants, locations, and employers."""
    engine = BreakdownEngine(db)
    return await engine.get_breakdowns()


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline(
    days: int = Query(default=30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns chronological activity trends over 7, 30, or 90 days."""
    engine = TimelineEngine(db)
    return await engine.get_timeline(days=days)


@router.get("/llm-usage", response_model=LLMUsageResponse)
async def get_llm_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns token consumption, provider distribution, and cost audit metrics."""
    tracker = LLMCostTracker(db)
    return await tracker.get_usage_metrics()


@router.get("/insights", response_model=LearningLoopResponse)
async def get_learning_loop_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns outcome-driven strategy recommendations while ensuring candidate facts remain immutable."""
    advisor = LearningLoopAdvisor(db)
    return await advisor.generate_insights()
