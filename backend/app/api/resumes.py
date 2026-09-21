import os
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.job import Job
from app.models.resume import ResumeVariant, ResumeVersion
from app.models.user import User
from app.schemas.resume import (
    ResumeVariantResponse,
    ResumeVersionListResponse,
    ResumeVersionResponse,
)
from app.services.candidate.kb_loader import get_candidate_kb

router = APIRouter()


@router.get("/variants", response_model=list[ResumeVariantResponse])
async def list_variants(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ResumeVariantResponse]:
    """List all candidate resume variants."""
    result = await db.execute(select(ResumeVariant))
    variants = result.scalars().all()
    if not variants:
        # Fallback to candidate knowledge base variants
        kb = get_candidate_kb()
        return [
            ResumeVariantResponse(
                id=i + 1,
                name=v.id,
                display_name=v.name,
                description=v.summary_emphasis,
                is_default=v.is_default,
                priority_skills=", ".join(v.priority_skills),
            )
            for i, v in enumerate(kb.variants)
        ]
    return [ResumeVariantResponse.model_validate(v) for v in variants]


@router.get("/versions", response_model=ResumeVersionListResponse)
async def list_versions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    job_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeVersionListResponse:
    """List tailored resume versions with pagination and optional job filter."""
    query = select(ResumeVersion)
    count_query = select(func.count(ResumeVersion.id))

    if job_id is not None:
        query = query.where(ResumeVersion.job_id == job_id)
        count_query = count_query.where(ResumeVersion.job_id == job_id)

    total = await db.scalar(count_query) or 0
    offset = (page - 1) * per_page
    query = query.order_by(ResumeVersion.id.desc()).offset(offset).limit(per_page)

    result = await db.execute(query)
    versions = result.scalars().all()

    # Load associated job details
    job_ids = [v.job_id for v in versions if v.job_id]
    jobs_by_id: dict[int, Job] = {}
    if job_ids:
        job_res = await db.execute(select(Job).where(Job.id.in_(job_ids)))
        jobs_by_id = {j.id: j for j in job_res.scalars().all()}

    items: list[ResumeVersionResponse] = []
    for v in versions:
        resp = ResumeVersionResponse.model_validate(v)
        if v.job_id and v.job_id in jobs_by_id:
            resp.job_title = jobs_by_id[v.job_id].title
            resp.job_company = jobs_by_id[v.job_id].company
        items.append(resp)

    return ResumeVersionListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/versions/{version_id}", response_model=ResumeVersionResponse)
async def get_version(
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeVersionResponse:
    """Get single tailored resume version with diff, evidence, and report."""
    version = await db.get(ResumeVersion, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found")

    resp = ResumeVersionResponse.model_validate(version)
    if version.job_id:
        job = await db.get(Job, version.job_id)
        if job:
            resp.job_title = job.title
            resp.job_company = job.company
    return resp


@router.get("/versions/{version_id}/download/{format}")
async def download_resume_file(
    version_id: int,
    format: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """
    Download resume in specified format: 'pdf', 'docx', or 'md'.
    """
    version = await db.get(ResumeVersion, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found")

    fmt = format.lower()
    if fmt == "pdf":
        file_path = version.file_path_pdf
        media_type = "application/pdf"
        filename = f"Resume_Shubham_Prakash_Job_{version.job_id or version.id}.pdf"
    elif fmt == "docx":
        file_path = version.file_path_docx
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"Resume_Shubham_Prakash_Job_{version.job_id or version.id}.docx"
    elif fmt in ["md", "markdown", "txt"]:
        file_path = str(Path(version.file_path_pdf or "").with_suffix(".md"))
        if not os.path.exists(file_path) and version.content_markdown:
            Path(file_path).write_text(version.content_markdown, encoding="utf-8")
        media_type = "text/markdown"
        filename = f"Resume_Shubham_Prakash_Job_{version.job_id or version.id}.md"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{format}'. Use 'pdf', 'docx', or 'md'.")

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Generated file not found on disk at {file_path}")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )
