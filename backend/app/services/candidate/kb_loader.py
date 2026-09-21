import os
from functools import lru_cache
from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field

from app.config import get_settings


class CandidateLinks(BaseModel):
    portfolio: str
    github: str
    linkedin: str


class CurrentEmployment(BaseModel):
    company: str
    role: str
    start_date: str
    is_current: bool = True
    location: str


class CandidatePreferences(BaseModel):
    total_experience_years: float = 3.2
    total_experience_months: int = 39
    notice_period_days: int = 30
    current_ctc: str
    expected_ctc: str
    target_roles: list[str]
    preferred_locations: list[str]
    remote_preference: str = "hybrid_or_remote"
    willing_to_relocate: bool = True


class CandidateProfileData(BaseModel):
    full_name: str
    first_name: str
    last_name: str
    title: str
    email: str
    phone: str
    location: str
    citizenship: str = "India"
    work_authorization: str = "India (Citizen)"
    links: CandidateLinks
    summary: str
    current_employment: CurrentEmployment
    preferences: CandidatePreferences


class MetricItem(BaseModel):
    name: str
    value: int | float
    unit: str | None = None
    description: str


class ExperienceBullet(BaseModel):
    id: str
    fact_id: str
    text: str
    metrics: list[MetricItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    verified: bool = True


class ExperienceItem(BaseModel):
    id: str
    company: str
    role: str
    location: str
    start_date: str
    end_date: str | None = None
    is_current: bool = False
    employment_type: str = "full_time"
    summary: str
    technologies: list[str] = Field(default_factory=list)
    bullet_points: list[ExperienceBullet] = Field(default_factory=list)


class ProjectBullet(BaseModel):
    id: str
    fact_id: str
    text: str
    skills: list[str] = Field(default_factory=list)
    verified: bool = True


class ProjectItem(BaseModel):
    id: str
    name: str
    title: str
    start_date: str
    end_date: str | None = None
    is_ongoing: bool = False
    status: str = "completed"
    badges: list[str] = Field(default_factory=list)
    summary: str
    architecture: dict[str, Any] = Field(default_factory=dict)
    features: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    metrics: list[MetricItem] = Field(default_factory=list)
    bullet_points: list[ProjectBullet] = Field(default_factory=list)


class SkillItem(BaseModel):
    name: str
    proficiency: str = "intermediate"
    years_experience: float = 1.0
    verified: bool = True
    evidence_source: str
    primary: bool = False


class SkillCategory(BaseModel):
    id: str
    name: str
    skills: list[SkillItem] = Field(default_factory=list)


class EducationGPA(BaseModel):
    score: float
    scale: float = 10.0
    display: str


class EducationItem(BaseModel):
    id: str
    institution: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: str
    is_completed: bool = True
    gpa: EducationGPA
    location: str
    highlights: list[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    id: str
    name: str
    issuer: str
    issue_date: str
    description: str


class ResumeVariantData(BaseModel):
    id: str
    name: str
    is_default: bool = False
    target_roles: list[str]
    tagline: str
    summary_emphasis: str
    priority_skills: list[str]
    bullet_point_ordering: list[str]
    primary_project: str
    secondary_project: str


class AtomicFact(BaseModel):
    fact_id: str
    category: str
    claim: str
    source: str
    verified: bool = True
    allowed_for_resume: bool = True
    allowed_for_application: bool = True
    keywords: list[str] = Field(default_factory=list)
    evidence_type: str = "employment"
    source_reference: str = ""
    metrics: list[MetricItem] = Field(default_factory=list)


class CandidateKnowledgeBase(BaseModel):
    profile: CandidateProfileData
    experiences: list[ExperienceItem]
    projects: list[ProjectItem]
    skill_categories: list[SkillCategory]
    education: list[EducationItem]
    certifications: list[CertificationItem]
    variants: list[ResumeVariantData]

    # Precomputed / lookup index
    def get_all_skills(self) -> list[str]:
        skills: list[str] = []
        for cat in self.skill_categories:
            for s in cat.skills:
                skills.append(s.name)
        return skills

    def get_skill_map(self) -> dict[str, SkillItem]:
        mapping: dict[str, SkillItem] = {}
        for cat in self.skill_categories:
            for s in cat.skills:
                mapping[s.name.lower()] = s
        return mapping

    def has_skill(self, skill_name: str) -> bool:
        s_lower = skill_name.strip().lower()
        mapping = self.get_skill_map()
        return s_lower in mapping

    def get_variant(self, variant_id: str) -> ResumeVariantData | None:
        for v in self.variants:
            if v.id == variant_id:
                return v
        return None

    def get_default_variant(self) -> ResumeVariantData:
        for v in self.variants:
            if v.is_default:
                return v
        return self.variants[0]

    def get_atomic_facts(self) -> list[AtomicFact]:
        facts: list[AtomicFact] = []

        # 1. Profile facts
        facts.append(
            AtomicFact(
                fact_id="fact.profile.experience_tenure",
                category="experience",
                claim=f"{self.profile.full_name} has {self.profile.preferences.total_experience_years} years ({self.profile.preferences.total_experience_months} months) of professional software engineering experience.",
                source="resume",
                verified=True,
                keywords=["experience", "years", "tenure", "software engineer"],
                evidence_type="employment",
                source_reference="docs/ShubhamPrakash_Resume_Latest.pdf",
            )
        )
        facts.append(
            AtomicFact(
                fact_id="fact.profile.current_role",
                category="experience",
                claim=f"Currently working as {self.profile.current_employment.role} at {self.profile.current_employment.company} in {self.profile.current_employment.location}.",
                source="resume",
                verified=True,
                keywords=[self.profile.current_employment.company, self.profile.current_employment.role, "current"],
                evidence_type="employment",
                source_reference="docs/ShubhamPrakash_Resume_Latest.pdf",
            )
        )

        # 2. Experience bullet points as facts
        for exp in self.experiences:
            facts.append(
                AtomicFact(
                    fact_id=f"fact.exp.{exp.company.lower().replace(' ', '_')}.role",
                    category="experience",
                    claim=f"Worked as {exp.role} at {exp.company} from {exp.start_date} to {exp.end_date or 'Present'}.",
                    source="resume",
                    verified=True,
                    keywords=[exp.company, exp.role, exp.location],
                    evidence_type="employment",
                    source_reference=f"Resume - Experience - {exp.company}",
                )
            )
            for bp in exp.bullet_points:
                facts.append(
                    AtomicFact(
                        fact_id=bp.fact_id,
                        category="experience",
                        claim=bp.text,
                        source="resume",
                        verified=bp.verified,
                        keywords=bp.skills + [exp.company],
                        evidence_type="employment",
                        source_reference=f"Resume - {exp.company} Bullet Point",
                        metrics=bp.metrics,
                    )
                )

        # 3. Project bullet points as facts
        for proj in self.projects:
            facts.append(
                AtomicFact(
                    fact_id=f"fact.proj.{proj.id}.overview",
                    category="project",
                    claim=f"Built {proj.name} ({proj.title}): {proj.summary.strip()}",
                    source="portfolio",
                    verified=True,
                    keywords=[proj.name, proj.title] + proj.technologies,
                    evidence_type="project",
                    source_reference=f"Portfolio / GitHub - {proj.name}",
                    metrics=proj.metrics,
                )
            )
            for bp in proj.bullet_points:
                facts.append(
                    AtomicFact(
                        fact_id=bp.fact_id,
                        category="project",
                        claim=bp.text,
                        source="portfolio",
                        verified=bp.verified,
                        keywords=bp.skills + [proj.name],
                        evidence_type="project",
                        source_reference=f"Project {proj.name} - Bullet Point",
                    )
                )

        # 4. Skills as atomic facts
        for cat in self.skill_categories:
            for skill in cat.skills:
                facts.append(
                    AtomicFact(
                        fact_id=f"fact.skill.{cat.id}.{skill.name.lower().replace(' ', '_').replace('/', '_')}",
                        category="skill",
                        claim=f"Proficient in {skill.name} ({skill.proficiency}, ~{skill.years_experience} years). Evidence: {skill.evidence_source}.",
                        source="resume",
                        verified=skill.verified,
                        keywords=[skill.name, cat.name, skill.proficiency],
                        evidence_type="skill",
                        source_reference=skill.evidence_source,
                    )
                )

        # 5. Education facts
        for edu in self.education:
            facts.append(
                AtomicFact(
                    fact_id=f"fact.edu.{edu.id}",
                    category="education",
                    claim=f"Graduated with {edu.degree} in {edu.field_of_study} from {edu.institution} with CGPA of {edu.gpa.display}.",
                    source="resume",
                    verified=True,
                    keywords=[edu.institution, edu.degree, edu.field_of_study, "CGPA", str(edu.gpa.score)],
                    evidence_type="education",
                    source_reference="docs/ShubhamPrakash_Resume_Latest.pdf",
                )
            )

        # 6. Certifications
        for cert in self.certifications:
            facts.append(
                AtomicFact(
                    fact_id=f"fact.cert.{cert.id}",
                    category="education",
                    claim=f"{cert.name} issued by {cert.issuer} ({cert.issue_date}): {cert.description}",
                    source="resume",
                    verified=True,
                    keywords=[cert.name, cert.issuer],
                    evidence_type="education",
                    source_reference="docs/ShubhamPrakash_Resume_Latest.pdf",
                )
            )

        return facts


def locate_candidate_dir() -> Path:
    """Find the candidate YAML directory across different runtime environments."""
    settings = get_settings()
    if settings.CANDIDATE_DATA_DIR:
        p = Path(settings.CANDIDATE_DATA_DIR)
        if p.exists() and p.is_dir():
            return p

    candidates = [
        Path("/app/candidate"),
        Path(__file__).resolve().parents[4] / "candidate",
        Path.cwd() / "candidate",
        Path.cwd().parent / "candidate",
    ]
    for p in candidates:
        if p.exists() and (p / "profile.yaml").exists():
            return p

    raise FileNotFoundError(f"Candidate data directory not found. Checked: {[str(p) for p in candidates]}")


def load_candidate_kb() -> CandidateKnowledgeBase:
    """Parse all candidate YAML files into a strongly-typed CandidateKnowledgeBase."""
    candidate_dir = locate_candidate_dir()

    with open(candidate_dir / "profile.yaml", "r", encoding="utf-8") as f:
        profile_data = yaml.safe_load(f)
        profile = CandidateProfileData(**profile_data)

    with open(candidate_dir / "experience.yaml", "r", encoding="utf-8") as f:
        exp_data = yaml.safe_load(f)
        experiences = [ExperienceItem(**item) for item in exp_data.get("experiences", [])]

    with open(candidate_dir / "projects.yaml", "r", encoding="utf-8") as f:
        proj_data = yaml.safe_load(f)
        projects = [ProjectItem(**item) for item in proj_data.get("projects", [])]

    with open(candidate_dir / "skills.yaml", "r", encoding="utf-8") as f:
        skill_data = yaml.safe_load(f)
        skill_categories = [SkillCategory(**item) for item in skill_data.get("categories", [])]

    with open(candidate_dir / "education.yaml", "r", encoding="utf-8") as f:
        edu_data = yaml.safe_load(f)
        education = [EducationItem(**item) for item in edu_data.get("education", [])]
        certifications = [CertificationItem(**item) for item in edu_data.get("certifications", [])]

    with open(candidate_dir / "variants.yaml", "r", encoding="utf-8") as f:
        var_data = yaml.safe_load(f)
        variants = [ResumeVariantData(**item) for item in var_data.get("variants", [])]

    return CandidateKnowledgeBase(
        profile=profile,
        experiences=experiences,
        projects=projects,
        skill_categories=skill_categories,
        education=education,
        certifications=certifications,
        variants=variants,
    )


_CACHED_KB: CandidateKnowledgeBase | None = None


def get_candidate_kb(force_reload: bool = False) -> CandidateKnowledgeBase:
    """Singleton getter for candidate knowledge base."""
    global _CACHED_KB
    if _CACHED_KB is None or force_reload:
        _CACHED_KB = load_candidate_kb()
    return _CACHED_KB
