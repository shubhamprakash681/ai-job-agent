import json
from typing import Any
from pydantic import BaseModel, Field

from app.services.candidate.kb_loader import get_candidate_kb


class ResumeBullet(BaseModel):
    id: str
    fact_id: str
    text: str
    skills: list[str] = Field(default_factory=list)
    relevance_score: float = 0.0


class ResumeExperienceItem(BaseModel):
    id: str
    company: str
    role: str
    location: str
    period: str
    bullets: list[ResumeBullet] = Field(default_factory=list)


class ResumeProjectItem(BaseModel):
    id: str
    name: str
    title: str
    summary: str
    technologies: list[str] = Field(default_factory=list)
    bullets: list[ResumeBullet] = Field(default_factory=list)


class ResumeEducationItem(BaseModel):
    degree: str
    institution: str
    period: str
    grade: str


class MasterResumeData(BaseModel):
    candidate_name: str = "Shubham Prakash"
    location: str = "Mumbai, India"
    email: str = "shubhamprakash681@gmail.com"
    phone: str = "+91-9955551381"
    portfolio_url: str = "https://www.shubhamprakash681.in/"
    linkedin_url: str = "https://linkedin.com/in/shubhamprakash681"
    github_url: str = "https://github.com/shubhamprakash681"
    variant_id: str = "java-react-fullstack"
    variant_name: str = "Java + React Full Stack"
    tagline: str = "Full Stack Engineer | Java, Spring Boot & React Ecosystem"
    summary: str = ""
    priority_skills: list[str] = Field(default_factory=list)
    categorized_skills: dict[str, list[str]] = Field(default_factory=dict)
    experiences: list[ResumeExperienceItem] = Field(default_factory=list)
    projects: list[ResumeProjectItem] = Field(default_factory=list)
    education: list[ResumeEducationItem] = Field(default_factory=list)


class MasterResumeBuilder:
    """
    Builds strongly-typed resume data models from verified candidate knowledge base.
    Respects variant positioning, priority skills, and bullet point ordering.
    """

    def __init__(self):
        self.kb = get_candidate_kb()

    def get_variant_config(self, variant_id: str | None = None) -> Any:
        v_id = (variant_id or "java-react-fullstack").lower().replace("_", "-")
        for v in self.kb.variants:
            if v.id == v_id or v_id in v.id:
                return v
        return self.kb.variants[0]

    def build_resume_data(self, variant_id: str | None = None) -> MasterResumeData:
        var_cfg = self.get_variant_config(variant_id)
        prof = self.kb.profile

        # Categorized skills
        categorized: dict[str, list[str]] = {
            cat.name: [s.name for s in cat.skills]
            for cat in self.kb.skill_categories
        }

        # Build Experiences
        experiences: list[ResumeExperienceItem] = []
        for exp in self.kb.experiences:
            period = f"{exp.start_date} – {'Present' if exp.is_current else exp.end_date}"
            bullets = [
                ResumeBullet(
                    id=bp.id,
                    fact_id=bp.fact_id,
                    text=bp.text,
                    skills=bp.skills,
                )
                for bp in exp.bullet_points
            ]
            experiences.append(
                ResumeExperienceItem(
                    id=exp.id,
                    company=exp.company,
                    role=exp.role,
                    location=exp.location,
                    period=period,
                    bullets=bullets,
                )
            )

        # Build Projects (Primary & Secondary per variant)
        projects: list[ResumeProjectItem] = []
        for prj in self.kb.projects:
            bullets = [
                ResumeBullet(
                    id=bp.id,
                    fact_id=bp.fact_id,
                    text=bp.text,
                    skills=bp.skills,
                )
                for bp in prj.bullet_points
            ]
            projects.append(
                ResumeProjectItem(
                    id=prj.id,
                    name=prj.name,
                    title=prj.title,
                    summary=prj.summary.strip(),
                    technologies=prj.technologies,
                    bullets=bullets,
                )
            )

        # Build Education
        education = [
            ResumeEducationItem(
                degree=f"{edu.degree} in {edu.field_of_study}",
                institution=f"{edu.institution}, {edu.location}",
                period=f"{edu.start_date[:4]} – {edu.end_date[:4]}",
                grade=f"CGPA: {edu.gpa.score}/10" if edu.gpa else "",
            )
            for edu in self.kb.education
        ]

        # Compose Summary
        full_summary = f"{var_cfg.tagline}. ~3.2 years of professional software development experience. {var_cfg.summary_emphasis}"

        return MasterResumeData(
            candidate_name=prof.full_name,
            location=prof.location,
            email=prof.email,
            phone=prof.phone,
            portfolio_url=prof.links.portfolio or "https://www.shubhamprakash681.in/",
            linkedin_url=prof.links.linkedin or "https://linkedin.com/in/shubhamprakash681",
            github_url=prof.links.github or "https://github.com/shubhamprakash681",
            variant_id=var_cfg.id,
            variant_name=var_cfg.name,
            tagline=var_cfg.tagline,
            summary=full_summary,
            priority_skills=var_cfg.priority_skills,
            categorized_skills=categorized,
            experiences=experiences,
            projects=projects,
            education=education,
        )

    def render_markdown(self, data: MasterResumeData) -> str:
        """
        Renders clean, ATS-compliant markdown with embedded evidence comments.
        """
        lines = [
            f"# {data.candidate_name}",
            f"{data.location} | {data.phone} | [{data.email}](mailto:{data.email}) | [Portfolio]({data.portfolio_url}) | [LinkedIn]({data.linkedin_url}) | [GitHub]({data.github_url})",
            "",
            "## Professional Summary",
            data.summary,
            "",
            "## Technical Skills",
        ]

        # Format skills
        lines.append(f"- **Priority Core Focus**: {', '.join(data.priority_skills)}")
        for cat, skills in data.categorized_skills.items():
            lines.append(f"- **{cat}**: {', '.join(skills)}")

        lines.extend(["", "## Professional Experience"])
        for exp in data.experiences:
            lines.append(f"### {exp.role} — **{exp.company}**")
            lines.append(f"*{exp.location} | {exp.period}*")
            for b in exp.bullets:
                lines.append(f"- {b.text} <!-- evidence:{b.fact_id} -->")
            lines.append("")

        lines.append("## Key Projects")
        for prj in data.projects:
            lines.append(f"### {prj.name} — *{prj.title}*")
            lines.append(f"**Technologies**: {', '.join(prj.technologies)}")
            for b in prj.bullets:
                lines.append(f"- {b.text} <!-- evidence:{b.fact_id} -->")
            lines.append("")

        lines.append("## Education")
        for edu in data.education:
            lines.append(f"### {edu.degree}")
            lines.append(f"*{edu.institution} | {edu.period} | {edu.grade}*")

        return "\n".join(lines)


_builder_instance: MasterResumeBuilder | None = None


def get_master_resume_builder() -> MasterResumeBuilder:
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = MasterResumeBuilder()
    return _builder_instance
