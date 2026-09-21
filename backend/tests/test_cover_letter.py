import os
from pathlib import Path
import pytest
from sqlalchemy import select

from app.models.job import Job
from app.models.application import Application
from app.services.cover_letter.generator import get_cover_letter_generator
from app.services.cover_letter.exporter import CoverLetterExporter
from app.services.candidate.evidence_engine import get_evidence_engine


def test_deterministic_cover_letter_templates():
    gen = get_cover_letter_generator()
    tones = ["technical", "executive", "startup"]

    for tone in tones:
        cl = gen.build_template_cover_letter(
            company="Swiggy",
            title="Senior Java Developer",
            keywords=["Java", "Spring Boot", "Kafka", "Microservices"],
            tone=tone,
        )

        # 1. Candidate facts assertions
        assert "~3.2 years" in cl, f"Tenure inaccurate in tone {tone}"
        assert "Accenture" in cl
        assert "TCS Digital" in cl
        assert "TradeX" in cl
        assert "30-day notice period" in cl
        assert "Swiggy" in cl

        # 2. Banned phrases assertions (no AI fluff)
        assert "thrilled to apply" not in cl.lower()
        assert "in today's fast-paced digital world" not in cl.lower()
        assert "my proven track record speaks for itself" not in cl.lower()


def test_cover_letter_anti_hallucination_validation():
    gen = get_cover_letter_generator()
    engine = get_evidence_engine()

    cl = gen.build_template_cover_letter(
        company="Razorpay",
        title="Full Stack Engineer",
        keywords=["Java", "React", "PostgreSQL"],
        tone="technical",
    )

    report = engine.validate_resume_content(cl)
    assert report.passed is True
    assert report.confidence_score >= 0.85
    assert len(report.hallucinated_skills) == 0
    assert "Java" in report.verified_skills
    assert "React" in report.verified_skills

    # Injecting invalid / unverified tech must fail
    bad_cl = cl + "\n\nI also have 8 years of experience building decentralized smart contracts with Solidity and Flutter."
    bad_report = engine.validate_resume_content(bad_cl)
    assert bad_report.passed is False
    assert len(bad_report.hallucinated_skills) >= 1
    assert any("solidity" in s.lower() or "flutter" in s.lower() for s in bad_report.hallucinated_skills)


def test_cover_letter_exporters():
    out_dir = Path("documents/generated/test")
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = str((out_dir / "test_cl.pdf").absolute())
    md_path = str((out_dir / "test_cl.md").absolute())

    content = (
        "I am writing to apply for the Backend Engineer position at PhonePe.\n\n"
        "At Accenture and TCS Digital, I engineered scalable microservices serving 10,000+ concurrent users.\n\n"
        "With TradeX, I architected event-driven streaming with Apache Kafka and Redis caching."
    )

    # Markdown Export
    saved_md = CoverLetterExporter.export_markdown(content, md_path)
    assert os.path.exists(saved_md)
    assert Path(saved_md).read_text(encoding="utf-8") == content

    # PDF Export
    saved_pdf = CoverLetterExporter.export_pdf(
        content=content,
        output_path=pdf_path,
        candidate_name="Shubham Prakash",
        company="PhonePe",
        title="Backend Engineer",
    )
    assert os.path.exists(saved_pdf)
    assert os.path.getsize(saved_pdf) > 500
    with open(saved_pdf, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-", f"Expected valid PDF header, got {header}"


@pytest.mark.asyncio
async def test_api_cover_letter_lifecycle(client, auth_headers, db_session):
    # 1. Create a test job
    job = Job(
        source="indeed",
        title="Backend Software Engineer",
        company="Zepto",
        description="Looking for Java, Spring Boot, Kafka, and Redis developers in Mumbai.",
        locations='["Mumbai"]',
        experience_min=3.0,
        status="active",
        required_skills='["Java", "Spring Boot", "Kafka", "Redis"]',
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # 2. POST /api/jobs/{job.id}/cover-letter (Generate)
    gen_resp = await client.post(
        f"/api/jobs/{job.id}/cover-letter",
        json={"tone": "technical"},
        headers=auth_headers,
    )
    assert gen_resp.status_code == 200
    data = gen_resp.json()
    assert data["job_id"] == job.id
    assert data["company"] == "Zepto"
    assert data["title"] == "Backend Software Engineer"
    assert data["validation_passed"] is True
    assert data["confidence_score"] >= 0.85
    assert "~3.2 years" in data["content_markdown"]
    assert "TradeX" in data["content_markdown"]
    assert data["file_path_pdf"] is not None

    # Verify Application was created or updated in DB
    app_res = await db_session.execute(select(Application).where(Application.job_id == job.id))
    app = app_res.scalar_one_or_none()
    assert app is not None
    assert app.cover_letter is not None

    # 3. GET /api/jobs/{job.id}/cover-letter (Fetch)
    get_resp = await client.get(
        f"/api/jobs/{job.id}/cover-letter",
        headers=auth_headers,
    )
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["job_id"] == job.id
    assert get_data["content_markdown"] == data["content_markdown"]

    # 4. PUT /api/jobs/{job.id}/cover-letter (Edit/Customize)
    updated_text = data["content_markdown"] + "\n\nAdditionally, I actively follow Zepto's engineering blog regarding 10-minute delivery dispatch systems."
    put_resp = await client.put(
        f"/api/jobs/{job.id}/cover-letter",
        json={"content_markdown": updated_text},
        headers=auth_headers,
    )
    assert put_resp.status_code == 200
    put_data = put_resp.json()
    assert "10-minute delivery" in put_data["content_markdown"]
    assert put_data["generator_source"] == "user_edited"

    # 5. GET /api/jobs/{job.id}/cover-letter/download/pdf
    pdf_resp = await client.get(
        f"/api/jobs/{job.id}/cover-letter/download/pdf",
        headers=auth_headers,
    )
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF-")

    # 6. GET /api/jobs/{job.id}/cover-letter/download/md
    md_resp = await client.get(
        f"/api/jobs/{job.id}/cover-letter/download/md",
        headers=auth_headers,
    )
    assert md_resp.status_code == 200
    assert "text/markdown" in md_resp.headers["content-type"]
    assert "10-minute delivery" in md_resp.text
