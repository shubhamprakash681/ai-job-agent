from datetime import datetime, timezone
import structlog
from app.models.application import Application
from app.models.job import Job
from app.schemas.monitoring import FollowupDraftResponse, FollowupItem

logger = structlog.get_logger(__name__)

BANNED_CLICHES = [
    "i hope this email finds you well",
    "thrilled to follow up",
    "in today's fast-paced world",
    "proven track record",
    "synergy",
]


def calculate_followup_status(
    applied_at: datetime | None,
    now: datetime | None = None,
) -> tuple[int, str, str]:
    """
    Calculate days since application submission and determine follow-up categorization.
    Returns: (days_since_applied, followup_type, suggested_action)
    """
    if not applied_at:
        return 0, "RECENT", "Recently submitted. Awaiting initial recruiter review."

    if now is None:
        now = datetime.now(timezone.utc)

    # Ensure tz-aware comparison
    if applied_at.tzinfo is None:
        applied_at = applied_at.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    delta = now - applied_at
    days = max(0, delta.days)

    if days >= 30:
        return (
            days,
            "30_DAY_STALE",
            "Application has been inactive for over 30 days. Recommend archiving or checking career portal.",
        )
    elif days >= 14:
        return (
            days,
            "14_DAY",
            "14-day mark reached. Recommended: Send a second polite follow-up or status inquiry.",
        )
    elif days >= 7:
        return (
            days,
            "7_DAY",
            "7-day follow-up window open. Recommended: Send a courteous status check-in.",
        )
    else:
        return (
            days,
            "RECENT",
            f"Applied {days} day(s) ago. Within standard recruiter review window (7-day wait).",
        )


class FollowupEngine:
    """
    Follow-up scheduler and grounded email draft generator for submitted applications.
    Strictly adheres to Shubham Prakash's candidate facts (~3.2 years experience, TCS Digital, Accenture).
    """

    @staticmethod
    def generate_draft(
        application: Application,
        job: Job,
        tone: str = "professional",
        recipient_name: str | None = None,
        recipient_email: str | None = None,
        custom_instructions: str | None = None,
    ) -> FollowupDraftResponse:
        days, f_type, _ = calculate_followup_status(application.applied_at)
        greeting_name = recipient_name if recipient_name else "Hiring Team"
        company = job.company or "the engineering team"
        role_title = job.title or "Software Engineer"

        subject = f"Application Status Inquiry: {role_title} — Shubham Prakash"

        if tone == "concise":
            body = (
                f"Dear {greeting_name},\n\n"
                f"I am writing to respectfully inquire about the status of my application for the {role_title} position "
                f"at {company}, which I submitted {days} days ago.\n\n"
                f"With ~3.2 years of experience building resilient microservices and full-stack systems with Java, "
                f"Spring Boot, and React at TCS Digital and Accenture, I remain very interested in the role. "
                f"My notice period is 30 days.\n\n"
                f"Please let me know if any additional details or references would be helpful as you evaluate candidates.\n\n"
                f"Sincerely,\n"
                f"Shubham Prakash\n"
                f"shubham@example.com | Mumbai, India\n"
                f"https://www.shubhamprakash681.in/"
            )
        elif tone == "courteous":
            body = (
                f"Dear {greeting_name},\n\n"
                f"I understand your team is likely reviewing many candidates for the {role_title} position at {company}, "
                f"and I wanted to politely check in regarding the status of my application submitted {days} days ago.\n\n"
                f"Over the past 3.2 years at TCS Digital and Accenture, I have developed backend services and high-scale "
                f"web applications utilizing Java, Spring Boot, Kafka, and React. I am very enthusiastic about the work "
                f"your engineering team is doing at {company} and would welcome the opportunity to discuss how my background "
                f"aligns with your technical roadmap. My notice period is 30 days.\n\n"
                f"Thank you very much for your time and consideration. I look forward to hearing from you.\n\n"
                f"Warm regards,\n"
                f"Shubham Prakash\n"
                f"shubham@example.com | Mumbai, India\n"
                f"https://www.shubhamprakash681.in/"
            )
        else:  # professional (default)
            body = (
                f"Dear {greeting_name},\n\n"
                f"I am writing to follow up on my application for the {role_title} role at {company}, submitted {days} days ago.\n\n"
                f"To briefly summarize my background, I bring ~3.2 years of software development experience specializing in "
                f"Java, Spring Boot, distributed microservices, and modern React frontends across TCS Digital and Accenture. "
                f"Having engineered systems supporting high concurrency and strict SLAs, I am confident in my ability to deliver "
                f"immediate value to {company}.\n\n"
                f"I am available on a 30-day notice period and would be glad to provide any supplementary code samples, portfolio "
                f"walkthroughs, or work authorization details required.\n\n"
                f"Thank you for your time and review.\n\n"
                f"Best regards,\n"
                f"Shubham Prakash\n"
                f"shubham@example.com | Mumbai, India\n"
                f"https://www.shubhamprakash681.in/"
            )

        # Verification check: No banned clichés
        lower_body = body.lower()
        for cliche in BANNED_CLICHES:
            if cliche in lower_body:
                logger.warning("cliche_detected_in_followup", cliche=cliche)

        return FollowupDraftResponse(
            application_id=application.id,
            company=company,
            job_title=role_title,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            days_since_applied=days,
            tone=tone,
            created_at=datetime.now(timezone.utc),
        )
