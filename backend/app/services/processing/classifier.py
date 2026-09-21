import json
import re
from typing import Any
import structlog
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.services.llm.client import UnifiedLLMClient
from app.services.llm.prompts import (
    JOB_CLASSIFICATION_SYSTEM_PROMPT,
    JOB_CLASSIFICATION_USER_TEMPLATE,
)

logger = structlog.get_logger(__name__)


class ClassificationResult(BaseModel):
    role_category: str = "JAVA_BACKEND"  # JAVA_BACKEND | JAVA_REACT_FULLSTACK | FULLSTACK_ENGINEER | DISTRIBUTED_SYSTEMS | UNRELATED
    fit_category: str = "MODERATE_FIT"   # HIGH_FIT | MODERATE_FIT | LOW_FIT | REJECT
    fit_score: int = 50                  # 0 to 100
    recommended_variant: str = "java-backend"  # java-react-fullstack | java-backend | fullstack-engineer | backend-distributed
    primary_technologies: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    experience_fit: str = "ACCEPTABLE"   # EXCELLENT | ACCEPTABLE | OVERQUALIFIED | UNDERQUALIFIED
    red_flags: list[str] = Field(default_factory=list)
    key_responsibilities: list[str] = Field(default_factory=list)
    reasoning: str = ""


class JobClassifier:
    """
    Intelligent Job Classifier that analyzes job requirements and maps them against
    Shubham Prakash's verified candidate profile.
    Uses UnifiedLLMClient with automatic failover (Groq -> Gemini -> Local -> Rule Heuristics).
    """

    def __init__(self):
        self.llm_client = UnifiedLLMClient()

    def format_experience(self, job: Job) -> str:
        if job.experience_min is not None and job.experience_max is not None:
            return f"{job.experience_min} - {job.experience_max} years"
        elif job.experience_min is not None:
            return f"{job.experience_min}+ years"
        return "Not explicitly specified"

    def format_salary(self, job: Job) -> str:
        if job.salary_min is not None and job.salary_max is not None:
            if job.currency == "INR":
                return f"₹{job.salary_min / 100000:.1f}L - ₹{job.salary_max / 100000:.1f}L ({job.currency})"
            return f"{job.currency} {job.salary_min:,} - {job.salary_max:,}"
        return "Not specified"

    def format_locations(self, job: Job) -> str:
        locs = []
        if job.locations:
            try:
                locs = json.loads(job.locations)
            except Exception:
                locs = [job.locations]
        if job.remote:
            locs.append("Remote")
        return ", ".join(locs) if locs else "Not specified"

    async def classify(self, job: Job, db: AsyncSession | None = None) -> ClassificationResult:
        """
        Classify job and calculate candidate fit.
        Calls the LLM client or rule fallback, logging telemetry to `llm_requests` if db session is provided.
        """
        user_prompt = JOB_CLASSIFICATION_USER_TEMPLATE.format(
            title=job.title or "Unknown Title",
            company=job.company or "Unknown Company",
            location=self.format_locations(job),
            experience=self.format_experience(job),
            salary=self.format_salary(job),
            description=job.description or job.title or "",
        )

        llm_result = await self.llm_client.generate_structured_json(
            system_prompt=JOB_CLASSIFICATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            db=db,
            job_id=job.id,
            operation="classify_job",
        )

        data = llm_result.parsed_json or {}

        # Validate and sanitize fields into ClassificationResult
        role_cat = str(data.get("role_category", "JAVA_BACKEND")).upper()
        if role_cat not in {
            "JAVA_BACKEND",
            "JAVA_REACT_FULLSTACK",
            "FULLSTACK_ENGINEER",
            "DISTRIBUTED_SYSTEMS",
            "UNRELATED",
        }:
            role_cat = "JAVA_BACKEND"

        fit_cat = str(data.get("fit_category", "MODERATE_FIT")).upper()
        if fit_cat not in {"HIGH_FIT", "MODERATE_FIT", "LOW_FIT", "REJECT"}:
            fit_cat = "MODERATE_FIT"

        try:
            fit_score = int(data.get("fit_score", 50))
            fit_score = max(0, min(100, fit_score))
        except (ValueError, TypeError):
            fit_score = 50

        rec_variant = str(data.get("recommended_variant", "java-backend")).lower()
        if rec_variant not in {
            "java-react-fullstack",
            "java-backend",
            "fullstack-engineer",
            "backend-distributed",
        }:
            rec_variant = "java-backend"

        # Sanitize list fields
        primary_techs = [str(x) for x in data.get("primary_technologies", []) if isinstance(x, (str, int))]
        matched_skills = [str(x) for x in data.get("matched_skills", []) if isinstance(x, (str, int))]
        missing_skills = [str(x) for x in data.get("missing_skills", []) if isinstance(x, (str, int))]
        red_flags = [str(x) for x in data.get("red_flags", []) if isinstance(x, (str, int))]
        key_resps = [str(x) for x in data.get("key_responsibilities", []) if isinstance(x, (str, int))]
        exp_fit = str(data.get("experience_fit", "ACCEPTABLE")).upper()
        reasoning = str(data.get("reasoning", ""))

        return ClassificationResult(
            role_category=role_cat,
            fit_category=fit_cat,
            fit_score=fit_score,
            recommended_variant=rec_variant,
            primary_technologies=primary_techs,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience_fit=exp_fit,
            red_flags=red_flags,
            key_responsibilities=key_resps,
            reasoning=reasoning,
        )


_classifier_instance: JobClassifier | None = None


def get_job_classifier() -> JobClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = JobClassifier()
    return _classifier_instance

