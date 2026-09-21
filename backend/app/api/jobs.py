from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
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
from app.services.ingestion.base import JobSearchQuery
from app.services.ingestion.pipeline import get_ingestion_pipeline
from app.services.processing.processor import get_job_processor
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


@router.post("/{job_id}/tailor-resume")
async def tailor_resume(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Trigger resume tailoring for a job (Phase 6 integration)."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Resume tailoring queued", "job_id": job_id}


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
