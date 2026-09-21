import re
from datetime import datetime, timezone
import httpx
import structlog
from app.services.ingestion.base import BaseJobSourceAdapter, JobSearchQuery, RawJobData

logger = structlog.get_logger(__name__)


class IndeedAdapter(BaseJobSourceAdapter):
    """
    Indeed public search & feed adapter.
    Enforces strict robots.txt inspection, random jitter delays, and safe fallback.
    """

    source_name = "indeed"
    is_enabled = True
    requires_auth = False
    min_delay_seconds = 3.0
    max_delay_seconds = 6.0

    async def fetch_jobs(self, query: JobSearchQuery) -> list[RawJobData]:
        results: list[RawJobData] = []
        base_url = "https://in.indeed.com"

        # 1. Respect robots.txt check
        if not self.check_robots_txt(f"{base_url}/jobs"):
            logger.info("Skipping Indeed fetch: disallow rule in robots.txt")
            return []

        # 2. Rate limit with random jitter
        await self.respect_rate_limit()

        search_url = f"{base_url}/jobs?q={query.keyword.replace(' ', '+')}&l={query.location.replace(' ', '+')}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                resp = await client.get(search_url, headers=headers)

                # Safe handling of anti-bot or CAPTCHA pages (never attempt bypass per rules!)
                if resp.status_code in (403, 429) or "cf-challenge" in resp.text.lower() or "captcha" in resp.text.lower():
                    logger.warning("Indeed presented verification or rate limit. Safely backing off without bypassing.", status=resp.status_code)
                    return []

                if resp.status_code != 200:
                    return []

                # Parse standard job cards from HTML using regex to avoid heavy parsing deps
                job_card_patterns = re.findall(
                    r'<h2 class="jobTitle[^"]*"[^>]*>.*?<a[^>]*href="(/rc/clk[^"]*|/viewjob[^"]*)"[^>]*>.*?<span[^>]*>(.*?)</span>.*?</h2>.*?'
                    r'<span data-testid="company-name"[^>]*>(.*?)</span>.*?'
                    r'<div data-testid="text-location"[^>]*>(.*?)</div>',
                    resp.text,
                    re.DOTALL,
                )

                for link, title, company, loc in job_card_patterns[:query.limit]:
                    clean_title = re.sub(r"<[^>]+>", "", title).strip()
                    clean_comp = re.sub(r"<[^>]+>", "", company).strip()
                    clean_loc = re.sub(r"<[^>]+>", "", loc).strip()
                    full_link = f"{base_url}{link}" if link.startswith("/") else link

                    job_id_match = re.search(r"jk=([a-zA-Z0-9]+)", link)
                    source_id = job_id_match.group(1) if job_id_match else None

                    results.append(
                        RawJobData(
                            source="indeed",
                            source_job_id=source_id,
                            url=full_link,
                            title=clean_title,
                            company=clean_comp,
                            raw_location=clean_loc,
                            posted_at=datetime.now(timezone.utc),
                            application_url=full_link,
                            source_type="PUBLIC_PAGE",
                        )
                    )

        except Exception as e:
            logger.warning("Error querying Indeed search", error=str(e))

        return results

    async def fetch_job_details(self, job_url: str) -> RawJobData | None:
        return None

