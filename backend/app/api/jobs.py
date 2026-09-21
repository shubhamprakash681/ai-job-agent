from typing import Any
import re
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.job import Job, JobScore
from app.models.user import User
from app.schemas.job import (
    JobClassifyResponse,
    JobFetchRequest,
    JobFetchResponse,
    JobListResponse,
    JobProcessPendingResponse,
    JobResponse,
    JobScoreResponse,
    JobSourceResponse,
    ManualJobCreate,
    ManualJobResponse,
)
from app.schemas.resume import ResumeVersionResponse
from app.services.ingestion.base import JobSearchQuery
from app.services.ingestion.pipeline import get_ingestion_pipeline
from app.services.processing.processor import get_job_processor
from fastapi.responses import FileResponse
from app.models.application import Application
from app.models.candidate import CandidateProfile
from app.schemas.cover_letter import (
    CoverLetterResponse,
    CoverLetterGenerateRequest,
    CoverLetterUpdateRequest,
)
from app.services.candidate.evidence_engine import get_evidence_engine
from app.services.cover_letter import (
    get_cover_letter_generator,
    CoverLetterExporter,
)
from app.services.resume.tailor import get_resume_tailor
from app.services.scoring.scorer import get_job_scorer

router = APIRouter()


@router.get("", response_model=JobListResponse)
@router.get("/", response_model=JobListResponse, include_in_schema=False)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    source: str | None = None,
    status: str | None = "active",
    min_score: int | None = Query(None, ge=0, le=100),
    search: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    """List jobs with pagination and optional source, status, and keyword filters."""
    query = select(Job)
    count_query = select(func.count(Job.id))

    if min_score is not None:
        query = query.join(JobScore, Job.id == JobScore.job_id).where(JobScore.total_score >= min_score)
        count_query = count_query.join(JobScore, Job.id == JobScore.job_id).where(JobScore.total_score >= min_score)

    if source:
        query = query.where(Job.source == source)
        count_query = count_query.where(Job.source == source)
    if status and status != "all":
        query = query.where(Job.status == status)
        count_query = count_query.where(Job.status == status)
    if search:
        search_filter = or_(
            Job.title.ilike(f"%{search}%"),
            Job.company.ilike(f"%{search}%"),
            Job.description.ilike(f"%{search}%"),
            Job.skills.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total = await db.scalar(count_query) or 0
    offset = (page - 1) * per_page
    query = query.order_by(Job.id.desc()).offset(offset).limit(per_page)

    result = await db.execute(query)
    jobs = result.scalars().all()
    job_ids = [j.id for j in jobs]

    scores_by_job: dict[int, JobScoreResponse] = {}
    if job_ids:
        score_res = await db.execute(select(JobScore).where(JobScore.job_id.in_(job_ids)))
        for s in score_res.scalars().all():
            scores_by_job[s.job_id] = JobScoreResponse.model_validate(s)

    items: list[JobResponse] = []
    for j in jobs:
        resp = JobResponse.model_validate(j)
        resp.score = scores_by_job.get(j.id)
        items.append(resp)

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("/manual", response_model=ManualJobResponse)
async def create_manual_job(
    job_in: ManualJobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ManualJobResponse:
    """
    Manually ingest a job opportunity by entering its details or pasting its description.
    Enforces normalization and multi-level deduplication.
    """
    pipeline = get_ingestion_pipeline()
    job, is_new, dup_reason = await pipeline.ingest_manual_job(
        db=db,
        title=job_in.title,
        company=job_in.company,
        description=job_in.description,
        url=job_in.url,
        location=job_in.location,
        salary=job_in.salary,
        experience=job_in.experience,
        application_url=job_in.application_url,
    )

    msg = "Job created successfully." if is_new else f"Existing job found ({dup_reason})."
    return ManualJobResponse(
        job=JobResponse.model_validate(job),
        is_new=is_new,
        message=msg,
    )


@router.post("/fetch", response_model=JobFetchResponse)
async def trigger_fetch_jobs(
    request: JobFetchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobFetchResponse:
    """
    Trigger automated job ingestion across configured source adapters.
    Deduplicates and stores new opportunities into the jobs table.
    """
    pipeline = get_ingestion_pipeline()
    search_q = JobSearchQuery(
        keyword=request.keyword,
        location=request.location,
        remote=request.remote,
        limit=request.limit,
    )
    res = await pipeline.run_ingestion(db=db, sources=request.sources, query=search_q)

    return JobFetchResponse(
        status=res["status"],
        total_fetched=res["total_fetched"],
        new_jobs_saved=res["new_jobs_saved"],
        duplicates_skipped=res["duplicates_skipped"],
        errors=res["errors"],
    )


@router.get("/sources", response_model=list[JobSourceResponse])
async def list_job_sources(
    current_user: User = Depends(get_current_user),
) -> list[JobSourceResponse]:
    """List available job sources, adapters, and their status."""
    pipeline = get_ingestion_pipeline()
    sources = pipeline.list_sources()
    return [JobSourceResponse(**s) for s in sources]


@router.post("/process-pending", response_model=JobProcessPendingResponse)
async def process_pending_jobs_endpoint(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobProcessPendingResponse:
    """
    Batch process all active opportunities that do not have a classification score yet.
    """
    processor = get_job_processor()
    res = await processor.process_pending_jobs(db, limit=limit)
    return JobProcessPendingResponse(
        total_processed=res["total_processed"],
        passed=res["passed"],
        rejected=res["rejected"],
        job_ids=res["job_ids"],
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Retrieve details for a single job."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    res = await db.execute(select(JobScore).where(JobScore.job_id == job_id))
    score = res.scalar_one_or_none()
    resp = JobResponse.model_validate(job)
    if score:
        resp.score = JobScoreResponse.model_validate(score)
    return resp


@router.get("/{job_id}/score", response_model=JobScoreResponse | None)
async def get_job_score(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobScoreResponse | None:
    """Get score breakdown for a specific job."""
    res = await db.execute(select(JobScore).where(JobScore.job_id == job_id))
    score = res.scalar_one_or_none()
    if not score:
        return None
    return JobScoreResponse.model_validate(score)


@router.post("/{job_id}/classify", response_model=JobClassifyResponse)
async def classify_job_endpoint(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobClassifyResponse:
    """
    Run prefilters and deep classification (LLM or heuristic) for a single job.
    Updates the job status, generates JobScore, and logs an audit trail.
    """
    processor = get_job_processor()
    try:
        job, score, summary = await processor.process_job(job_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to classify job: {str(e)}")

    job_resp = JobResponse.model_validate(job)
    score_resp = JobScoreResponse.model_validate(score)
    job_resp.score = score_resp

    return JobClassifyResponse(
        job=job_resp,
        score=score_resp,
        processing_summary=summary,
    )


@router.post("/{job_id}/analyze", response_model=JobScoreResponse)
async def analyze_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobScoreResponse:
    """
    Perform deep multi-dimensional match analysis for a job (Phase 5).
    Evaluates role relevance, core skills, distributed systems, experience, location, and quality.
    Updates and persists JobScore record.
    """
    import json
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    scorer = get_job_scorer()
    scoring = scorer.score_job(job)

    res = await db.execute(select(JobScore).where(JobScore.job_id == job_id))
    score = res.scalar_one_or_none()
    if not score:
        score = JobScore(
            job_id=job_id,
            total_score=scoring.total_score,
            role_relevance=scoring.role_relevance,
            core_skills=scoring.core_skills,
            distributed_systems=scoring.distributed_systems,
            experience_fit=scoring.experience_fit,
            location_score=scoring.location_score,
            job_quality=scoring.job_quality,
            fit_category=scoring.fit_category,
            recommended_variant=scoring.recommended_variant,
            strengths=json.dumps(scoring.strengths),
            gaps=json.dumps(scoring.gaps),
            risks=json.dumps(scoring.risks),
            reasoning=scoring.reasoning,
        )
        db.add(score)
    else:
        score.total_score = scoring.total_score
        score.role_relevance = scoring.role_relevance
        score.core_skills = scoring.core_skills
        score.distributed_systems = scoring.distributed_systems
        score.experience_fit = scoring.experience_fit
        score.location_score = scoring.location_score
        score.job_quality = scoring.job_quality
        score.fit_category = scoring.fit_category
        score.recommended_variant = scoring.recommended_variant
        score.strengths = json.dumps(scoring.strengths)
        score.gaps = json.dumps(scoring.gaps)
        score.risks = json.dumps(scoring.risks)
        score.reasoning = scoring.reasoning

    await db.commit()
    await db.refresh(score)
    return JobScoreResponse.model_validate(score)


@router.post("/{job_id}/tailor-resume", response_model=ResumeVersionResponse)
async def tailor_resume(
    job_id: int,
    variant_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeVersionResponse:
    """
    Trigger automated resume tailoring for a job (Phase 6).
    Reorders experience and project bullets to align with job keywords,
    links evidence IDs, validates against anti-hallucination rules, and exports PDF/DOCX.
    """
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    tailor = get_resume_tailor()
    resume_ver = await tailor.tailor_for_job(job=job, variant_id=variant_id, db=db)

    resp = ResumeVersionResponse.model_validate(resume_ver)
    resp.job_title = job.title
    resp.job_company = job.company
    return resp


@router.post("/{job_id}/cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter_endpoint(
    job_id: int,
    req: CoverLetterGenerateRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CoverLetterResponse:
    """
    Generate or regenerate an ATS-tailored, zero-hallucination cover letter for a job.
    Exports PDF and Markdown, checks against the Evidence Engine, and links to the Application.
    """
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    tone = req.tone if req else "technical"
    custom_instructions = req.custom_instructions if req else None

    generator = get_cover_letter_generator()
    res = await generator.generate_cover_letter(
        job=job,
        tone=tone,
        custom_instructions=custom_instructions,
        db=db,
    )

    # Sync with candidate profile & application record
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=current_user.full_name or "Shubham Prakash",
            email=current_user.email,
            location="Mumbai, India",
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    app_res = await db.execute(
        select(Application).where(
            Application.job_id == job_id,
            Application.candidate_id == profile.id,
        )
    )
    app = app_res.scalar_one_or_none()
    if not app:
        app = Application(
            job_id=job_id,
            candidate_id=profile.id,
            status="RESUME_READY",
            cover_letter=res.content_markdown,
        )
        db.add(app)
    else:
        app.cover_letter = res.content_markdown
    await db.commit()

    return CoverLetterResponse(
        job_id=job.id,
        company=job.company or "Company",
        title=job.title,
        content_markdown=res.content_markdown,
        tone=res.tone,
        word_count=res.word_count,
        file_path_pdf=res.file_path_pdf,
        file_path_md=res.file_path_md,
        validation_passed=res.validation_passed,
        confidence_score=res.confidence_score,
        warnings=res.warnings,
        verified_skills=res.verified_skills,
        generator_source=res.generator_source,
    )


@router.get("/{job_id}/cover-letter", response_model=CoverLetterResponse)
async def get_cover_letter_endpoint(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CoverLetterResponse:
    """
    Retrieve existing cover letter for a job, or generate a tailored default on the fly.
    """
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    md_path = Path(f"documents/generated/CoverLetter_Shubham_Prakash_Job{job.id}.md")
    pdf_path = Path(f"documents/generated/CoverLetter_Shubham_Prakash_Job{job.id}.pdf")
    content = ""

    if md_path.exists():
        content = md_path.read_text(encoding="utf-8")
    else:
        prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
        profile = prof_res.scalar_one_or_none()
        if profile:
            app_res = await db.execute(
                select(Application).where(
                    Application.job_id == job_id,
                    Application.candidate_id == profile.id,
                )
            )
            app = app_res.scalar_one_or_none()
            if app and app.cover_letter:
                content = app.cover_letter

    if not content:
        generator = get_cover_letter_generator()
        res = await generator.generate_cover_letter(job=job, tone="technical", db=db)
        return CoverLetterResponse(
            job_id=job.id,
            company=job.company or "Company",
            title=job.title,
            content_markdown=res.content_markdown,
            tone=res.tone,
            word_count=res.word_count,
            file_path_pdf=res.file_path_pdf,
            file_path_md=res.file_path_md,
            validation_passed=res.validation_passed,
            confidence_score=res.confidence_score,
            warnings=res.warnings,
            verified_skills=res.verified_skills,
            generator_source=res.generator_source,
        )

    val_engine = get_evidence_engine()
    val_report = val_engine.validate_resume_content(content)
    words = len(re.findall(r"\b\w+\b", content))

    return CoverLetterResponse(
        job_id=job.id,
        company=job.company or "Company",
        title=job.title,
        content_markdown=content,
        tone="technical",
        word_count=words,
        file_path_pdf=str(pdf_path.absolute()) if pdf_path.exists() else None,
        file_path_md=str(md_path.absolute()) if md_path.exists() else None,
        validation_passed=val_report.passed,
        confidence_score=val_report.confidence_score,
        warnings=val_report.warnings,
        verified_skills=list(val_report.verified_skills),
        generator_source="saved_document",
    )


@router.put("/{job_id}/cover-letter", response_model=CoverLetterResponse)
async def update_cover_letter_endpoint(
    job_id: int,
    req: CoverLetterUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CoverLetterResponse:
    """
    Update / edit cover letter content, perform live anti-hallucination check, and re-export PDF.
    """
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    content = req.content_markdown.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Cover letter content cannot be empty")

    val_engine = get_evidence_engine()
    val_report = val_engine.validate_resume_content(content)

    base_dir = Path("documents/generated")
    base_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = str((base_dir / f"CoverLetter_Shubham_Prakash_Job{job.id}.pdf").absolute())
    md_path = str((base_dir / f"CoverLetter_Shubham_Prakash_Job{job.id}.md").absolute())

    CoverLetterExporter.export_markdown(content, md_path)
    CoverLetterExporter.export_pdf(
        content=content,
        output_path=pdf_path,
        candidate_name="Shubham Prakash",
        company=job.company or "Company",
        title=job.title,
    )

    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=current_user.full_name or "Shubham Prakash",
            email=current_user.email,
            location="Mumbai, India",
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    app_res = await db.execute(
        select(Application).where(
            Application.job_id == job_id,
            Application.candidate_id == profile.id,
        )
    )
    app = app_res.scalar_one_or_none()
    if not app:
        app = Application(
            job_id=job_id,
            candidate_id=profile.id,
            status="RESUME_READY",
            cover_letter=content,
        )
        db.add(app)
    else:
        app.cover_letter = content
    await db.commit()

    words = len(re.findall(r"\b\w+\b", content))

    return CoverLetterResponse(
        job_id=job.id,
        company=job.company or "Company",
        title=job.title,
        content_markdown=content,
        tone="custom",
        word_count=words,
        file_path_pdf=pdf_path,
        file_path_md=md_path,
        validation_passed=val_report.passed,
        confidence_score=val_report.confidence_score,
        warnings=val_report.warnings,
        verified_skills=list(val_report.verified_skills),
        generator_source="user_edited",
    )


@router.get("/{job_id}/cover-letter/download/{format}")
async def download_cover_letter(
    job_id: int,
    format: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Download cover letter as ATS PDF or Markdown file.
    """
    format = format.lower()
    if format not in ("pdf", "md"):
        raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'md'")

    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    base_dir = Path("documents/generated")
    base_dir.mkdir(parents=True, exist_ok=True)
    file_path = base_dir / f"CoverLetter_Shubham_Prakash_Job{job.id}.{format}"

    if not file_path.exists():
        generator = get_cover_letter_generator()
        await generator.generate_cover_letter(job=job, db=db)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Cover letter {format.upper()} file not found")

    media_type = "application/pdf" if format == "pdf" else "text/markdown; charset=utf-8"
    company_clean = (job.company or "Company").replace(" ", "_")
    filename = f"CoverLetter_Shubham_Prakash_{company_clean}_{job.id}.{format}"
    return FileResponse(
        path=str(file_path.absolute()),
        media_type=media_type,
        filename=filename,
    )


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Soft delete a job by setting status to 'closed'."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = "closed"
    await db.commit()
    return {"message": f"Job {job_id} closed"}
