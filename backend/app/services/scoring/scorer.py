import json
from typing import Any
import structlog
from pydantic import BaseModel, Field

from app.models.job import Job
from app.services.scoring.rubric import (
    score_core_skills,
    score_distributed_systems,
    score_experience,
    score_job_quality,
    score_location,
    score_role_relevance,
)

logger = structlog.get_logger(__name__)


class ScoringBreakdown(BaseModel):
    role_relevance: int = 0         # Max 25
    core_skills: int = 0            # Max 25
    distributed_systems: int = 0    # Max 15
    experience_fit: int = 0         # Max 15
    location_score: int = 0         # Max 10
    job_quality: int = 0            # Max 10
    total_score: int = 0            # 0 to 100
    llm_score: int | None = None
    fit_category: str = "IGNORE"    # AUTO_PREPARE | HIGH_PRIORITY | GOOD | OPTIONAL | IGNORE
    recommended_variant: str = "java-backend"
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    reasoning: str = ""


class JobScorer:
    """
    Multi-Dimensional 100-Point Candidate Job Scorer.
    Evaluates opportunities against Shubham Prakash's verified profile across 6 granular dimensions:
    1. Role Relevance (0 - 25)
    2. Core Tech Stack Match (0 - 25)
    3. Distributed Systems & Scale (0 - 15)
    4. Experience Level Match (0 - 15)
    5. Location & Work Mode Fit (0 - 10)
    6. Job Quality & Recency (0 - 10)
    """

    @staticmethod
    def calculate_fit_category(score: int) -> str:
        """
        Category mapping according to PROMPT.md Section 17 & 35:
        - 85 - 100: AUTO_PREPARE (Immediately ready for resume tailoring)
        - 70 - 84: HIGH_PRIORITY (Strong match)
        - 50 - 69: GOOD (Viable candidate)
        - 30 - 49: OPTIONAL (Marginal match)
        - < 30: IGNORE (Unrelated / poor fit)
        """
        if score >= 85:
            return "AUTO_PREPARE"
        if score >= 70:
            return "HIGH_PRIORITY"
        if score >= 50:
            return "GOOD"
        if score >= 30:
            return "OPTIONAL"
        return "IGNORE"

    @staticmethod
    def determine_recommended_variant(
        role_rel_score: int,
        core_matched: list[str],
        dist_matched: list[str],
        title: str,
        desc: str,
    ) -> str:
        """
        Recommend the optimal resume variant based on matched skills and role focus:
        - java-react-fullstack: Both Java and React present
        - backend-distributed: Kafka, Redis, or Distributed Architecture present
        - fullstack-engineer: Generic fullstack with Node/TS/React
        - java-backend: Core Spring Boot / microservices
        """
        combo = f"{title.lower()} {desc.lower()}"
        has_java = any("java" in m.lower() or "spring" in m.lower() for m in core_matched)
        has_react = any("react" in m.lower() for m in core_matched)
        has_dist = len(dist_matched) >= 2 or "kafka" in combo or "distributed" in combo

        if has_java and has_react:
            return "java-react-fullstack"
        if has_dist and has_java:
            return "backend-distributed"
        if has_react and ("node" in combo or "full stack" in combo):
            return "fullstack-engineer"
        return "java-backend"

    def score_job(
        self,
        job: Job,
        role_category: str | None = None,
        llm_score: int | None = None,
    ) -> ScoringBreakdown:
        """
        Compute multi-dimensional score and generate transparent explanation.
        """
        # Parse job fields
        locations = []
        if job.locations:
            try:
                locations = json.loads(job.locations)
            except Exception:
                locations = [job.locations]

        skills = []
        if job.skills:
            try:
                skills = json.loads(job.skills)
            except Exception:
                skills = [job.skills]

        full_text = f"{job.title} {job.description or ''}"

        # 1. Dimension 1: Role Relevance (0 - 25)
        rel_score = score_role_relevance(job.title, job.description or "", role_category=role_category)

        # 2. Dimension 2: Core Tech Stack (0 - 25)
        core_score, core_matched, core_missing = score_core_skills(skills, full_text)

        # 3. Dimension 3: Distributed Systems (0 - 15)
        dist_score, dist_matched = score_distributed_systems(skills, full_text)

        # 4. Dimension 4: Experience Level Match (0 - 15)
        exp_score, exp_risks = score_experience(job.experience_min, job.experience_max, job.title)

        # 5. Dimension 5: Location & Work Mode Fit (0 - 10)
        loc_score, loc_warnings = score_location(locations, job.remote)

        # 6. Dimension 6: Job Quality & Recency (0 - 10)
        qual_score, qual_strengths = score_job_quality(job.source, job.salary_min, job.description or "", job.posted_at)

        # Total deterministic score
        raw_total = rel_score + core_score + dist_score + exp_score + loc_score + qual_score
        total_score = max(0, min(100, raw_total))

        # Determine Fit Category
        fit_category = self.calculate_fit_category(total_score)

        # Determine Recommended Variant
        recommended_variant = self.determine_recommended_variant(
            rel_score, core_matched, dist_matched, job.title, job.description or ""
        )

        # Assemble Strengths
        all_strengths = list(dict.fromkeys(core_matched + dist_matched + qual_strengths))

        # Assemble Gaps
        all_gaps = list(dict.fromkeys(core_missing))

        # Assemble Risks
        all_risks = list(dict.fromkeys(exp_risks + loc_warnings))
        if job.fraud_risk and job.fraud_risk != "none":
            all_risks.append(f"Fraud indicator flagged: {job.fraud_risk}")

        # Assemble Rationale / Reasoning
        reasoning_parts = []
        if rel_score >= 20:
            reasoning_parts.append(f"Strong role alignment ({rel_score}/25) with Shubham's background.")
        if core_score >= 18:
            reasoning_parts.append(f"High tech stack overlap ({core_score}/25) on {', '.join(core_matched[:3])}.")
        if dist_score >= 8:
            reasoning_parts.append(f"Distributed systems requirements ({dist_score}/15) align with TradeX Kafka/Redis experience.")
        if exp_score >= 12:
            reasoning_parts.append("Candidate's ~3.2 years matches the target seniority sweet spot.")
        elif exp_risks:
            reasoning_parts.append(exp_risks[0])
        if loc_score == 10:
            reasoning_parts.append("Ideal location fit (Mumbai or preferred tech hub).")

        reasoning = " ".join(reasoning_parts) or f"Evaluated match score of {total_score}/100 across 6 dimensions."

        return ScoringBreakdown(
            role_relevance=rel_score,
            core_skills=core_score,
            distributed_systems=dist_score,
            experience_fit=exp_score,
            location_score=loc_score,
            job_quality=qual_score,
            total_score=total_score,
            llm_score=llm_score,
            fit_category=fit_category,
            recommended_variant=recommended_variant,
            strengths=all_strengths,
            gaps=all_gaps,
            risks=all_risks,
            reasoning=reasoning,
        )


_scorer_instance: JobScorer | None = None


def get_job_scorer() -> JobScorer:
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = JobScorer()
    return _scorer_instance

