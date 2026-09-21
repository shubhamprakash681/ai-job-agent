from datetime import datetime
from pydantic import BaseModel, Field


class ResumeVariantResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: str | None = None
    is_default: bool = False
    priority_skills: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ResumeVersionResponse(BaseModel):
    id: int
    variant_id: int
    job_id: int | None = None
    version_number: int
    content_markdown: str | None = None
    content_json: str | None = None
    file_path_docx: str | None = None
    file_path_pdf: str | None = None
    keyword_mapping: str | None = None
    evidence_mapping: str | None = None
    change_diff: str | None = None
    confidence_score: float | None = None
    unsupported_claims: str | None = None
    missing_skills: str | None = None
    validation_status: str | None = None
    validation_report: str | None = None
    job_title: str | None = None
    job_company: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ResumeVersionListResponse(BaseModel):
    items: list[ResumeVersionResponse]
    total: int
    page: int
    per_page: int
