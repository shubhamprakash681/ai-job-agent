from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


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


class ApplicationQuestionUpdateRequest(BaseModel):
    final_answer: str
    approved: bool = True


class ApplicationEventResponse(BaseModel):
    id: int
    application_id: int
    event_type: str
    event_data: str | None = None
    created_at: datetime | None = None

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
    submission_evidence: str | None = None
    job_title: str | None = None
    job_company: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ApplicationDetailResponse(ApplicationResponse):
    job_location: str | None = None
    job_description: str | None = None
    resume_version_number: int | None = None
    resume_pdf_path: str | None = None
    questions: list[ApplicationQuestionResponse] = Field(default_factory=list)
    events: list[ApplicationEventResponse] = Field(default_factory=list)
    submission_evidence_parsed: dict[str, Any] | None = None


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    per_page: int
    daily_count: int = 0
    daily_limit: int = 10


class ApplicationApproveRequest(BaseModel):
    user_approved: bool = Field(default=True, description="Explicit human approval confirmation")
    dry_run: bool | None = Field(default=None, description="Override default dry-run behavior")
    notes: str | None = Field(default=None, description="Optional submission note")


class ApplicationRejectRequest(BaseModel):
    reason: str | None = Field(default=None, description="Reason for rejection or withdrawal")


class ApplicationPrepareRequest(BaseModel):
    variant_id: str | None = Field(default=None, description="Target resume variant ID")
    tone: str = Field(default="technical", description="Cover letter tone: technical, executive, or startup")
    custom_instructions: str | None = Field(default=None, description="Custom generation guidance")
