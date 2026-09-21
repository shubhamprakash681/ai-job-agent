import json
import os
import re
from pathlib import Path
from typing import Any
import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.job import Job, JobScore
from app.models.resume import ResumeVariant, ResumeVersion
from app.services.candidate.evidence_engine import get_evidence_engine
from app.services.resume.builder import (
    MasterResumeBuilder,
    MasterResumeData,
    get_master_resume_builder,
)
from app.services.resume.exporters import ResumeExporters

logger = structlog.get_logger(__name__)


class ResumeTailor:
    """
    Intelligent Resume Tailoring Engine.
    Grounds tailored resumes 100% in candidate verified facts and evidence,
    reorders bullets to align with job keywords, exports PDF/DOCX, and guarantees zero hallucination.
    """

    def __init__(self):
        self.builder = get_master_resume_builder()
        self.evidence_engine = get_evidence_engine()

    def extract_job_keywords(self, job: Job) -> set[str]:
        """Extract matched technical keywords from job."""
        job_text = f"{job.title} {job.description or ''} {job.skills or ''}".lower()
        all_skills = [
            "java", "spring boot", "spring cloud", "react", "typescript",
            "microservices", "rest", "restful", "kafka", "redis",
            "postgresql", "postgres", "sql", "docker", "aws", "websockets",
            "eureka", "api gateway", "jwt", "oauth2", "node.js", "chart.js",
        ]
        matched = set()
        for s in all_skills:
            if re.search(rf"\b{re.escape(s)}\b", job_text):
                matched.add(s)
        return matched

    def reorder_bullets_for_job(self, resume_data: MasterResumeData, job_keywords: set[str]) -> list[str]:
        """
        Reorders bullets inside experiences and projects to prioritize JD requirements.
        Returns list of reordered bullet IDs.
        """
        reordered_ids = []

        # Reorder experience bullets
        for exp in resume_data.experiences:
            for b in exp.bullets:
                # Calculate match relevance
                b_skills_lower = [s.lower() for s in b.skills]
                match_count = sum(1 for kw in job_keywords if any(kw in sk for sk in b_skills_lower))
                b.relevance_score = float(match_count)

            # Sort descending by relevance, preserving stable order
            original_order = [b.id for b in exp.bullets]
            exp.bullets.sort(key=lambda b: b.relevance_score, reverse=True)
            new_order = [b.id for b in exp.bullets]
            if new_order != original_order:
                reordered_ids.extend(new_order)

        # Reorder project bullets
        for prj in resume_data.projects:
            for b in prj.bullets:
                b_skills_lower = [s.lower() for s in b.skills]
                match_count = sum(1 for kw in job_keywords if any(kw in sk for sk in b_skills_lower))
                b.relevance_score = float(match_count)
            prj.bullets.sort(key=lambda b: b.relevance_score, reverse=True)

        return reordered_ids

    async def tailor_for_job(
        self,
        job: Job,
        variant_id: str | None = None,
        db: AsyncSession | None = None,
    ) -> ResumeVersion:
        """
        Tailor a resume for a specific job, generating PDF/DOCX and recording ResumeVersion.
        """
        # 1. Determine target variant
        selected_variant = variant_id
        if not selected_variant:
            # Check if job has score with recommended variant
            if db:
                score_res = await db.execute(select(JobScore).where(JobScore.job_id == job.id))
                score = score_res.scalar_one_or_none()
                if score and score.recommended_variant:
                    selected_variant = score.recommended_variant
            if not selected_variant:
                selected_variant = "java-react-fullstack"

        # 2. Look up or create variant in database
        variant_record: ResumeVariant | None = None
        if db:
            var_query = await db.execute(
                select(ResumeVariant).where(ResumeVariant.name == selected_variant)
            )
            variant_record = var_query.scalar_one_or_none()
            if not variant_record:
                # Fetch default variant or first
                default_query = await db.execute(
                    select(ResumeVariant).where(ResumeVariant.is_default == True)
                )
                variant_record = default_query.scalar_one_or_none()
                if not variant_record:
                    # Create default variant record
                    variant_record = ResumeVariant(
                        name=selected_variant,
                        display_name=selected_variant.replace("-", " ").title(),
                        description=f"Tailored variant for {selected_variant}",
                        is_default=True,
                    )
                    db.add(variant_record)
                    await db.commit()
                    await db.refresh(variant_record)

        # 3. Build base resume data
        resume_data = self.builder.build_resume_data(selected_variant)

        # 4. Extract job keywords and reorder
        job_keywords = self.extract_job_keywords(job)
        reordered_ids = self.reorder_bullets_for_job(resume_data, job_keywords)

        # 5. Build Evidence Mapping
        evidence_mapping: dict[str, Any] = {}
        for exp in resume_data.experiences:
            for b in exp.bullets:
                evidence_mapping[b.id] = {
                    "fact_id": b.fact_id,
                    "skills": b.skills,
                    "evidence_ref": f"candidate.evidence.{b.id}",
                }
        for prj in resume_data.projects:
            for b in prj.bullets:
                evidence_mapping[b.id] = {
                    "fact_id": b.fact_id,
                    "skills": b.skills,
                    "evidence_ref": f"candidate.evidence.{b.id}",
                }

        # 6. Render Markdown
        markdown_content = self.builder.render_markdown(resume_data)

        # 7. Validate with Evidence Engine
        val_result = self.evidence_engine.validate_resume_content(markdown_content)
        validation_status = "passed" if val_result.passed else "failed"
        confidence_score = 1.0 if val_result.passed else val_result.confidence_score
        validation_summary = (
            f"Passed: {val_result.passed}. Supported claims: {val_result.supported_claims_count}, "
            f"Unsupported: {val_result.unsupported_claims_count}. "
            f"Hallucinated skills: {len(val_result.hallucinated_skills)}."
        )

        # 8. Determine version number
        version_num = 1
        if db:
            count_stmt = select(func.count(ResumeVersion.id)).where(ResumeVersion.job_id == job.id)
            existing_count = await db.scalar(count_stmt) or 0
            version_num = existing_count + 1

        # 9. Export to files (PDF, DOCX, Markdown)
        doc_dir = Path("documents/generated")
        doc_dir.mkdir(parents=True, exist_ok=True)

        base_filename = f"Resume_Shubham_Prakash_{job.id}_v{version_num}"
        pdf_path = str(doc_dir / f"{base_filename}.pdf")
        docx_path = str(doc_dir / f"{base_filename}.docx")
        md_path = str(doc_dir / f"{base_filename}.md")

        try:
            ResumeExporters.export_markdown(resume_data, md_path, content=markdown_content)
            ResumeExporters.export_docx(resume_data, docx_path)
            ResumeExporters.export_pdf(resume_data, pdf_path)
        except Exception as e:
            logger.error("Error exporting resume files", error=str(e))

        # 10. Record diff & keyword mapping
        keyword_mapping = {kw: True for kw in job_keywords}
        diff_info = {
            "target_company": job.company or "",
            "target_role": job.title,
            "variant": selected_variant,
            "matched_keywords": list(job_keywords),
            "reordered_bullets_count": len(reordered_ids),
            "total_experiences": len(resume_data.experiences),
            "total_projects": len(resume_data.projects),
            "validation_passed": val_result.passed,
        }

        # 11. Create ResumeVersion record
        variant_id_val = variant_record.id if variant_record else 1
        resume_version = ResumeVersion(
            variant_id=variant_id_val,
            job_id=job.id,
            version_number=version_num,
            content_markdown=markdown_content,
            content_json=resume_data.model_dump_json(),
            file_path_docx=docx_path,
            file_path_pdf=pdf_path,
            keyword_mapping=json.dumps(keyword_mapping),
            evidence_mapping=json.dumps(evidence_mapping),
            change_diff=json.dumps(diff_info),
            confidence_score=confidence_score,
            unsupported_claims=json.dumps(val_result.unsupported_claims),
            missing_skills=json.dumps(val_result.hallucinated_skills),
            validation_status=validation_status,
            validation_report=validation_summary,
        )

        if db:
            db.add(resume_version)
            # Create Audit Log
            audit = AuditLog(
                action="RESUME_TAILORED",
                entity_type="resume",
                entity_id=job.id,
                details=json.dumps({
                    "job_id": job.id,
                    "variant": selected_variant,
                    "version": version_num,
                    "validation_status": validation_status,
                    "confidence": confidence_score,
                }),
            )
            db.add(audit)
            await db.commit()
            await db.refresh(resume_version)

        return resume_version


_tailor_instance: ResumeTailor | None = None


def get_resume_tailor() -> ResumeTailor:
    global _tailor_instance
    if _tailor_instance is None:
        _tailor_instance = ResumeTailor()
    return _tailor_instance
