from datetime import datetime, timezone
import httpx
import structlog
from app.services.ingestion.base import BaseJobSourceAdapter, JobSearchQuery, RawJobData

logger = structlog.get_logger(__name__)

DEFAULT_LEVER_COMPANIES = [
    "atlassian",
    "deliveroo",
    "canva",
    "hopper",
]


class LeverAdapter(BaseJobSourceAdapter):
    """
    Direct API adapter for Lever public job board endpoints.
    Official public API: https://api.lever.co/v0/postings/{company}?mode=json
    """

    source_name = "lever"
    is_enabled = True
    requires_auth = False

    def __init__(self, target_companies: list[str] | None = None):
        super().__init__()
        self.target_companies = target_companies or DEFAULT_LEVER_COMPANIES

    async def fetch_jobs(self, query: JobSearchQuery) -> list[RawJobData]:
        """Fetch jobs across configured Lever boards and filter by keywords/location."""
        results: list[RawJobData] = []

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for comp in self.target_companies:
                await self.respect_rate_limit()
                url = f"https://api.lever.co/v0/postings/{comp}?mode=json"

                try:
                    resp = await client.get(url, headers={"User-Agent": "AIJobAgent/1.0"})
                    if resp.status_code != 200:
                        logger.debug("Lever endpoint returned non-200", company=comp, status=resp.status_code)
                        continue

                    postings = resp.json()
                    if not isinstance(postings, list):
                        continue

                    for job in postings:
                        title = job.get("text", "")
                        categories = job.get("categories", {})
                        location_name = categories.get("location", "")
                        commitment = categories.get("commitment", "")
                        description = job.get("descriptionPlain", "") or job.get("description", "")

                        combined = f"{title} {description} {location_name}".lower()
                        keywords = [k.strip().lower() for k in query.keyword.split() if k.strip()]
                        if not any(k in combined for k in keywords):
                            continue

                        results.append(
                            RawJobData(
                                source="lever",
                                source_job_id=str(job.get("id")),
                                url=job.get("hostedUrl"),
                                title=title,
                                company=comp.capitalize(),
                                raw_location=location_name,
                                description=description,
                                posted_at=datetime.now(timezone.utc),
                                application_url=job.get("applyUrl") or job.get("hostedUrl"),
                                source_type="API",
                                metadata={"commitment": commitment},
                            )
                        )

                        if len(results) >= query.limit:
                            return results

                except Exception as e:
                    logger.warning("Error fetching from Lever board", company=comp, error=str(e))

        return results

    async def fetch_job_details(self, job_url: str) -> RawJobData | None:
        return None

