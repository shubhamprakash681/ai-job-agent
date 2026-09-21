import pytest
from httpx import AsyncClient

from app.services.candidate.kb_loader import get_candidate_kb
from app.services.candidate.evidence_engine import get_evidence_engine


def test_candidate_kb_loads():
    """Verify all YAML files parse into strongly-typed models."""
    kb = get_candidate_kb(force_reload=True)
    assert kb.profile.full_name == "Shubham Prakash"
    assert kb.profile.current_employment.company == "Accenture"
    assert len(kb.experiences) == 4
    assert len(kb.projects) == 2
    assert len(kb.skill_categories) >= 6
    assert len(kb.variants) == 4

    skills = kb.get_all_skills()
    assert "Java" in skills
    assert "Spring Boot" in skills
    assert "React" in skills
    assert "Kafka" in skills
    assert "Redis" in skills


def test_atomic_facts_generation():
    """Verify atomic facts are generated for experience, projects, skills, education."""
    kb = get_candidate_kb()
    facts = kb.get_atomic_facts()
    assert len(facts) >= 50

    fact_ids = [f.fact_id for f in facts]
    assert "fact.profile.experience_tenure" in fact_ids
    assert "fact.exp.tcs.auth_migration" in fact_ids
    assert "fact.proj.proj.tradex.overview" in fact_ids
    assert "fact.edu.edu.cusat" in fact_ids


def test_evidence_engine_valid_claim():
    """Verify that claims derived from verified resume pass."""
    engine = get_evidence_engine()
    res = engine.verify_claim(
        "Migrated ArcGIS authentication from frontend to backend and implemented JWT, OAuth2, and Auth0 SSO."
    )
    assert res.is_supported is True
    assert res.confidence >= 0.7
    assert len(res.supporting_evidence) > 0


def test_evidence_engine_rejects_hallucination():
    """Verify that unverified technologies are caught and rejected."""
    engine = get_evidence_engine()
    res = engine.verify_claim(
        "Led high-throughput microservices architecture using Kubernetes, Rust, and Go."
    )
    assert res.is_supported is False
    assert res.confidence == 0.0
    assert len(res.conflicts) > 0
    assert "kubernetes" in res.conflicts[0] or "rust" in res.conflicts[0] or "go" in res.conflicts[0]


def test_evidence_engine_rejects_inflated_tenure():
    """Verify tenure inflation is flagged."""
    engine = get_evidence_engine()
    res = engine.verify_claim("Over 8 years of professional Java software engineering experience.")
    assert res.is_supported is False
    assert any("tenure" in c.lower() or "years" in c.lower() for c in res.conflicts)


def test_resume_validation_clean_pass():
    """Verify that a legitimate resume section passes with high confidence."""
    engine = get_evidence_engine()
    clean_resume = """
    # Shubham Prakash
    Software Engineer with 3 years of experience building scalable applications using Java, Spring Boot, React.
    
    ## Professional Experience
    Tata Consultancy Services (TCS Digital)
    - Developed enterprise applications using Java, Spring Boot Microservices, React, TypeScript, and Node.js.
    - Optimized caching supporting 10,000+ concurrent users with zero data conflicts.
    - Migrated ArcGIS authentication from frontend to backend and implemented JWT, OAuth2, and Auth0 SSO.
    """
    report = engine.validate_resume_content(clean_resume)
    assert report.passed is True
    assert report.confidence_score >= 0.7
    assert len(report.hallucinated_skills) == 0
    assert len(report.errors) == 0


def test_resume_validation_detects_fabrication():
    """Verify that a resume with fabricated skills and inflated metrics is rejected."""
    engine = get_evidence_engine()
    fake_resume = """
    # Fake Engineer
    Staff Engineer with 12 years of experience leading Kubernetes and Golang architectures.
    - Scaled backend to 500,000+ concurrent users with Rust microservices.
    - Managed GraphQL gateway in production.
    """
    report = engine.validate_resume_content(fake_resume)
    assert report.passed is False
    assert report.confidence_score < 0.5
    assert len(report.errors) > 0
    assert any("kubernetes" in s.lower() for s in report.hallucinated_skills)


@pytest.mark.asyncio
async def test_candidate_api_profile(client: AsyncClient, auth_headers: dict):
    """Test GET /api/candidate/ returns seeded candidate profile."""
    res = await client.get("/api/candidate/", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Shubham Prakash"
    assert data["current_company"] == "Accenture"
    assert data["location"] == "Mumbai, India"


@pytest.mark.asyncio
async def test_candidate_api_sync_and_facts(client: AsyncClient, auth_headers: dict):
    """Test POST /api/candidate/sync and GET /api/candidate/facts."""
    sync_res = await client.post("/api/candidate/sync", headers=auth_headers)
    assert sync_res.status_code == 200
    sync_data = sync_res.json()
    assert sync_data["status"] == "synced"
    assert sync_data["facts_count"] >= 50

    facts_res = await client.get("/api/candidate/facts", headers=auth_headers)
    assert facts_res.status_code == 200
    facts = facts_res.json()
    assert len(facts) >= 50


@pytest.mark.asyncio
async def test_candidate_api_validate_claim(client: AsyncClient, auth_headers: dict):
    """Test POST /api/candidate/validate-claim."""
    # 1. Valid claim
    res_valid = await client.post(
        "/api/candidate/validate-claim",
        headers=auth_headers,
        json={"claim": "Built TradeX paper trading platform using Kafka and WebSockets."},
    )
    assert res_valid.status_code == 200
    assert res_valid.json()["is_supported"] is True

    # 2. Invalid claim
    res_invalid = await client.post(
        "/api/candidate/validate-claim",
        headers=auth_headers,
        json={"claim": "Deployed Ethereum smart contracts using Solidity and Rust."},
    )
    assert res_invalid.status_code == 200
    assert res_invalid.json()["is_supported"] is False

