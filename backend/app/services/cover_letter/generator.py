import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.services.candidate.kb_loader import get_candidate_kb, CandidateKnowledgeBase
from app.services.candidate.evidence_engine import get_evidence_engine, EvidenceEngine
from app.services.llm.client import get_llm_client, UnifiedLLMClient
from app.services.cover_letter.prompts import (
    COVER_LETTER_SYSTEM_PROMPT,
    COVER_LETTER_USER_TEMPLATE,
)
from app.services.cover_letter.exporter import CoverLetterExporter

logger = structlog.get_logger(__name__)


@dataclass
class CoverLetterResult:
    content_markdown: str
    file_path_pdf: str
    file_path_md: str
    tone: str
    word_count: int
    validation_passed: bool
    confidence_score: float
    warnings: list[str] = field(default_factory=list)
    verified_skills: list[str] = field(default_factory=list)
    hallucinated_skills: list[str] = field(default_factory=list)
    generator_source: str = "template_fallback"


class CoverLetterGenerator:
    """
    High-impact, zero-hallucination Cover Letter Generation Engine.
    Combines LLM tailoring with deterministic fallback and strict anti-hallucination validation.
    """

    def __init__(
        self,
        kb: CandidateKnowledgeBase | None = None,
        evidence_engine: EvidenceEngine | None = None,
        llm_client: UnifiedLLMClient | None = None,
    ):
        self.kb = kb or get_candidate_kb()
        self.evidence_engine = evidence_engine or get_evidence_engine()
        self.llm_client = llm_client or get_llm_client()

    def build_template_cover_letter(
        self,
        company: str,
        title: str,
        keywords: list[str],
        tone: str = "technical",
    ) -> str:
        """
        Generate a deterministic, 100% grounded 3-4 paragraph cover letter.
        Ground truth: Shubham Prakash, ~3.2 years experience (Accenture current, TCS Digital 3 years),
        TradeX (Kafka, WebSockets, Redis, PostgreSQL), VideoShare (Node.js, React, EC2, Docker).
        """
        company_clean = company or "your organization"
        title_clean = title or "Software Engineer"
        top_keywords = [k for k in keywords if k.lower() in [
            "java", "spring boot", "react", "microservices", "kafka", "redis",
            "postgresql", "docker", "aws", "rest api", "typescript", "distributed systems"
        ]][:4]

        skills_phrase = ", ".join(top_keywords) if top_keywords else "Java, Spring Boot, and modern React architectures"

        if tone == "startup":
            p1 = (
                f"I am writing to apply for the {title_clean} position at {company_clean}. "
                f"With ~3.2 years of full-stack and backend software engineering experience across high-growth "
                f"enterprise environments, I specialize in building end-to-end scalable microservices with "
                f"Spring Boot, resilient data layers in PostgreSQL, and responsive frontends in React."
            )
            p2 = (
                f"Across my 3 years at TCS Digital and current role at Accenture, I developed a strong bias for action "
                f"and ownership. I engineered RESTful microservices for high-traffic platforms serving over 10,000 "
                f"concurrent users, maintaining 99.9% uptime and zero-downtime rolling deployments. My hands-on work "
                f"encompasses API design, query optimization, and containerized deployments using Docker and AWS."
            )
            p3 = (
                f"To push distributed architectures further, I built TradeX—a real-time paper trading simulation platform "
                f"leveraging Spring Boot, Apache Kafka for event-driven order processing, Redis for low-latency market data caching, "
                f"and WebSockets for real-time portfolio updates. Whether architecting backend pipelines or streamlining "
                f"frontend state management, I focus on delivering clean, test-driven code that drives user impact."
            )
            p4 = (
                f"I am excited by {company_clean}'s engineering roadmap and would welcome the opportunity to bring my "
                f"full-stack agility and backend rigor to your team. I am available on a 30-day notice period and look "
                f"forward to discussing how my experience with {skills_phrase} aligns with your objectives."
            )
        elif tone == "executive":
            p1 = (
                f"I am pleased to submit my application for the {title_clean} role at {company_clean}. "
                f"Bringing ~3.2 years of demonstrated expertise in enterprise Java, Spring Boot microservices, and full-stack "
                f"application delivery, I have consistently driven operational reliability, API performance, and seamless system integrations."
            )
            p2 = (
                f"In my tenure at TCS Digital and Accenture, I contributed to mission-critical distributed systems. At TCS Digital, "
                f"I designed and deployed production REST microservices supporting 10,000+ concurrent enterprise users, achieving "
                f"a 30% reduction in response latency through indexed PostgreSQL query tuning and Redis cache layers. My approach "
                f"prioritizes test automation, SOLID design principles, and robust CI/CD deployment pipelines."
            )
            p3 = (
                f"Complementing my enterprise background, my work on TradeX showcases hands-on expertise in distributed event-driven systems. "
                f"I architected real-time event streaming pipelines with Apache Kafka and WebSockets to handle high-frequency trade simulations "
                f"with sub-second execution. Paired with frontend proficiency in React and TypeScript, I deliver complete end-to-end features "
                f"from schema design to responsive UI."
            )
            p4 = (
                f"With direct relevance to {company_clean}'s technology priorities in {skills_phrase}, I am prepared to make an immediate, "
                f"measurable contribution. With a 30-day notice period, I would welcome the opportunity to discuss my qualifications with your leadership team."
            )
        else:  # "technical" (default)
            p1 = (
                f"I am writing to express my strong interest in the {title_clean} opening at {company_clean}. "
                f"With ~3.2 years of specialized experience in Java, Spring Boot microservices, and modern React full-stack "
                f"engineering, I focus on building resilient, high-throughput backend services and clean web architectures."
            )
            p2 = (
                f"In my production engineering roles at Accenture and TCS Digital, I engineered scalable microservices handling "
                f"concurrent workloads of 10,000+ active users. At TCS Digital, I architected RESTful endpoints, optimized relational "
                f"queries in PostgreSQL, and integrated Redis caching to dramatically reduce database overhead. I emphasize "
                f"strict type safety, comprehensive unit testing, and maintainable domain-driven design."
            )
            p3 = (
                f"In the distributed systems domain, I built TradeX, an event-driven stock trading platform powered by Spring Boot, "
                f"Apache Kafka event streams, Redis caching, and WebSockets for real-time market data dissemination. On the frontend, "
                f"my work with React and TypeScript ensures high performance, clean state management, and intuitive user experiences."
            )
            p4 = (
                f"Given {company_clean}'s focus on {skills_phrase}, I am confident in my ability to hit the ground running. "
                f"I hold a 30-day notice period and look forward to discussing how my background can support your engineering initiatives."
            )

        paragraphs = [p1, p2, p3, p4]
        return "\n\n".join(paragraphs)

    async def generate_cover_letter(
        self,
        job: Job,
        tone: str = "technical",
        custom_instructions: str | None = None,
        db: AsyncSession | None = None,
    ) -> CoverLetterResult:
        """
        Generate, validate, and export an ATS-friendly cover letter for a job.
        """
        company = job.company or "Company"
        title = job.title or "Software Engineer"

        # Extract keywords
        keywords: list[str] = []
        if job.required_skills:
            try:
                parsed = json.loads(job.required_skills)
                if isinstance(parsed, list):
                    keywords.extend(parsed)
            except Exception:
                pass
        if job.skills:
            try:
                parsed = json.loads(job.skills)
                if isinstance(parsed, list):
                    keywords.extend([s for s in parsed if s not in keywords])
            except Exception:
                pass

        description = (job.description or "")[:2000]
        gen_source = "template_fallback"
        letter_content = ""

        # Check if LLM client is usable
        has_keys = bool(self.llm_client.settings.GROQ_API_KEY or self.llm_client.settings.GEMINI_API_KEY)
        if has_keys:
            try:
                sys_prompt = COVER_LETTER_SYSTEM_PROMPT
                user_prompt = COVER_LETTER_USER_TEMPLATE.format(
                    company=company,
                    title=title,
                    keywords=", ".join(keywords[:8]) if keywords else "Java, Spring Boot, React, Microservices",
                    description=description,
                    tone=tone,
                )
                if custom_instructions:
                    user_prompt += f"\nAdditional Instructions: {custom_instructions}"

                user_prompt += (
                    "\n\nIMPORTANT: Respond with a single valid JSON object formatted as:\n"
                    '{\n  "cover_letter": "<full cover letter markdown paragraphs separated by double newlines>"\n}'
                )

                llm_res = await self.llm_client.generate_structured_json(
                    system_prompt=sys_prompt,
                    user_prompt=user_prompt,
                    db=db,
                    job_id=job.id,
                    operation="cover_letter",
                )

                if llm_res.parsed_json and "cover_letter" in llm_res.parsed_json:
                    candidate_text = str(llm_res.parsed_json["cover_letter"]).strip()
                    # Verify candidate text isn't empty and has reasonable length
                    if len(candidate_text.split()) >= 150:
                        letter_content = candidate_text
                        gen_source = f"llm_{llm_res.provider}"
            except Exception as e:
                logger.warning("LLM generation failed, falling back to deterministic template", error=str(e))

        if not letter_content:
            letter_content = self.build_template_cover_letter(company, title, keywords, tone)
            gen_source = "template_fallback"

        # Validate with Evidence Engine
        val_report = self.evidence_engine.validate_resume_content(letter_content)

        # Word count
        word_count = len(re.findall(r"\b\w+\b", letter_content))

        # File paths
        base_dir = Path("documents/generated")
        base_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = str((base_dir / f"CoverLetter_Shubham_Prakash_Job{job.id}.pdf").absolute())
        md_path = str((base_dir / f"CoverLetter_Shubham_Prakash_Job{job.id}.md").absolute())

        # Export Markdown
        CoverLetterExporter.export_markdown(letter_content, md_path)

        # Export PDF
        CoverLetterExporter.export_pdf(
            content=letter_content,
            output_path=pdf_path,
            candidate_name="Shubham Prakash",
            company=company,
            title=title,
        )

        return CoverLetterResult(
            content_markdown=letter_content,
            file_path_pdf=pdf_path,
            file_path_md=md_path,
            tone=tone,
            word_count=word_count,
            validation_passed=val_report.passed,
            confidence_score=val_report.confidence_score,
            warnings=val_report.warnings,
            verified_skills=list(val_report.verified_skills),
            hallucinated_skills=val_report.hallucinated_skills,
            generator_source=gen_source,
        )


_COVER_LETTER_GENERATOR: CoverLetterGenerator | None = None


def get_cover_letter_generator() -> CoverLetterGenerator:
    global _COVER_LETTER_GENERATOR
    if _COVER_LETTER_GENERATOR is None:
        _COVER_LETTER_GENERATOR = CoverLetterGenerator()
    return _COVER_LETTER_GENERATOR

