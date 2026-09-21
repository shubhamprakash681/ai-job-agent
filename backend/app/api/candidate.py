from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.candidate import CandidateFact, CandidateProfile
from app.models.user import User
from app.schemas.candidate import (
    CandidateFactResponse,
    CandidateProfileResponse,
    CandidateProfileUpdate,
)

router = APIRouter()


@router.get("/", response_model=CandidateProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CandidateProfileResponse:
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        now = datetime.now(timezone.utc)
        return CandidateProfileResponse(
            id=0,
            user_id=current_user.id,
            full_name="Shubham Prakash",
            email=current_user.email,
            location="Mumbai, India",
            portfolio_url="https://shubhamprakash681.in/",
            current_company="Accenture",
            current_role="Packaged App Development Analyst",
            total_experience_months=39,
            created_at=now,
            updated_at=now,
        )

    return profile  # type: ignore[return-value]


@router.put("/", response_model=CandidateProfileResponse)
async def update_profile(
    update_data: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CandidateProfileResponse:
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=update_data.full_name or current_user.full_name,
        )
        db.add(profile)

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)
    return profile  # type: ignore[return-value]


@router.get("/facts", response_model=list[CandidateFactResponse])
async def list_facts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CandidateFactResponse]:
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        return []

    result = await db.execute(
        select(CandidateFact).where(CandidateFact.candidate_id == profile.id)
    )
    return result.scalars().all()  # type: ignore[return-value]


@router.get("/facts/{fact_id}", response_model=CandidateFactResponse)
async def get_fact(
    fact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CandidateFactResponse:
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    result = await db.execute(
        select(CandidateFact).where(
            CandidateFact.id == fact_id,
            CandidateFact.candidate_id == profile.id,
        )
    )
    fact = result.scalar_one_or_none()

    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")

    return fact  # type: ignore[return-value]
