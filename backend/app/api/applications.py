from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User
from app.models.application import Application, ApplicationQuestion
from app.schemas.application import ApplicationResponse, ApplicationListResponse, ApplicationQuestionResponse
from app.api.deps import get_current_user
from app.schemas.common import MessageResponse

router = APIRouter()

@router.get("", response_model=ApplicationListResponse)
@router.get("/", response_model=ApplicationListResponse, include_in_schema=False)
async def list_applications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Application)
    
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return ApplicationListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    return app

@router.post("/{app_id}/approve", response_model=MessageResponse)
async def approve_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # status -> APPLYING if DRY_RUN else APPLIED
    # Placeholder
    return MessageResponse(message="Application approved")

@router.post("/{app_id}/reject", response_model=MessageResponse)
async def reject_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return MessageResponse(message="Application rejected")

@router.get("/{app_id}/questions", response_model=List[ApplicationQuestionResponse])
async def list_questions(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ApplicationQuestion).where(ApplicationQuestion.application_id == app_id))
    return result.scalars().all()
