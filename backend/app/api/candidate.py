from datetime import datetime, timezone
import json
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
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
    CandidateSyncResponse,
    ClaimValidationRequest,
    ClaimValidationResponse,
    ResumeValidationRequest,
    ResumeValidationResponse,
)
from app.services.candidate.kb_loader import get_candidate_kb
from app.services.candidate.evidence_engine import get_evidence_engine
from app.services.candidate.kb_seeder import seed_candidate_kb

router = APIRouter()


@router.get("", response_model=CandidateProfileResponse)
@router.get("/", response_model=CandidateProfileResponse, include_in_schema=False)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CandidateProfileResponse:
    """Get the candidate profile for the current user."""
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        # Auto-seed from knowledge base
        try:
            profile = await seed_candidate_kb(db, user_id=current_user.id)
        except Exception:
            kb = get_candidate_kb()
            now = datetime.now(timezone.utc)
            return CandidateProfileResponse(
                id=0,
                user_id=current_user.id,
                full_name=kb.profile.full_name,
                email=kb.profile.email,
                phone=kb.profile.phone,
                location=kb.profile.location,
                portfolio_url=kb.profile.links.portfolio,
                github_url=kb.profile.links.github,
                linkedin_url=kb.profile.links.linkedin,
                current_company=kb.profile.current_employment.company,
                current_role=kb.profile.current_employment.role,
                total_experience_months=kb.profile.preferences.total_experience_months,
                notice_period_days=kb.profile.preferences.notice_period_days,
                preferred_locations=json.dumps(kb.profile.preferences.preferred_locations),
                remote_preference=kb.profile.preferences.remote_preference,
                target_roles=json.dumps(kb.profile.preferences.target_roles),
                profile_data=json.dumps(kb.model_dump(), default=str),
                created_at=now,
                updated_at=now,
            )

    return profile  # type: ignore[return-value]


@router.put("", response_model=CandidateProfileResponse)
@router.put("/", response_model=CandidateProfileResponse, include_in_schema=False)
async def update_profile(
    update_data: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CandidateProfileResponse:
    """Update candidate profile attributes."""
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


@router.post("/sync", response_model=CandidateSyncResponse)
async def sync_knowledge_base(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CandidateSyncResponse:
    """Sync candidate YAML knowledge base into database tables."""
    profile = await seed_candidate_kb(db, user_id=current_user.id)
    facts_result = await db.execute(
        select(CandidateFact).where(CandidateFact.candidate_id == profile.id)
    )
    facts = facts_result.scalars().all()

    return CandidateSyncResponse(
        status="synced",
        message="Candidate knowledge base successfully synced from YAML files.",
        facts_count=len(facts),
        candidate_name=profile.full_name,
    )


@router.get("/facts", response_model=list[CandidateFactResponse])
async def list_facts(
    category: str | None = Query(None, description="Filter by category: experience, skill, project, education"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CandidateFactResponse]:
    """List atomic candidate facts, optionally filtered by category."""
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = await seed_candidate_kb(db, user_id=current_user.id)

    query = select(CandidateFact).where(CandidateFact.candidate_id == profile.id)
    if category:
        query = query.where(CandidateFact.category == category)

    facts_res = await db.execute(query)
    return facts_res.scalars().all()  # type: ignore[return-value]


@router.get("/facts/{fact_id}", response_model=CandidateFactResponse)
async def get_fact(
    fact_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CandidateFactResponse:
    """Retrieve a single atomic fact by fact_id or numeric id."""
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    if fact_id.isdigit():
        q = select(CandidateFact).where(
            CandidateFact.id == int(fact_id),
            CandidateFact.candidate_id == profile.id,
        )
    else:
        q = select(CandidateFact).where(
            CandidateFact.fact_id == fact_id,
            CandidateFact.candidate_id == profile.id,
        )

    res = await db.execute(q)
    fact = res.scalar_one_or_none()
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")

    return fact  # type: ignore[return-value]


@router.get("/skills")
async def get_skills_taxonomy(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Retrieve structured skills taxonomy grouped by category."""
    kb = get_candidate_kb()
    return {
        "categories": [c.model_dump() for c in kb.skill_categories],
        "total_skills": len(kb.get_all_skills()),
    }


@router.post("/validate-claim", response_model=ClaimValidationResponse)
async def validate_claim(
    request: ClaimValidationRequest,
    current_user: User = Depends(get_current_user),
) -> ClaimValidationResponse:
    """Verify whether an individual claim or sentence is grounded in candidate facts."""
    engine = get_evidence_engine()
    res = engine.verify_claim(request.claim)

    return ClaimValidationResponse(
        is_supported=res.is_supported,
        confidence=res.confidence,
        claim=res.claim,
        conflicts=res.conflicts,
        reasoning=res.reasoning,
        supporting_evidence=[e.model_dump() for e in res.supporting_evidence],
    )


@router.post("/validate-resume", response_model=ResumeValidationResponse)
async def validate_resume_text(
    request: ResumeValidationRequest,
    current_user: User = Depends(get_current_user),
) -> ResumeValidationResponse:
    """Validate full resume or cover letter text against anti-hallucination rules."""
    engine = get_evidence_engine()
    report = engine.validate_resume_content(request.content)

    return ResumeValidationResponse(
        passed=report.passed,
        confidence_score=report.confidence_score,
        supported_claims_count=report.supported_claims_count,
        unsupported_claims_count=report.unsupported_claims_count,
        supported_claims=report.supported_claims,
        unsupported_claims=report.unsupported_claims,
        hallucinated_skills=report.hallucinated_skills,
        verified_skills=report.verified_skills,
        metric_discrepancies=report.metric_discrepancies,
        warnings=report.warnings,
        errors=report.errors,
    )
