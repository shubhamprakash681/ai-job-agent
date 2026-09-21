import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import CandidateProfile, CandidateFact, CandidateEvidence
from app.models.user import User
from app.services.candidate.kb_loader import get_candidate_kb


async def seed_candidate_kb(db: AsyncSession, user_id: int | None = None) -> CandidateProfile:
    """
    Seed or sync the candidate profile, atomic facts, and evidence tables
    from the candidate YAML knowledge base.
    """
    kb = get_candidate_kb(force_reload=True)

    # 1. Resolve target user
    if user_id is None:
        user_res = await db.execute(select(User).order_by(User.id.asc()).limit(1))
        user = user_res.scalar_one_or_none()
        if user is None:
            raise ValueError("No user found in database. Please run setup first.")
        user_id = user.id

    # 2. Upsert CandidateProfile
    profile_query = select(CandidateProfile).where(CandidateProfile.user_id == user_id)
    profile_res = await db.execute(profile_query)
    profile = profile_res.scalar_one_or_none()

    profile_data_dict = {
        "full_name": kb.profile.full_name,
        "email": kb.profile.email,
        "phone": kb.profile.phone,
        "location": kb.profile.location,
        "portfolio_url": kb.profile.links.portfolio,
        "github_url": kb.profile.links.github,
        "linkedin_url": kb.profile.links.linkedin,
        "current_company": kb.profile.current_employment.company,
        "current_role": kb.profile.current_employment.role,
        "total_experience_months": kb.profile.preferences.total_experience_months,
        "notice_period_days": kb.profile.preferences.notice_period_days,
        "current_ctc": kb.profile.preferences.current_ctc,
        "expected_ctc": kb.profile.preferences.expected_ctc,
        "preferred_locations": json.dumps(kb.profile.preferences.preferred_locations),
        "remote_preference": kb.profile.preferences.remote_preference,
        "target_roles": json.dumps(kb.profile.preferences.target_roles),
        "profile_data": json.dumps(kb.model_dump(), default=str),
    }

    if profile is None:
        profile = CandidateProfile(user_id=user_id, **profile_data_dict)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    else:
        for key, value in profile_data_dict.items():
            setattr(profile, key, value)
        await db.commit()
        await db.refresh(profile)

    # 3. Seed atomic facts and evidence
    facts = kb.get_atomic_facts()

    for fact_data in facts:
        fact_q = select(CandidateFact).where(
            CandidateFact.candidate_id == profile.id,
            CandidateFact.fact_id == fact_data.fact_id,
        )
        fact_res = await db.execute(fact_q)
        existing_fact = fact_res.scalar_one_or_none()

        metadata = {
            "keywords": fact_data.keywords,
            "metrics": [m.model_dump() for m in fact_data.metrics],
            "evidence_type": fact_data.evidence_type,
            "source_reference": fact_data.source_reference,
        }

        if existing_fact is None:
            new_fact = CandidateFact(
                candidate_id=profile.id,
                fact_id=fact_data.fact_id,
                claim=fact_data.claim,
                category=fact_data.category,
                source=fact_data.source,
                verified=fact_data.verified,
                allowed_for_resume=fact_data.allowed_for_resume,
                allowed_for_application=fact_data.allowed_for_application,
                metadata_json=json.dumps(metadata),
            )
            db.add(new_fact)
            await db.flush()  # to get new_fact.id

            # Create matching evidence record
            evidence = CandidateEvidence(
                candidate_id=profile.id,
                fact_id=new_fact.id,
                evidence_type=fact_data.evidence_type,
                description=fact_data.claim,
                source_reference=fact_data.source_reference,
                confidence=1.0 if fact_data.verified else 0.8,
            )
            db.add(evidence)
        else:
            existing_fact.claim = fact_data.claim
            existing_fact.category = fact_data.category
            existing_fact.source = fact_data.source
            existing_fact.verified = fact_data.verified
            existing_fact.allowed_for_resume = fact_data.allowed_for_resume
            existing_fact.allowed_for_application = fact_data.allowed_for_application
            existing_fact.metadata_json = json.dumps(metadata)

    await db.commit()
    await db.refresh(profile)
    return profile

