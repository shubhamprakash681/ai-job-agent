from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, Boolean, Float, Text
from app.db.base import Base, TimestampMixin

class CandidateProfile(TimestampMixin, Base):
    __tablename__ = 'candidate_profiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String, nullable=True)
    github_url: Mapped[str | None] = mapped_column(String, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String, nullable=True)
    current_company: Mapped[str | None] = mapped_column(String, nullable=True)
    current_role: Mapped[str | None] = mapped_column(String, nullable=True)
    total_experience_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notice_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_ctc: Mapped[str | None] = mapped_column(String, nullable=True)
    expected_ctc: Mapped[str | None] = mapped_column(String, nullable=True)
    preferred_locations: Mapped[str | None] = mapped_column(Text, nullable=True)
    remote_preference: Mapped[str | None] = mapped_column(String, nullable=True)
    target_roles: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_data: Mapped[str | None] = mapped_column(Text, nullable=True)


class CandidateFact(TimestampMixin, Base):
    __tablename__ = 'candidate_facts'

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey('candidate_profiles.id'))
    fact_id: Mapped[str] = mapped_column(String, unique=True)
    claim: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_for_resume: Mapped[bool] = mapped_column(Boolean, default=True)
    allowed_for_application: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class CandidateEvidence(TimestampMixin, Base):
    __tablename__ = 'candidate_evidence'

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey('candidate_profiles.id'))
    fact_id: Mapped[int] = mapped_column(ForeignKey('candidate_facts.id'))
    evidence_type: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    source_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
