import hashlib
import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Tuple
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.services.ingestion.base import RawJobData


def clean_text_for_hash(text: str | None) -> str:
    """Normalize text for consistent content hashing: lowercase, strip punctuation, collapse whitespace."""
    if not text:
        return ""
    cleaned = text.lower()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def compute_content_hash(company: str | None, title: str, location: str | None) -> str:
    """
    Level 3 Content Hash:
    SHA-256 of cleaned (company + title + primary_location).
    """
    comp = clean_text_for_hash(company)
    tit = clean_text_for_hash(title)
    loc = clean_text_for_hash(location)
    raw_key = f"{comp}|{tit}|{loc}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def compute_similarity(str1: str, str2: str) -> float:
    """Compute string similarity ratio between 0.0 and 1.0."""
    return SequenceMatcher(None, clean_text_for_hash(str1), clean_text_for_hash(str2)).ratio()


async def check_duplicate(
    db: AsyncSession,
    raw_job: RawJobData,
    content_hash: str,
) -> Tuple[bool, str | None, int | None]:
    """
    Check for duplicate jobs using a 4-level deduplication hierarchy:
    1. Exact URL match
    2. Source + Source Job ID match
    3. SHA-256 Content hash match
    4. Fuzzy match: Company similarity > 0.85, Title similarity > 0.85, within 7 days

    Returns:
        (is_duplicate: bool, reason: str | None, existing_job_id: int | None)
    """
    # Level 1: Exact URL match
    if raw_job.url:
        url_q = select(Job).where(or_(Job.url == raw_job.url, Job.canonical_url == raw_job.url))
        url_res = await db.execute(url_q)
        existing_url_job = url_res.scalar_one_or_none()
        if existing_url_job:
            return True, "Level 1: Exact URL match", existing_url_job.id

    # Level 2: Source + Source Job ID match
    if raw_job.source and raw_job.source_job_id:
        src_q = select(Job).where(
            Job.source == raw_job.source,
            Job.source_job_id == str(raw_job.source_job_id),
        )
        src_res = await db.execute(src_q)
        existing_src_job = src_res.scalar_one_or_none()
        if existing_src_job:
            return True, f"Level 2: Source ID match ({raw_job.source}:{raw_job.source_job_id})", existing_src_job.id

    # Level 3: Content Hash match
    hash_q = select(Job).where(Job.raw_content_hash == content_hash)
    hash_res = await db.execute(hash_q)
    existing_hash_job = hash_res.scalar_one_or_none()
    if existing_hash_job:
        return True, "Level 3: Normalized content hash match", existing_hash_job.id

    # Level 4: Fuzzy similarity (within past 7 days)
    recent_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    recent_q = select(Job).where(Job.created_at >= recent_cutoff).limit(100)
    recent_res = await db.execute(recent_q)
    recent_jobs = recent_res.scalars().all()

    target_company = raw_job.company or ""
    target_title = raw_job.title

    for candidate in recent_jobs:
        cand_comp = candidate.company or ""
        comp_sim = compute_similarity(target_company, cand_comp)
        title_sim = compute_similarity(target_title, candidate.title)

        if comp_sim >= 0.85 and title_sim >= 0.85:
            return (
                True,
                f"Level 4: Fuzzy match with Job #{candidate.id} (Company: {comp_sim:.2f}, Title: {title_sim:.2f})",
                candidate.id,
            )

    return False, None, None

