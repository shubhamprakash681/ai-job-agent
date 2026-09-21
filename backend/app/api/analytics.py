from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any

from app.db.session import get_db
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/summary", response_model=Dict[str, Any])
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    total_jobs_query = select(func.count()).select_from(Job)
    total_jobs_result = await db.execute(total_jobs_query)
    total_jobs = total_jobs_result.scalar_one()

    apps_total_query = select(func.count()).select_from(Application)
    apps_total_result = await db.execute(apps_total_query)
    applications_total = apps_total_result.scalar_one()

    return {
        "total_jobs": total_jobs,
        "new_jobs_today": 0,
        "high_priority_jobs": 0,
        "applications_pending": 0,
        "applications_submitted": 0,
        "applications_total": applications_total,
        "interview_count": 0,
        "response_rate": 0.0,
        "top_companies": [],
        "top_cities": []
    }
