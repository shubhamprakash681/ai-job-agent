import os
from pathlib import Path
import pytest
from sqlalchemy import select

from app.models.job import Job
from app.models.resume import ResumeVersion
from app.services.resume.builder import get_master_resume_builder
from app.services.resume.exporters import ResumeExporters
from app.services.resume.tailor import get_resume_tailor


def test_master_resume_builder():
    builder = get_master_resume_builder()

    # Build primary variant
    resume = builder.build_resume_data("java-react-fullstack")
    assert resume.candidate_name == "Shubham Prakash"
    assert resume.variant_id == "java-react-fullstack"
    assert len(resume.experiences) >= 2
    assert any("Accenture" in exp.company for exp in resume.experiences)
    assert any("TCS" in exp.company for exp in resume.experiences)
    assert len(resume.projects) >= 1
    assert any("TradeX" in proj.name for proj in resume.projects)

    # Every bullet must have fact_id (evidence link)
    for exp in resume.experiences:
        for b in exp.bullets:
            assert b.fact_id, f"Missing fact_id in bullet: {b.text}"
    for proj in resume.projects:
        for b in proj.bullets:
            assert b.fact_id, f"Missing fact_id in project bullet: {b.text}"

    # Render markdown
    md = builder.render_markdown(resume)
    assert "# Shubham Prakash" in md
    assert "Accenture" in md
    assert "Tata Consultancy Services" in md or "TCS" in md
    assert "TradeX" in md
    assert "Cochin University of Science and Technology" in md


def test_all_variants_build_successfully():
    builder = get_master_resume_builder()
    variants = ["java-react-fullstack", "java-backend", "backend-distributed", "fullstack-engineer"]

    for v_id in variants:
        resume = builder.build_resume_data(v_id)
        assert resume.variant_id == v_id
        md = builder.render_markdown(resume)
        assert len(md) > 500
        assert "Shubham Prakash" in md


def test_resume_exporters(tmp_path):
    builder = get_master_resume_builder()
    resume = builder.build_resume_data("java-react-fullstack")

    # 1. Export Markdown
    md_file = str(tmp_path / "test_resume.md")
    md_path = ResumeExporters.export_markdown(resume, md_file)
    assert os.path.exists(md_path)
    assert Path(md_path).stat().st_size > 500

    # 2. Export ATS PDF
    pdf_file = str(tmp_path / "test_resume.pdf")
    pdf_path = ResumeExporters.export_pdf(resume, pdf_file)
    assert os.path.exists(pdf_path)
    assert Path(pdf_path).stat().st_size > 1000
    with open(pdf_path, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-"

    # 3. Export Word DOCX
    docx_file = str(tmp_path / "test_resume.docx")
    docx_path = ResumeExporters.export_docx(resume, docx_file)
    assert os.path.exists(docx_path)
    assert Path(docx_path).stat().st_size > 1000


@pytest.mark.asyncio
async def test_resume_tailor_pipeline(db_session, tmp_path):
    job = Job(
        source="greenhouse",
        title="Full Stack Java & React Engineer",
        company="Razorpay",
        description="We are looking for a Software Engineer with Java, Spring Boot, React, Kafka, Redis, and PostgreSQL.",
        locations='["Bengaluru"]',
        experience_min=3.0,
        experience_max=5.0,
        status="active",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    tailor = get_resume_tailor()
    version = await tailor.tailor_for_job(job=job, variant_id="java-react-fullstack", db=db_session)

    assert version.job_id == job.id
    assert version.validation_status == "passed"
    assert version.confidence_score == 1.0
    assert version.file_path_pdf is not None
    assert os.path.exists(version.file_path_pdf)
    assert version.file_path_docx is not None
    assert os.path.exists(version.file_path_docx)
    assert "Shubham Prakash" in version.content_markdown
    assert "Razorpay" in (version.change_diff or "")


@pytest.mark.asyncio
async def test_api_tailor_and_download(client, auth_headers, db_session):
    # 1. Test variants list
    v_resp = await client.get("/api/resumes/variants", headers=auth_headers)
    assert v_resp.status_code == 200
    variants = v_resp.json()
    assert len(variants) >= 4
    variant_names = [v["name"] for v in variants]
    assert "java-react-fullstack" in variant_names
    assert "java-backend" in variant_names

    # 2. Ingest a job
    job = Job(
        source="manual",
        title="Senior Spring Boot Developer",
        company="Swiggy",
        description="Design microservices using Java 17, Spring Boot, Kafka, and Redis caching.",
        locations='["Mumbai"]',
        experience_min=3.0,
        status="active",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # 3. Trigger tailor endpoint
    tailor_resp = await client.post(f"/api/jobs/{job.id}/tailor-resume", headers=auth_headers)
    assert tailor_resp.status_code == 200
    version_data = tailor_resp.json()
    assert version_data["job_id"] == job.id
    assert version_data["validation_status"] == "passed"
    assert version_data["confidence_score"] == 1.0
    version_id = version_data["id"]

    # 4. List versions endpoint
    list_resp = await client.get("/api/resumes/versions", headers=auth_headers)
    assert list_resp.status_code == 200
    versions_list = list_resp.json()
    assert versions_list["total"] >= 1
    assert any(v["id"] == version_id for v in versions_list["items"])

    # 5. Get single version details
    detail_resp = await client.get(f"/api/resumes/versions/{version_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["job_title"] == "Senior Spring Boot Developer"

    # 6. Download PDF
    pdf_resp = await client.get(f"/api/resumes/versions/{version_id}/download/pdf", headers=auth_headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 1000

    # 7. Download DOCX
    docx_resp = await client.get(f"/api/resumes/versions/{version_id}/download/docx", headers=auth_headers)
    assert docx_resp.status_code == 200
    assert "wordprocessingml" in docx_resp.headers["content-type"]
    assert len(docx_resp.content) > 1000

    # 8. Download Markdown
    md_resp = await client.get(f"/api/resumes/versions/{version_id}/download/md", headers=auth_headers)
    assert md_resp.status_code == 200
    assert "text/markdown" in md_resp.headers["content-type"]
    assert "Shubham Prakash" in md_resp.text
