import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.services.ingestion.base import RawJobData
from app.services.ingestion.dedup import check_duplicate, compute_content_hash
from app.services.ingestion.normalizer import (
    clean_job_title,
    normalize_job_data,
    parse_experience,
    parse_locations,
    parse_salary,
)
from app.services.ingestion.pipeline import get_ingestion_pipeline


def test_clean_job_title():
    raw = "🔥 Urgent Hiring!! Senior Java Developer / Immediate Joiner ***"
    cleaned = clean_job_title(raw)
    assert "Senior Java Developer" in cleaned
    assert "🔥" not in cleaned
    assert "Urgent" not in cleaned
    assert "Immediate Joiner" not in cleaned


def test_parse_locations():
    # Mumbai
    cities, is_remote = parse_locations("Mumbai, Maharashtra, India")
    assert "Mumbai" in cities
    assert is_remote is False

    # Bangalore / Bengaluru
    cities, is_remote = parse_locations("Bangalore / Bengaluru")
    assert "Bengaluru" in cities

    # Remote
    cities, is_remote = parse_locations("Work from home", text_for_remote_check="100% remote job")
    assert is_remote is True
    assert "Remote" in cities


def test_parse_experience():
    # Range
    e_min, e_max = parse_experience("3 - 5 yrs")
    assert e_min == 3.0
    assert e_max == 5.0

    # Min only
    e_min, e_max = parse_experience("3+ years of software experience")
    assert e_min == 3.0
    assert e_max == 6.0


def test_parse_salary():
    # INR LPA
    s_min, s_max, curr = parse_salary("15 - 25 LPA")
    assert s_min == 1500000
    assert s_max == 2500000
    assert curr == "INR"

    # USD
    s_min, s_max, curr = parse_salary("$120k - $160k")
    assert s_min == 120000
    assert s_max == 160000
    assert curr == "USD"


def test_normalize_job_data():
    raw = RawJobData(
        source="naukri",
        source_job_id="naukri-12345",
        url="https://example.com/job/123",
        title="🔥 Senior Java Spring Boot Developer",
        company="TechCorp India",
        raw_location="Mumbai, Maharashtra",
        raw_salary="18 - 24 LPA",
        raw_experience="3 - 6 yrs",
        description="We are seeking an experienced Java engineer proficient in Spring Boot, Kafka, and Redis.",
        skill_tags=["Java", "Spring Boot", "Kafka"],
    )

    canonical = normalize_job_data(raw)
    assert canonical["company"] == "TechCorp India"
    assert "Senior Java Spring Boot Developer" in canonical["title"]
    assert canonical["salary_min"] == 1800000
    assert canonical["salary_max"] == 2400000
    assert canonical["experience_min"] == 3.0
    assert canonical["experience_max"] == 6.0
    assert "Java" in canonical["skills"]
    assert "Kafka" in canonical["skills"]
    assert canonical["fraud_risk"] == "none"
    assert len(canonical["raw_content_hash"]) == 64


@pytest.mark.asyncio
async def test_deduplication_exact_url(db_session: AsyncSession):
    pipeline = get_ingestion_pipeline()
    job1, is_new1, _ = await pipeline.ingest_manual_job(
        db=db_session,
        title="Java Engineer",
        company="Razorpay",
        url="https://jobs.razorpay.com/101",
        location="Mumbai",
    )
    assert is_new1 is True

    # Same URL should be detected as duplicate
    job2, is_new2, reason = await pipeline.ingest_manual_job(
        db=db_session,
        title="Java Engineer",
        company="Razorpay",
        url="https://jobs.razorpay.com/101",
        location="Mumbai",
    )
    assert is_new2 is False
    assert "Exact URL" in reason
    assert job2.id == job1.id


@pytest.mark.asyncio
async def test_deduplication_content_hash(db_session: AsyncSession):
    pipeline = get_ingestion_pipeline()
    job1, is_new1, _ = await pipeline.ingest_manual_job(
        db=db_session,
        title="Backend Developer (Spring Boot)",
        company="Swiggy",
        location="Bengaluru",
        description="Spring Boot microservices engineer",
    )
    assert is_new1 is True

    # Same company, title, location (different or empty URL)
    job2, is_new2, reason = await pipeline.ingest_manual_job(
        db=db_session,
        title="Backend Developer (Spring Boot)",
        company="Swiggy",
        location="Bengaluru",
        description="Duplicate posting",
    )
    assert is_new2 is False
    assert "content hash" in reason.lower()
    assert job2.id == job1.id


@pytest.mark.asyncio
async def test_api_jobs_manual_endpoint(client: AsyncClient, auth_headers: dict):
    payload = {
        "title": "Full Stack Java Developer",
        "company": "Accenture Test",
        "location": "Mumbai",
        "salary": "16 - 22 LPA",
        "experience": "3 - 5 yrs",
        "description": "Looking for a Full Stack engineer with Java, Spring Boot, and React experience.",
        "url": "https://careers.accenture.com/sample-job-99",
    }
    res = await client.post("/api/jobs/manual", headers=auth_headers, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_new"] is True
    assert data["job"]["title"] == "Full Stack Java Developer"
    assert data["job"]["company"] == "Accenture Test"
    assert data["job"]["salary_min"] == 1600000


@pytest.mark.asyncio
async def test_api_jobs_sources_endpoint(client: AsyncClient, auth_headers: dict):
    res = await client.get("/api/jobs/sources", headers=auth_headers)
    assert res.status_code == 200
    sources = res.json()
    source_names = [s["source"] for s in sources]
    assert "manual" in source_names
    assert "greenhouse" in source_names
    assert "lever" in source_names
    assert "indeed" in source_names
    assert "naukri" in source_names

