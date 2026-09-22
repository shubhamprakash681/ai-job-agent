import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job, JobScore
from app.models.application import Application, ApplicationEvent
from app.models.resume import ResumeVariant, ResumeVersion
from app.models.candidate import CandidateProfile
from app.models.llm import LLMRequest
from app.services.analytics.funnel_engine import FunnelEngine
from app.services.analytics.breakdown_engine import BreakdownEngine
from app.services.analytics.learning_loop import LearningLoopAdvisor
from app.services.analytics.cost_tracker import LLMCostTracker
from app.services.analytics.timeline_engine import TimelineEngine


async def seed_analytics_data(db: AsyncSession):
    """Seed test data for analytics testing."""
    # 1. Candidate Profile
    cand = CandidateProfile(
        user_id=1,
        full_name="Shubham Prakash",
        email="shubham@example.com",
        location="Mumbai",
    )
    db.add(cand)
    await db.flush()

    # 2. Resume Variants & Versions
    var1 = ResumeVariant(
        name="java-react-fullstack",
        display_name="Java + React Full Stack",
        description="Full stack variant",
        is_default=True,
    )
    var2 = ResumeVariant(
        name="java-backend",
        display_name="Java Backend / Spring Boot",
        description="Backend variant",
        is_default=False,
    )
    db.add_all([var1, var2])
    await db.flush()

    ver1 = ResumeVersion(variant_id=var1.id, version_number=1, content_markdown="# Resume 1")
    ver2 = ResumeVersion(variant_id=var2.id, version_number=1, content_markdown="# Resume 2")
    db.add_all([ver1, ver2])
    await db.flush()

    # 3. Jobs
    j1 = Job(
        title="Full Stack Engineer",
        company="Swiggy",
        source="greenhouse",
        locations='["Mumbai, India"]',
        remote=False,
        status="active",
    )
    j2 = Job(
        title="Senior Backend Engineer",
        company="Zomato",
        source="lever",
        locations='["Bengaluru, India"]',
        remote=True,
        status="active",
    )
    j3 = Job(
        title="Java Developer",
        company="TCS",
        source="naukri",
        locations='["Pune, India"]',
        remote=False,
        status="active",
    )
    db.add_all([j1, j2, j3])
    await db.flush()

    # 4. Job Scores
    s1 = JobScore(job_id=j1.id, total_score=85, fit_category="HIGH_PRIORITY", role_relevance=25)
    s2 = JobScore(job_id=j2.id, total_score=75, fit_category="GOOD", role_relevance=22)
    s3 = JobScore(job_id=j3.id, total_score=40, fit_category="IGNORE", role_relevance=10)
    db.add_all([s1, s2, s3])
    await db.flush()

    # 5. Applications
    app1 = Application(
        job_id=j1.id,
        candidate_id=cand.id,
        status="INTERVIEW",
        resume_version_id=ver1.id,
        applied_at=datetime.now(timezone.utc),
    )
    app2 = Application(
        job_id=j2.id,
        candidate_id=cand.id,
        status="APPLIED",
        resume_version_id=ver2.id,
        applied_at=datetime.now(timezone.utc),
    )
    db.add_all([app1, app2])
    await db.flush()

    # 6. Events
    event1 = ApplicationEvent(
        application_id=app1.id,
        event_type="interview_scheduled",
        event_data='{"round": "Technical Round 1"}',
    )
    db.add(event1)

    # 7. LLM Requests
    req1 = LLMRequest(
        provider="groq",
        model="llama-3.3-70b-versatile",
        operation="classify",
        input_tokens=500,
        output_tokens=150,
        estimated_cost=0.0,
        duration_ms=450,
        status="success",
    )
    req2 = LLMRequest(
        provider="gemini",
        model="gemini-2.0-flash",
        operation="generate_resume",
        input_tokens=1200,
        output_tokens=800,
        estimated_cost=0.0,
        duration_ms=1200,
        status="success",
    )
    db.add_all([req1, req2])
    await db.commit()


@pytest.mark.asyncio
async def test_funnel_metrics_calculation(db_session: AsyncSession):
    await seed_analytics_data(db_session)
    engine = FunnelEngine(db_session)
    funnel = await engine.get_funnel_metrics()

    assert len(funnel.stages) == 6
    stage_keys = [s.key for s in funnel.stages]
    assert stage_keys == ["DISCOVERED", "SHORTLISTED", "PREPARED", "APPLIED", "INTERVIEW", "OFFER"]

    # Verify counts:
    # 3 jobs discovered
    discovered = next(s for s in funnel.stages if s.key == "DISCOVERED")
    assert discovered.count == 3

    # 2 jobs shortlisted (scores 85 and 75 >= 60)
    shortlisted = next(s for s in funnel.stages if s.key == "SHORTLISTED")
    assert shortlisted.count == 2

    # 2 applications applied (app1 INTERVIEW, app2 APPLIED)
    applied = next(s for s in funnel.stages if s.key == "APPLIED")
    assert applied.count == 2

    # 1 interview (app1 has INTERVIEW status and interview event)
    interview = next(s for s in funnel.stages if s.key == "INTERVIEW")
    assert interview.count == 1

    # Verify summary rates
    assert funnel.summary_rates.match_to_application_rate == 1.0  # 2 applied / 2 shortlisted
    assert funnel.summary_rates.application_to_interview_rate == 0.5  # 1 interview / 2 applied


@pytest.mark.asyncio
async def test_breakdowns_calculation(db_session: AsyncSession):
    await seed_analytics_data(db_session)
    engine = BreakdownEngine(db_session)
    breakdowns = await engine.get_breakdowns()

    # Sources
    source_names = [s.source for s in breakdowns.sources]
    assert "greenhouse" in source_names
    gh = next(s for s in breakdowns.sources if s.source == "greenhouse")
    assert gh.jobs_count == 1
    assert gh.applied_count == 1
    assert gh.interviews_count == 1
    assert gh.interview_rate == 100.0

    # Variants
    var_names = [v.variant_name for v in breakdowns.variants]
    assert "java-react-fullstack" in var_names
    assert "java-backend" in var_names
    v1 = next(v for v in breakdowns.variants if v.variant_name == "java-react-fullstack")
    assert v1.applications_count == 1
    assert v1.interviews_count == 1
    assert v1.conversion_rate == 100.0

    # Locations
    loc_names = [l.location for l in breakdowns.locations]
    assert any("Mumbai" in l for l in loc_names)

    # Companies
    comp_names = [c.company for c in breakdowns.companies]
    assert "Swiggy" in comp_names
    swiggy = next(c for c in breakdowns.companies if c.company == "Swiggy")
    assert swiggy.total_jobs == 1
    assert swiggy.applied_count == 1
    assert swiggy.highest_stage == "INTERVIEW"


@pytest.mark.asyncio
async def test_timeline_trends(db_session: AsyncSession):
    await seed_analytics_data(db_session)
    engine = TimelineEngine(db_session)
    timeline = await engine.get_timeline(days=7)

    assert timeline.period_days == 7
    assert len(timeline.points) == 8  # 7 days + today
    today_point = timeline.points[-1]
    assert today_point.discovered >= 3
    assert today_point.applied >= 2


@pytest.mark.asyncio
async def test_llm_cost_tracker(db_session: AsyncSession):
    await seed_analytics_data(db_session)
    tracker = LLMCostTracker(db_session)
    usage = await tracker.get_usage_metrics()

    assert usage.total_requests == 2
    assert usage.total_input_tokens == 1700
    assert usage.total_output_tokens == 950
    assert "groq" in usage.by_provider
    assert "gemini" in usage.by_provider
    assert usage.by_provider["groq"]["requests"] == 1
    assert usage.by_provider["gemini"]["requests"] == 1
    assert "classify" in usage.by_operation
    assert "generate_resume" in usage.by_operation


@pytest.mark.asyncio
async def test_learning_loop_insights(db_session: AsyncSession):
    await seed_analytics_data(db_session)
    advisor = LearningLoopAdvisor(db_session)
    resp = await advisor.generate_insights()

    assert resp.candidate_facts_preserved is True
    assert len(resp.insights) >= 2
    # Verify top variant identified
    assert resp.top_variant == "java-react-fullstack"
    assert resp.top_source == "greenhouse"

    types = [i.type for i in resp.insights]
    assert "variant_preference" in types
    assert "source_priority" in types


@pytest.mark.asyncio
async def test_api_analytics_endpoints_authorized(client, auth_headers, db_session):
    await seed_analytics_data(db_session)

    # 1. Summary
    res = await client.get("/api/analytics/summary", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_jobs"] == 3
    assert data["applications_submitted"] == 2
    assert data["interview_count"] == 1
    assert "Swiggy" in data["top_companies"]

    # 2. Funnel
    res = await client.get("/api/analytics/funnel", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["stages"]) == 6
    assert "summary_rates" in data

    # 3. Breakdowns
    res = await client.get("/api/analytics/breakdowns", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "sources" in data
    assert "variants" in data
    assert "locations" in data
    assert "companies" in data

    # 4. Timeline
    res = await client.get("/api/analytics/timeline?days=14", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["points"]) == 15

    # 5. LLM Usage
    res = await client.get("/api/analytics/llm-usage", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_requests"] == 2

    # 6. Insights
    res = await client.get("/api/analytics/insights", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["candidate_facts_preserved"] is True
    assert len(data["insights"]) > 0


@pytest.mark.asyncio
async def test_api_analytics_unauthorized(client):
    endpoints = [
        "/api/analytics/summary",
        "/api/analytics/funnel",
        "/api/analytics/breakdowns",
        "/api/analytics/timeline",
        "/api/analytics/llm-usage",
        "/api/analytics/insights",
    ]
    for ep in endpoints:
        res = await client.get(ep)
        assert res.status_code == 401

