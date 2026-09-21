from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.config import get_settings

router = APIRouter()

@router.get("", response_model=Dict[str, Any])
@router.get("/", response_model=Dict[str, Any], include_in_schema=False)
async def get_settings_endpoint(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    # Return non-sensitive settings
    settings = get_settings()
    return {
        "dry_run": settings.DRY_RUN,
        "human_approval": settings.HUMAN_APPROVAL_REQUIRED,
        "daily_limit": settings.DAILY_APPLICATION_LIMIT,
        "min_score": settings.MINIMUM_JOB_SCORE,
        "gemini_enabled": settings.GEMINI_ENABLED,
        "groq_enabled": settings.GROQ_ENABLED,
    }

@router.put("", response_model=Dict[str, Any])
@router.put("/", response_model=Dict[str, Any], include_in_schema=False)
async def update_settings(
    settings_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Just returning the current ones as placeholder
    settings = get_settings()
    return {
        "dry_run": settings.DRY_RUN,
        "human_approval": True,
        "daily_limit": settings.DAILY_APPLICATION_LIMIT,
        "min_score": 70,
        "gemini_enabled": bool(settings.GEMINI_API_KEY),
        "groq_enabled": bool(settings.GROQ_API_KEY)
    }
