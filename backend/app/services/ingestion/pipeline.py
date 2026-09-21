from typing import Any
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.services.ingestion.adapters.greenhouse import GreenhouseAdapter
from app.services.ingestion.adapters.indeed import IndeedAdapter
from app.services.ingestion.adapters.lever import LeverAdapter
from app.services.ingestion.adapters.manual import ManualJobAdapter
from app.services.ingestion.adapters.naukri import NaukriAdapter
from app.services.ingestion.base import BaseJobSourceAdapter, JobSearchQuery, RawJobData
from app.services.ingestion.dedup import check_duplicate
from app.services.ingestion.normalizer import normalize_job_data

logger = structlog.get_logger(__name__)


class IngestionPipeline:
    def __init__(self):
        self.adapters: dict[str, BaseJobSourceAdapter] = {
            "manual": ManualJobAdapter(),
            "greenhouse": GreenhouseAdapter(),
            "lever": LeverAdapter(),
            "indeed": IndeedAdapter(),
            "naukri": NaukriAdapter(),
        }

    def get_adapter(self, source_name: str) -> BaseJobSourceAdapter | None:
        return self.adapters.get(source_name.lower())

    def list_sources(self) -> list[dict[str, Any]]:
        return [
            {
                "source": name,
                "enabled": adapter.is_enabled,
                "requires_auth": adapter.requires_auth,
                "description": adapter.__doc__.strip().split("\n")[0] if adapter.__doc__ else "",
            }
            for name, adapter in self.adapters.items()
        ]

    async def ingest_manual_job(
        self,
        db: AsyncSession,
        title: str,
        company: str | None = None,
        description: str = "",
        url: str | None = None,
        location: str | None = None,
        salary: str | None = None,
        experience: str | None = None,
        application_url: str | None = None,
    ) -> tuple[Job, bool, str | None]:
        """
        Ingest a single manually provided job.
        Returns (job_instance, is_new: bool, duplicate_reason: str | None).
        """
        manual_adapter = self.adapters["manual"]
        assert isinstance(manual_adapter, ManualJobAdapter)

        raw = manual_adapter.parse_manual_input(
            title=title,
            company=company,
            description=description,
            url=url,
            location=location,
            salary=salary,
            experience=experience,
            application_url=application_url,
        )

        canonical_dict = normalize_job_data(raw)
        content_hash = canonical_dict["raw_content_hash"]

        is_dup, reason, existing_id = await check_duplicate(db, raw, content_hash)
        if is_dup and existing_id:
            existing_job = await db.get(Job, existing_id)
            if existing_job:
                return existing_job, False, reason

        new_job = Job(**canonical_dict)
        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)

        logger.info("Manual job ingested successfully", job_id=new_job.id, title=new_job.title, company=new_job.company)
        return new_job, True, None

    async def run_ingestion(
        self,
        db: AsyncSession,
        sources: list[str] | None = None,
        query: JobSearchQuery | None = None,
    ) -> dict[str, Any]:
        """
        Run batch ingestion across specified sources.
        Deduplicates and stores new opportunities into the database.
        """
        query = query or JobSearchQuery()
        target_sources = sources or ["greenhouse", "lever", "indeed", "naukri"]

        total_fetched = 0
        new_jobs_saved = 0
        duplicates_skipped = 0
        errors: list[str] = []

        for source_name in target_sources:
            adapter = self.get_adapter(source_name)
            if not adapter or not adapter.is_enabled:
                continue

            try:
                logger.info("Starting ingestion fetch", source=source_name, query=query.keyword)
                raw_jobs = await adapter.fetch_jobs(query)
                total_fetched += len(raw_jobs)

                for raw in raw_jobs:
                    canonical_dict = normalize_job_data(raw)
                    content_hash = canonical_dict["raw_content_hash"]

                    is_dup, reason, _ = await check_duplicate(db, raw, content_hash)
                    if is_dup:
                        duplicates_skipped += 1
                        logger.debug("Duplicate job detected and skipped", reason=reason, title=raw.title, company=raw.company)
                        continue

                    new_job = Job(**canonical_dict)
                    db.add(new_job)
                    new_jobs_saved += 1

                await db.commit()
            except Exception as e:
                error_msg = f"Error running ingestion for {source_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)

        return {
            "status": "completed",
            "total_fetched": total_fetched,
            "new_jobs_saved": new_jobs_saved,
            "duplicates_skipped": duplicates_skipped,
            "errors": errors,
        }


_PIPELINE_INSTANCE: IngestionPipeline | None = None


def get_ingestion_pipeline() -> IngestionPipeline:
    global _PIPELINE_INSTANCE
    if _PIPELINE_INSTANCE is None:
        _PIPELINE_INSTANCE = IngestionPipeline()
    return _PIPELINE_INSTANCE

