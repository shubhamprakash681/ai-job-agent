from datetime import datetime

from pydantic import BaseModel


class ApplicationQuestionResponse(BaseModel):
    id: int
    application_id: int
    question: str
    proposed_answer: str | None = None
    final_answer: str | None = None
    answer_source: str | None = None
    confidence: float = 0.0
    requires_human: bool = True
    approved: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    status: str
    resume_version_id: int | None = None
    cover_letter: str | None = None
    application_url: str | None = None
    applied_at: datetime | None = None
    job_score: int | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    per_page: int
