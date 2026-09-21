from datetime import datetime

from pydantic import BaseModel


class JobScoreResponse(BaseModel):
    id: int
    job_id: int
    total_score: int
    role_relevance: int = 0
    core_skills: int = 0
    distributed_systems: int = 0
    experience_fit: int = 0
    location_score: int = 0
    job_quality: int = 0
    llm_score: int | None = None
    fit_category: str | None = None
    recommended_variant: str | None = None

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    id: int
    source: str
    source_job_id: str | None = None
    url: str | None = None
    canonical_url: str | None = None
    title: str
    company: str | None = None
    locations: str | None = None
    remote: bool = False
    experience_min: float | None = None
    experience_max: float | None = None
    employment_type: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    currency: str = "INR"
    description: str | None = None
    skills: str | None = None
    required_skills: str | None = None
    preferred_skills: str | None = None
    posted_at: datetime | None = None
    application_url: str | None = None
    source_type: str | None = None
    status: str = "active"
    fraud_risk: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    per_page: int


class JobFilters(BaseModel):
    source: str | None = None
    status: str | None = None
    min_score: int | None = None
    location: str | None = None
    search: str | None = None
