from datetime import datetime

from pydantic import BaseModel


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
    preferred_locations: str | None = None
    remote_preference: str | None = None
    target_roles: str | None = None
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

    model_config = {"from_attributes": True}
