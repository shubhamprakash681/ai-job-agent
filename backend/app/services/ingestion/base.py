import asyncio
import random
import urllib.robotparser
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from urllib.parse import urlparse
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class RawJobData(BaseModel):
    source: str
    source_job_id: str | None = None
    url: str | None = None
    title: str
    company: str | None = None
    raw_location: str | None = None
    is_remote: bool = False
    raw_salary: str | None = None
    raw_experience: str | None = None
    description: str | None = None
    skill_tags: list[str] = Field(default_factory=list)
    posted_at: datetime | None = None
    application_url: str | None = None
    source_type: str = "PUBLIC_PAGE"  # API, FEED, PUBLIC_PAGE, MANUAL
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobSearchQuery(BaseModel):
    keyword: str = "Java Spring Boot"
    location: str = "Mumbai"
    remote: bool = False
    experience_years: float = 3.0
    limit: int = 20


class BaseJobSourceAdapter(ABC):
    """
    Abstract base class for all job source adapters.
    Enforces compliance, robots.txt inspection, and rate limiting with jitter.
    """

    source_name: str = "base"
    is_enabled: bool = True
    requires_auth: bool = False
    min_delay_seconds: float = 2.0
    max_delay_seconds: float = 5.0

    def __init__(self):
        self._robots_parsers: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last_request_time: float = 0.0

    async def respect_rate_limit(self) -> None:
        """Enforce delay with random jitter between outgoing HTTP requests."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        target_delay = random.uniform(self.min_delay_seconds, self.max_delay_seconds)

        if elapsed < target_delay:
            wait_time = target_delay - elapsed
            logger.debug(
                "Rate limit pause",
                adapter=self.source_name,
                wait_seconds=round(wait_time, 2),
            )
            await asyncio.sleep(wait_time)

        self._last_request_time = asyncio.get_event_loop().time()

    def check_robots_txt(self, target_url: str, user_agent: str = "AIJobAgentBot/1.0") -> bool:
        """
        Inspect the site's robots.txt before making public scraping requests.
        Returns True if scraping the path is permitted, False otherwise.
        """
        try:
            parsed = urlparse(target_url)
            base_host = f"{parsed.scheme}://{parsed.netloc}"

            if base_host not in self._robots_parsers:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(f"{base_host}/robots.txt")
                try:
                    rp.read()
                    self._robots_parsers[base_host] = rp
                except Exception as e:
                    logger.warning("Could not read robots.txt, defaulting to cautious permit", host=base_host, error=str(e))
                    return True

            rp = self._robots_parsers[base_host]
            allowed = rp.can_fetch(user_agent, target_url)
            if not allowed:
                logger.warning("robots.txt disallowed path", adapter=self.source_name, url=target_url)
            return allowed
        except Exception:
            return True

    @abstractmethod
    async def fetch_jobs(self, query: JobSearchQuery) -> list[RawJobData]:
        """Fetch a list of job opportunities matching the search query."""
        pass

    @abstractmethod
    async def fetch_job_details(self, job_url: str) -> RawJobData | None:
        """Fetch detailed information for a single job listing."""
        pass

