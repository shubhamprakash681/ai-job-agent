import json
import pytest
from sqlalchemy import select

from app.models.job import Job, JobScore
from app.services.scoring.rubric import (
    score_core_skills,
    score_distributed_systems,
    score_experience,
    score_job_quality,
    score_location,
    score_role_relevance,
)
from app.services.scoring.scorer import get_job_scorer


def test_rubric_role_relevance():
    # Java + React
    assert score_role_relevance("Full Stack Java Developer", "Spring Boot and React experience required.") == 25
    # Distributed Systems
    assert score_role_relevance("Backend Distributed Systems Engineer", "Java microservices with Kafka streaming.") == 24
    # Java Backend
    assert score_role_relevance("Senior Java Engineer", "Spring Boot REST APIs.") == 22
    # Unrelated
    assert score_role_relevance("iOS Swift Developer", "Build mobile apps in Swift.") == 0


def test_rubric_core_skills():
    text = "We are seeking a developer with deep Java, Spring Boot, microservices architecture, React, and PostgreSQL expertise."
    score, matched, missing = score_core_skills(["Java", "React"], text)
    assert score == 25
    assert "Java" in matched
    assert "Spring Boot" in matched
    assert "React" in matched
    assert "REST / Microservices" in matched
    assert "SQL / PostgreSQL" in matched
    assert len(missing) == 0


def test_rubric_distributed_systems():
    text = "High throughput order processing with Kafka event streams, Redis cache, and WebSockets."
    score, matched = score_distributed_systems([], text)
    assert score >= 10
    assert "Kafka" in matched
    assert "Redis" in matched
    assert "WebSockets / Real-Time" in matched


def test_rubric_experience_fit():
    # 3.0 yrs (candidate has ~3.2 yrs)
    score_ideal, risks_ideal = score_experience(3.0, 5.0, "Java Developer")
    assert score_ideal == 15
    assert len(risks_ideal) == 0

    # 4.5 yrs (stretch)
    score_stretch, risks_stretch = score_experience(4.5, 6.0, "Senior Java Developer")
    assert score_stretch == 8
    assert len(risks_stretch) > 0

    # Principal Architect title penalty
    score_exec, risks_exec = score_experience(3.0, 5.0, "Principal Software Architect")
    assert score_exec == 0
    assert len(risks_exec) > 0


def test_rubric_location():
    # Mumbai
    score_mum, _ = score_location(["Mumbai"], remote=False)
    assert score_mum == 10

    # Remote
    score_rem, _ = score_location([], remote=True)
    assert score_rem == 10

    # Bengaluru
    score_blr, _ = score_location(["Bengaluru"], remote=False)
    assert score_blr == 10

    # Secondary location
    score_sec, warnings = score_location(["Ahmedabad"], remote=False)
    assert score_sec == 6
    assert len(warnings) > 0


def test_rubric_job_quality():
    score, strengths = score_job_quality(
        source="greenhouse",
        salary_min=2000000,
        description="A" * 500,
        posted_at=None,
    )
    assert score >= 7
    assert any("Direct ATS" in s for s in strengths)
    assert any("Transparent salary" in s for s in strengths)


def test_job_scorer_aggregation():
    scorer = get_job_scorer()

    job_perfect = Job(
        source="greenhouse",
        title="Full Stack Java & React Engineer",
        description="Core Java, Spring Boot, React, Kafka, PostgreSQL, microservices. Build high-scale web apps.",
        locations='["Mumbai"]',
        remote=True,
        experience_min=3.0,
        experience_max=5.0,
        salary_min=2500000,
        salary_max=3500000,
        skills='["Java", "React", "Spring Boot", "Kafka", "PostgreSQL"]',
    )
    breakdown = scorer.score_job(job_perfect)

    assert breakdown.total_score >= 85
    assert breakdown.fit_category == "AUTO_PREPARE"
    assert breakdown.recommended_variant == "java-react-fullstack"
    assert breakdown.role_relevance == 25
    assert breakdown.core_skills == 25
    assert breakdown.experience_fit == 15
    assert breakdown.location_score == 10
    assert len(breakdown.strengths) >= 4


@pytest.mark.asyncio
async def test_api_analyze_job_endpoint(client, auth_headers, db_session):
    job = Job(
        source="greenhouse",
        title="Java Microservices Developer",
        company="Fintech Corp",
        description="Java 17, Spring Boot, Kafka streaming, Redis caching, PostgreSQL.",
        locations='["Bengaluru"]',
        experience_min=3.0,
        experience_max=4.0,
        salary_min=2200000,
        status="active",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    resp = await client.post(f"/api/jobs/{job.id}/analyze", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["job_id"] == job.id
    assert data["total_score"] >= 70
    assert data["role_relevance"] > 0
    assert data["core_skills"] > 0
    assert data["distributed_systems"] > 0
    assert data["fit_category"] in ["AUTO_PREPARE", "HIGH_PRIORITY"]
    assert data["recommended_variant"] in ["backend-distributed", "java-backend"]

    # Verify score saved in DB
    score_in_db = (await db_session.execute(select(JobScore).where(JobScore.job_id == job.id))).scalar_one()
    assert score_in_db.total_score == data["total_score"]


@pytest.mark.asyncio
async def test_api_min_score_filter(client, auth_headers, db_session):
    # Job 1 with high score
    j1 = Job(source="manual", title="Java Spring Dev", status="active")
    db_session.add(j1)
    await db_session.commit()
    await db_session.refresh(j1)

    s1 = JobScore(
        job_id=j1.id,
        total_score=92,
        fit_category="AUTO_PREPARE",
        recommended_variant="java-backend",
    )

    # Job 2 with low score
    j2 = Job(source="manual", title="PHP Dev", status="active")
    db_session.add(j2)
    await db_session.commit()
    await db_session.refresh(j2)

    s2 = JobScore(
        job_id=j2.id,
        total_score=25,
        fit_category="IGNORE",
        recommended_variant="java-backend",
    )
    db_session.add_all([s1, s2])
    await db_session.commit()

    # Query with min_score=80
    resp = await client.get("/api/jobs?min_score=80", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == j1.id
    assert items[0]["score"]["total_score"] == 92

