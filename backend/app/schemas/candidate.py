from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class CandidateProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    current_company: str | None = None
    current_role: str | None = None
    total_experience_months: int | None = None
    notice_period_days: int | None = None
    current_ctc: str | None = None
    expected_ctc: str | None = None
    preferred_locations: str | None = None
    remote_preference: str | None = None
    target_roles: str | None = None
    profile_data: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class CandidateProfileUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    current_company: str | None = None
    current_role: str | None = None
    total_experience_months: int | None = None
    notice_period_days: int | None = None
    current_ctc: str | None = None
    expected_ctc: str | None = None
    preferred_locations: str | None = None
    remote_preference: str | None = None
    target_roles: str | None = None


class CandidateFactResponse(BaseModel):
    id: int
    fact_id: str
    claim: str
    category: str
    source: str
    verified: bool
    allowed_for_resume: bool
    allowed_for_application: bool
    metadata_json: str | None = None

    model_config = {"from_attributes": True}


class ClaimValidationRequest(BaseModel):
    claim: str


class ClaimValidationResponse(BaseModel):
    is_supported: bool
    confidence: float
    claim: str
    conflicts: list[str] = Field(default_factory=list)
    reasoning: str
    supporting_evidence: list[dict[str, Any]] = Field(default_factory=list)


class ResumeValidationRequest(BaseModel):
    content: str


class ResumeValidationResponse(BaseModel):
    passed: bool
    confidence_score: float
    supported_claims_count: int
    unsupported_claims_count: int
    supported_claims: list[dict[str, Any]] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    hallucinated_skills: list[str] = Field(default_factory=list)
    verified_skills: list[str] = Field(default_factory=list)
    metric_discrepancies: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class CandidateSyncResponse(BaseModel):
    status: str
    message: str
    facts_count: int
    candidate_name: str
