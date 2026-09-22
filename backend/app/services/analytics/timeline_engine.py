from datetime import datetime, timedelta, timezone
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.job import Job
from app.models.application import Application, ApplicationEvent
from app.schemas.analytics import TimelinePoint, TimelineResponse


class TimelineEngine:
    """Aggregates daily activity timelines for jobs discovered, applications submitted, and interviews."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_timeline(self, days: int = 30) -> TimelineResponse:
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)

        # 1. Jobs discovered by date
        jobs_stmt = (
            select(func.date(Job.created_at), func.count(Job.id))
            .where(Job.created_at >= start_date)
            .group_by(func.date(Job.created_at))
        )
        jobs_res = await self.db.execute(jobs_stmt)
        jobs_by_date: Dict[str, int] = {str(row[0])[:10]: row[1] for row in jobs_res.all() if row[0]}

        # 2. Applications submitted by date
        apps_stmt = (
            select(func.date(Application.created_at), func.count(Application.id))
            .where(Application.created_at >= start_date)
            .group_by(func.date(Application.created_at))
        )
        apps_res = await self.db.execute(apps_stmt)
        apps_by_date: Dict[str, int] = {str(row[0])[:10]: row[1] for row in apps_res.all() if row[0]}

        # 3. Interviews logged by date
        interviews_stmt = (
            select(func.date(ApplicationEvent.created_at), func.count(ApplicationEvent.id))
            .where(
                ApplicationEvent.created_at >= start_date,
                ApplicationEvent.event_type.in_(["interview_scheduled", "interview"])
            )
            .group_by(func.date(ApplicationEvent.created_at))
        )
        interviews_res = await self.db.execute(interviews_stmt)
        interviews_by_date: Dict[str, int] = {str(row[0])[:10]: row[1] for row in interviews_res.all() if row[0]}

        # Build chronological day-by-day points
        points: List[TimelinePoint] = []
        for i in range(days + 1):
            day_dt = (start_date + timedelta(days=i)).date()
            day_str = day_dt.isoformat()

            points.append(
                TimelinePoint(
                    date=day_str,
                    discovered=jobs_by_date.get(day_str, 0),
                    applied=apps_by_date.get(day_str, 0),
                    interviews=interviews_by_date.get(day_str, 0),
                )
            )

        return TimelineResponse(points=points, period_days=days)

