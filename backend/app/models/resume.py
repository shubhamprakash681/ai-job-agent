from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, Boolean, Float, Text
from app.db.base import Base, TimestampMixin

class ResumeVariant(TimestampMixin, Base):
    __tablename__ = 'resume_variants'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    display_name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    priority_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class ResumeVersion(TimestampMixin, Base):
    __tablename__ = 'resume_versions'

    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey('resume_variants.id'))
    job_id: Mapped[int | None] = mapped_column(ForeignKey('jobs.id'), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer)
    content_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path_docx: Mapped[str | None] = mapped_column(String, nullable=True)
    file_path_pdf: Mapped[str | None] = mapped_column(String, nullable=True)
    keyword_mapping: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_mapping: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_diff: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    unsupported_claims: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_status: Mapped[str | None] = mapped_column(String, nullable=True)
    validation_report: Mapped[str | None] = mapped_column(Text, nullable=True)
