from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.resume import ResumeVariant, ResumeVersion
from app.schemas.resume import ResumeVariantResponse, ResumeVersionResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/variants", response_model=List[ResumeVariantResponse])
async def list_variants(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ResumeVariant))
    return result.scalars().all()

@router.get("/versions", response_model=List[ResumeVersionResponse])
async def list_versions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(ResumeVersion).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/versions/{version_id}", response_model=ResumeVersionResponse)
async def get_version(
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ResumeVersion).where(ResumeVersion.id == version_id))
    version = result.scalar_one_or_none()
    
    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found")
        
    return version
