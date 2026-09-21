import json
import re
from typing import Any
from pydantic import BaseModel, Field

from app.models.job import Job
from app.services.candidate.kb_loader import get_candidate_kb


class PreFilterResult(BaseModel):
    passed: bool
    rejection_reason: str | None = None
    warnings: list[str] = Field(default_factory=list)
    flags: dict[str, Any] = Field(default_factory=dict)


EXCLUDED_ROLE_KEYWORDS = [
    r"\bphp\b",
    r"\bwordpress\b",
    r"\bcobol\b",
    r"\bmainframe\b",
    r"\bsalesforce\s+(?:admin|developer)\b",
    r"\bhelp\s*desk\b",
    r"\btech\s*support\b",
    r"\btelecom\s*technician\b",
    r"\bdata\s*entry\b",
    r"\bcontent\s*writer\b",
    r"\bdigital\s*marketing\b",
]


def run_prefilters(job: Job) -> PreFilterResult:
    """
    Apply fast, zero-cost deterministic filters on a job before running LLM classification.
    Filters out extreme tenure mismatches, scam risks, and completely unrelated domains.
    """
    warnings: list[str] = []
    flags: dict[str, Any] = {}

    title_lower = (job.title or "").lower()
    desc_lower = (job.description or "").lower()

    # 1. Fraud Risk Check
    if job.fraud_risk == "high":
        return PreFilterResult(
            passed=False,
            rejection_reason="High fraud risk indicators detected in posting.",
            flags={"fraud_risk": "high"},
        )

    # 2. Excluded Role Keywords in Title
    for pattern in EXCLUDED_ROLE_KEYWORDS:
        if re.search(pattern, title_lower):
            return PreFilterResult(
                passed=False,
                rejection_reason=f"Role domain does not align with software engineering profile: matched pattern '{pattern}'.",
                flags={"excluded_keyword": pattern},
            )

    # 3. Experience Filter (Candidate has ~3.2 years)
    if job.experience_min is not None and job.experience_min > 5.5:
        return PreFilterResult(
            passed=False,
            rejection_reason=f"Experience requirement ({job.experience_min}+ yrs) exceeds candidate's ~3.2 yrs.",
            flags={"experience_min": job.experience_min, "candidate_years": 3.2},
        )

    if job.experience_min is not None and job.experience_min > 4.5:
        warnings.append(f"Borderline experience requirement ({job.experience_min} yrs).")

    # 4. Location Check
    try:
        kb = get_candidate_kb()
        preferred_cities = [c.lower() for c in kb.profile.preferences.preferred_locations]
    except Exception:
        preferred_cities = ["mumbai", "bengaluru", "bangalore", "pune", "hyderabad", "remote"]

    locations_list = []
    if job.locations:
        try:
            locations_list = [l.lower() for l in json.loads(job.locations)]
        except Exception:
            locations_list = [job.locations.lower()]

    if locations_list and not job.remote:
        has_preferred = any(
            any(pref in loc for pref in preferred_cities)
            for loc in locations_list
        )
        if not has_preferred:
            warnings.append(f"Job locations ({', '.join(locations_list)}) outside top preferred cities.")

    return PreFilterResult(
        passed=True,
        rejection_reason=None,
        warnings=warnings,
        flags=flags,
    )

