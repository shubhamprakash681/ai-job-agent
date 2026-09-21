import json
import pytest
from sqlalchemy import select

from app.models.audit import AuditLog
from app.models.job import Job, JobScore
from app.models.llm import LLMRequest
from app.services.llm.client import (
    UnifiedLLMClient,
    extract_json_from_llm_output,
)
from app.services.processing.classifier import get_job_classifier
from app.services.processing.prefilter import run_prefilters
from app.services.processing.processor import get_job_processor


def test_extract_json_from_llm_output():
    # Plain JSON
    assert extract_json_from_llm_output('{"key": "val"}') == {"key": "val"}
    # Code fenced
    assert extract_json_from_llm_output('```json\n{"key": "val"}\n```') == {"key": "val"}
    # Preceding/trailing conversational text
    raw = 'Here is your classification:\n{"role_category": "JAVA_BACKEND", "fit_score": 85}\nHope this helps!'
    parsed = extract_json_from_llm_output(raw)
    assert parsed is not None
    assert parsed["role_category"] == "JAVA_BACKEND"
    assert parsed["fit_score"] == 85


def test_prefilter_scam_and_fraud():
    job = Job(
        source="manual",
        title="Software Engineer",
        fraud_risk="high",
        status="active",
    )
    result = run_prefilters(job)
    assert not result.passed
    assert "High fraud risk" in result.rejection_reason


def test_prefilter_excluded_keywords():
    job = Job(
        source="manual",
        title="Senior PHP Developer",
        fraud_risk="none",
        status="active",
    )
    result = run_prefilters(job)
    assert not result.passed
    assert "Role domain does not align" in result.rejection_reason

    job2 = Job(
        source="manual",
        title="Content Writer",
        fraud_risk="none",
        status="active",
    )
    result2 = run_prefilters(job2)
    assert not result2.passed


def test_prefilter_experience_ceiling():
    # Shubham has ~3.2 years, 8+ years must be rejected
    job = Job(
        source="manual",
        title="Lead Java Architect",
        experience_min=8.0,
        experience_max=12.0,
        status="active",
    )
    result = run_prefilters(job)
    assert not result.passed
    assert "exceeds candidate's ~3.2 yrs" in result.rejection_reason

    # 3-5 years passes
    job_ok = Job(
        source="manual",
        title="Java Developer",
        experience_min=3.0,
        experience_max=5.0,
        status="active",
    )
    result_ok = run_prefilters(job_ok)
    assert result_ok.passed


@pytest.mark.asyncio
async def test_classifier_rule_fallbacks():
    classifier = get_job_classifier()

    # 1. Unrelated stack
    job_unrelated = Job(
        source="manual",
        title="Ruby on Rails Developer",
        description="Must have 3 years of Ruby on Rails and PostgreSQL.",
        locations='["Mumbai"]',
    )
    res_unrelated = await classifier.classify(job_unrelated)
    assert res_unrelated.role_category == "UNRELATED"
    assert res_unrelated.fit_category == "REJECT"

    # 2. Java React Full Stack
    job_fullstack = Job(
        source="manual",
        title="Full Stack Java & React Developer",
        description="We need an engineer experienced with Java Spring Boot backend and React web UI.",
        locations='["Mumbai"]',
    )
    res_fullstack = await classifier.classify(job_fullstack)
    assert res_fullstack.role_category == "JAVA_REACT_FULLSTACK"
    assert res_fullstack.fit_category == "HIGH_FIT"
    assert res_fullstack.recommended_variant == "java-react-fullstack"

    # 3. Distributed Systems / Kafka
    job_dist = Job(
        source="manual",
        title="Backend Distributed Systems Engineer",
        description="High-scale trading platform using Kafka event streams, Redis caching, and Java microservices.",
        locations='["Bengaluru"]',
    )
    res_dist = await classifier.classify(job_dist)
    assert res_dist.role_category == "DISTRIBUTED_SYSTEMS"
    assert res_dist.fit_category == "HIGH_FIT"
    assert res_dist.recommended_variant == "backend-distributed"


@pytest.mark.asyncio
async def test_processor_pipeline_and_audit(db_session):
    processor = get_job_processor()

    # Create job that passes prefilters
    job = Job(
        source="greenhouse",
        title="Senior Java Developer",
        company="Paytm",
        description="Core Java, Spring Boot, Microservices, and REST API development.",
        locations='["Mumbai"]',
        experience_min=3.0,
        experience_max=5.0,
        status="active",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    job_processed, score, summary = await processor.process_job(job.id, db_session)

    assert job_processed.id == job.id
    assert score is not None
    assert score.fit_category in ["AUTO_PREPARE", "HIGH_PRIORITY", "GOOD", "HIGH_FIT", "MODERATE_FIT"]
    assert score.total_score > 50
    assert summary["status"] == "classified"

    # Verify LLM request logged
    llm_logs = (await db_session.execute(select(LLMRequest).where(LLMRequest.job_id == job.id))).scalars().all()
    assert len(llm_logs) >= 1
    assert llm_logs[0].status == "success"

    # Verify Audit log created
    audit_logs = (await db_session.execute(select(AuditLog).where(AuditLog.entity_id == job.id))).scalars().all()
    assert len(audit_logs) >= 1
    assert audit_logs[0].action == "JOB_CLASSIFIED"


@pytest.mark.asyncio
async def test_processor_prefilter_rejection(db_session):
    processor = get_job_processor()

    # Create job requiring 10+ years
    job = Job(
        source="indeed",
        title="Principal Software Architect",
        company="Enterprise Corp",
        description="Must have 10+ years leading enterprise architecture.",
        experience_min=10.0,
        status="active",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    job_processed, score, summary = await processor.process_job(job.id, db_session)

    assert job_processed.status == "rejected_prefilter"
    assert score.fit_category == "REJECT"
    assert score.total_score == 0
    assert not summary["passed_prefilter"]


@pytest.mark.asyncio
async def test_api_classify_endpoint(client, auth_headers, db_session):
    job = Job(
        source="manual",
        title="Software Engineer - Java/Spring",
        company="Fintech Co",
        description="Build microservices using Java and Spring Boot.",
        status="active",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    resp = await client.post(f"/api/jobs/{job.id}/classify", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["job"]["id"] == job.id
    assert data["score"]["fit_category"] in ["AUTO_PREPARE", "HIGH_PRIORITY", "GOOD", "HIGH_FIT", "MODERATE_FIT"]
    assert "processing_summary" in data

    # Verify GET /jobs now includes score
    list_resp = await client.get("/api/jobs", headers=auth_headers)
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    matched = next((j for j in items if j["id"] == job.id), None)
    assert matched is not None
    assert matched["score"] is not None
    assert matched["score"]["fit_category"] == data["score"]["fit_category"]


@pytest.mark.asyncio
async def test_api_process_pending_endpoint(client, auth_headers, db_session):
    # Seed 2 pending active jobs
    j1 = Job(source="manual", title="Java Dev 1", description="Java, Spring", status="active")
    j2 = Job(source="manual", title="PHP Dev 2", description="PHP, WordPress", status="active")
    db_session.add_all([j1, j2])
    await db_session.commit()

    resp = await client.post("/api/jobs/process-pending?limit=10", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_processed"] >= 2
    assert data["passed"] >= 1
    assert data["rejected"] >= 1

