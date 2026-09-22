from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class FollowupItem(BaseModel):
    application_id: int
    job_id: int
    job_title: str
    company: str
    applied_at: datetime | None = None
    days_since_applied: int
    status: str
    followup_type: str  # 7_DAY, 14_DAY, 30_DAY_STALE, RECENT
    suggested_action: str


class FollowupListResponse(BaseModel):
    items: list[FollowupItem]
    total_needing_followup: int
    seven_day_count: int
    fourteen_day_count: int
    stale_count: int


class FollowupDraftRequest(BaseModel):
    tone: str = "professional"  # professional, courteous, concise
    recipient_name: str | None = None
    recipient_email: str | None = None
    custom_instructions: str | None = None


class FollowupDraftResponse(BaseModel):
    application_id: int
    company: str
    job_title: str
    recipient_name: str | None = None
    recipient_email: str | None = None
    subject: str
    body: str
    days_since_applied: int
    tone: str
    created_at: datetime


class EmailParseRequest(BaseModel):
    raw_email_text: str
    sender: str | None = None
    subject: str | None = None


class EmailParseResponse(BaseModel):
    classification: str  # INTERVIEW_INVITATION, ASSESSMENT_REQUEST, REJECTION, APPLICATION_RECEIVED, OFFER, GENERAL_INQUIRY, UNKNOWN
    confidence: float
    company_extracted: str | None = None
    role_extracted: str | None = None
    key_details: dict[str, Any] = Field(default_factory=dict)
    suggested_application_id: int | None = None
    suggested_status: str | None = None
    match_rationale: str | None = None


class EmailApplyMatchRequest(BaseModel):
    application_id: int
    classification: str
    new_status: str | None = None
    notes: str | None = None
    event_metadata: dict[str, Any] | None = None


class ApplicationStatusUpdateRequest(BaseModel):
    status: str
    reason: str | None = None
    notes: str | None = None
    interview_details: dict[str, Any] | None = None
    offer_details: dict[str, Any] | None = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    message: str
    read: bool
    action_url: str | None = None
    data: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int
    total: int

