from datetime import datetime, timezone
import re
from app.services.ingestion.base import BaseJobSourceAdapter, JobSearchQuery, RawJobData


class ManualJobAdapter(BaseJobSourceAdapter):
    """
    Adapter for manually entered jobs (via URL or pasted text).
    First-class citizen allowing users to input jobs from any source (including LinkedIn)
    without automated scraping.
    """

    source_name = "manual"
    is_enabled = True
    requires_auth = False

    def parse_manual_input(
        self,
        title: str,
        company: str | None = None,
        description: str = "",
        url: str | None = None,
        location: str | None = None,
        salary: str | None = None,
        experience: str | None = None,
        application_url: str | None = None,
    ) -> RawJobData:
        """Create a RawJobData object from manual user inputs."""
        # Detect if title wasn't explicitly given but first line of description has it
        if not title and description:
            first_line = description.strip().split("\n")[0].strip("# ")
            if len(first_line) < 100:
                title = first_line

        # Try to extract company from URL if missing
        if not company and url:
            match = re.search(r"https?://(?:www\.)?([^/]+)", url)
            if match:
                domain_parts = match.group(1).split(".")
                if len(domain_parts) >= 2:
                    company = domain_parts[0].capitalize()

        return RawJobData(
            source="manual",
            source_job_id=None,
            url=url,
            title=title or "Software Engineer",
            company=company or "Confidential / Direct",
            raw_location=location or "Mumbai",
            raw_salary=salary,
            raw_experience=experience,
            description=description,
            posted_at=datetime.now(timezone.utc),
            application_url=application_url or url,
            source_type="MANUAL",
        )

    async def fetch_jobs(self, query: JobSearchQuery) -> list[RawJobData]:
        # Manual adapter does not poll externally
        return []

    async def fetch_job_details(self, job_url: str) -> RawJobData | None:
        return None

