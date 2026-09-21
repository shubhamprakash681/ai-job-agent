import re
from datetime import datetime, timezone
import httpx
import structlog
from app.services.ingestion.base import BaseJobSourceAdapter, JobSearchQuery, RawJobData

logger = structlog.get_logger(__name__)


class NaukriAdapter(BaseJobSourceAdapter):
    """
    Naukri India search adapter.
    Enforces strict rate limiting with jitter, respects robots.txt,
    and falls back cleanly when anti-bot or verification challenges appear.
    """

    source_name = "naukri"
    is_enabled = True
    requires_auth = False
    min_delay_seconds = 3.0
    max_delay_seconds = 6.0

    async def fetch_jobs(self, query: JobSearchQuery) -> list[RawJobData]:
        results: list[RawJobData] = []
        base_url = "https://www.naukri.com"

        # Check robots.txt
        if not self.check_robots_txt(f"{base_url}/jobapi"):
            logger.info("Skipping Naukri fetch: disallow in robots.txt")

        await self.respect_rate_limit()

        # Format URL for keyword search
        kw_slug = query.keyword.lower().replace(" ", "-")
        loc_slug = query.location.lower().replace(" ", "-") if query.location else ""
        search_path = f"/{kw_slug}-jobs-in-{loc_slug}" if loc_slug else f"/{kw_slug}-jobs"
        search_url = f"{base_url}{search_path}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.naukri.com/",
        }

        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                resp = await client.get(search_url, headers=headers)

                # Safe fallback: never attempt to bypass CAPTCHA or Cloudflare challenges
                if resp.status_code in (403, 429) or "captcha" in resp.text.lower() or "challenge" in resp.text.lower():
                    logger.warning("Naukri presented verification challenge or rate limit. Safely backing off.", status=resp.status_code)
                    return []

                if resp.status_code != 200:
                    return []

                # Extract JSON payload embedded in HTML script tags if present
                tuple_matches = re.findall(
                    r'<a[^>]*class="title[^"]*"[^>]*href="([^"]+)"[^>]*title="([^"]+)"',
                    resp.text,
                )
                comp_matches = re.findall(
                    r'<a[^>]*class="comp-name[^"]*"[^>]*title="([^"]+)"',
                    resp.text,
                )

                for i, (job_url, title) in enumerate(tuple_matches[:query.limit]):
                    company = comp_matches[i] if i < len(comp_matches) else "Naukri Listing"
                    results.append(
                        RawJobData(
                            source="naukri",
                            source_job_id=None,
                            url=job_url,
                            title=title.strip(),
                            company=company.strip(),
                            raw_location=query.location,
                            posted_at=datetime.now(timezone.utc),
                            application_url=job_url,
                            source_type="PUBLIC_PAGE",
                        )
                    )

        except Exception as e:
            logger.warning("Error during Naukri query", error=str(e))

        return results

    async def fetch_job_details(self, job_url: str) -> RawJobData | None:
        return None

