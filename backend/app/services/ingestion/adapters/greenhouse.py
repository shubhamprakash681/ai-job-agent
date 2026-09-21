from datetime import datetime, timezone
import httpx
import structlog
from app.services.ingestion.base import BaseJobSourceAdapter, JobSearchQuery, RawJobData

logger = structlog.get_logger(__name__)

# Curated list of high-relevance tech companies utilizing Greenhouse job boards
DEFAULT_GREENHOUSE_BOARDS = [
    "postman",
    "razorpay",
    "swiggy",
    "datadog",
    "airmeet",
    "browserstack",
]


class GreenhouseAdapter(BaseJobSourceAdapter):
    """
    Direct API adapter for Greenhouse public board endpoints.
    Official public API: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
    """

    source_name = "greenhouse"
    is_enabled = True
    requires_auth = False

    def __init__(self, target_boards: list[str] | None = None):
        super().__init__()
        self.target_boards = target_boards or DEFAULT_GREENHOUSE_BOARDS

    async def fetch_jobs(self, query: JobSearchQuery) -> list[RawJobData]:
        """Fetch jobs across configured Greenhouse boards and filter by keywords/location."""
        results: list[RawJobData] = []

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for board in self.target_boards:
                await self.respect_rate_limit()
                url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"

                try:
                    resp = await client.get(url, headers={"User-Agent": "AIJobAgent/1.0"})
                    if resp.status_code != 200:
                        logger.debug("Greenhouse board returned non-200", board=board, status=resp.status_code)
                        continue

                    data = resp.json()
                    jobs_list = data.get("jobs", [])

                    for job in jobs_list:
                        title = job.get("title", "")
                        content = job.get("content", "")
                        location_name = job.get("location", {}).get("name", "")

                        # Filter by query keyword in title or content
                        combined = f"{title} {content} {location_name}".lower()
                        keywords = [k.strip().lower() for k in query.keyword.split() if k.strip()]
                        if not any(k in combined for k in keywords):
                            continue

                        # Check location filter if specified
                        if query.location and query.location.lower() not in combined and not query.remote:
                            continue

                        results.append(
                            RawJobData(
                                source="greenhouse",
                                source_job_id=str(job.get("id")),
                                url=job.get("absolute_url"),
                                title=title,
                                company=board.capitalize(),
                                raw_location=location_name,
                                description=content,
                                posted_at=datetime.now(timezone.utc),
                                application_url=job.get("absolute_url"),
                                source_type="API",
                                metadata={"board_token": board},
                            )
                        )

                        if len(results) >= query.limit:
                            return results

                except Exception as e:
                    logger.warning("Error fetching from Greenhouse board", board=board, error=str(e))

        return results

    async def fetch_job_details(self, job_url: str) -> RawJobData | None:
        # Greenhouse content=true already fetches full description in fetch_jobs
        return None

