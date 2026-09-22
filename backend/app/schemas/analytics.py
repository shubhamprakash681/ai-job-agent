from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class FunnelStage(BaseModel):
    key: str
    name: str
    count: int
    drop_off_count: int = 0
    drop_off_pct: float = 0.0
    conversion_pct: float = 0.0


class FunnelSummaryRates(BaseModel):
    match_to_application_rate: float = 0.0
    application_to_interview_rate: float = 0.0
    interview_to_offer_rate: float = 0.0
    overall_conversion_rate: float = 0.0


class FunnelResponse(BaseModel):
    stages: List[FunnelStage]
    summary_rates: FunnelSummaryRates


class SourceBreakdown(BaseModel):
    source: str
    jobs_count: int
    applied_count: int = 0
    interviews_count: int = 0
    offers_count: int = 0
    response_rate: float = 0.0
    interview_rate: float = 0.0


class VariantBreakdown(BaseModel):
    variant_id: Optional[int] = None
    variant_name: str
    display_name: str
    applications_count: int = 0
    interviews_count: int = 0
    offers_count: int = 0
    conversion_rate: float = 0.0


class LocationBreakdown(BaseModel):
    location: str
    jobs_count: int
    applications_count: int = 0


class CompanyBreakdown(BaseModel):
    company: str
    total_jobs: int
    applied_count: int = 0
    highest_stage: str = "DISCOVERED"


class BreakdownsResponse(BaseModel):
    sources: List[SourceBreakdown]
    variants: List[VariantBreakdown]
    locations: List[LocationBreakdown]
    companies: List[CompanyBreakdown]


class TimelinePoint(BaseModel):
    date: str
    discovered: int = 0
    applied: int = 0
    interviews: int = 0


class TimelineResponse(BaseModel):
    points: List[TimelinePoint]
    period_days: int


class LLMUsageResponse(BaseModel):
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    estimated_total_cost_usd: float = 0.0
    by_provider: Dict[str, Any] = Field(default_factory=dict)
    by_operation: Dict[str, Any] = Field(default_factory=dict)
    avg_duration_ms: float = 0.0


class LearningInsight(BaseModel):
    type: str  # variant_preference, source_priority, role_focus, observation
    title: str
    recommendation: str
    rationale: str
    impact: str


class LearningLoopResponse(BaseModel):
    insights: List[LearningInsight]
    top_variant: Optional[str] = None
    top_source: Optional[str] = None
    candidate_facts_preserved: bool = True


class DashboardSummaryResponse(BaseModel):
    total_jobs: int
    new_jobs_today: int
    high_priority_jobs: int
    applications_pending: int
    applications_submitted: int
    applications_total: int
    interview_count: int
    response_rate: float
    top_companies: List[str]
    top_cities: List[str]

