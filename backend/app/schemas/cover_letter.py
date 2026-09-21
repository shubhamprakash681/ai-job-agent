from pydantic import BaseModel, Field


class CoverLetterGenerateRequest(BaseModel):
    tone: str = Field(default="technical", description="Tone of the cover letter: technical, executive, or startup")
    custom_instructions: str | None = Field(default=None, description="Optional custom instructions to guide generation")


class CoverLetterUpdateRequest(BaseModel):
    content_markdown: str = Field(..., description="Updated Markdown content of the cover letter")


class CoverLetterResponse(BaseModel):
    job_id: int
    company: str
    title: str
    content_markdown: str
    tone: str
    word_count: int
    file_path_pdf: str | None = None
    file_path_md: str | None = None
    validation_passed: bool
    confidence_score: float
    warnings: list[str] = Field(default_factory=list)
    verified_skills: list[str] = Field(default_factory=list)
    generator_source: str = "template_fallback"

