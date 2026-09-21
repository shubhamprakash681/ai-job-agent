import re
from typing import Any
from pydantic import BaseModel, Field

from app.services.candidate.kb_loader import (
    CandidateKnowledgeBase,
    get_candidate_kb,
    AtomicFact,
    MetricItem,
)


class EvidenceItem(BaseModel):
    fact_id: str
    category: str
    claim: str
    source_reference: str
    confidence: float = 1.0
    matched_keywords: list[str] = Field(default_factory=list)


class EvidenceVerificationResult(BaseModel):
    is_supported: bool
    confidence: float
    claim: str
    supporting_evidence: list[EvidenceItem] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    reasoning: str


class ValidationReport(BaseModel):
    passed: bool
    confidence_score: float
    supported_claims_count: int
    unsupported_claims_count: int
    supported_claims: list[dict[str, Any]] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    hallucinated_skills: list[str] = Field(default_factory=list)
    verified_skills: list[str] = Field(default_factory=list)
    metric_discrepancies: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


# Known aliases to map informal names to canonical skill names
SKILL_ALIASES: dict[str, str] = {
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring-boot": "Spring Boot",
    "ts": "TypeScript",
    "js": "JavaScript",
    "node": "Node.js",
    "nodejs": "Node.js",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "eureka discovery": "Eureka",
    "spring gateway": "Spring Cloud Gateway",
    "ec2": "AWS EC2",
    "aws": "AWS EC2",
    "websockets": "WebSockets",
    "websocket": "WebSockets",
    "kfk": "Kafka",
    "apache kafka": "Kafka",
    "hibernate": "JPA / Hibernate",
    "jpa": "JPA / Hibernate",
    "auth0": "Auth0 SSO",
    "oauth": "OAuth2",
    "oauth 2.0": "OAuth2",
    "oauth2": "OAuth2",
    "jwt tokens": "JWT",
    "system design": "System Design",
    "hld": "High-Level Design (HLD)",
    "lld": "Low-Level Design (LLD)",
    "dsa": "Data Structures & Algorithms (DSA)",
    "oop": "Object-Oriented Programming (OOP)",
    "react.js": "React",
    "reactjs": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
}

# Forbidden / known hallucinated skills that must be rejected if claimed as core experience
PROHIBITED_OR_UNVERIFIED_TECH: set[str] = {
    "kubernetes",
    "k8s",
    "graphql",
    "rust",
    "golang",
    "go",
    "c++",
    "c#",
    ".net",
    "flutter",
    "swift",
    "kotlin",
    "solidity",
    "blockchain",
    "angular",
    "vue",
    "vue.js",
    "django",
    "ruby",
    "rails",
    "scala",
    "spark",
    "hadoop",
    "azure",
    "gcp",
}


class EvidenceEngine:
    def __init__(self, kb: CandidateKnowledgeBase | None = None):
        self.kb = kb or get_candidate_kb()
        self._build_index()

    def _build_index(self) -> None:
        """Index skills and atomic facts for fast matching."""
        self.canonical_skills: dict[str, str] = {}
        for skill_name in self.kb.get_all_skills():
            self.canonical_skills[skill_name.lower()] = skill_name

        # Include aliases
        for alias, canonical in SKILL_ALIASES.items():
            self.canonical_skills[alias.lower()] = canonical

        self.atomic_facts = self.kb.get_atomic_facts()

    def normalize_skill(self, skill: str) -> str | None:
        """Return canonical skill name if recognized in candidate taxonomy."""
        cleaned = skill.strip().lower()
        return self.canonical_skills.get(cleaned)

    def verify_claim(self, claim: str) -> EvidenceVerificationResult:
        """Verify whether an individual claim or sentence is grounded in candidate facts."""
        claim_clean = claim.strip()
        claim_lower = claim_clean.lower()

        # Check for hallucinated technologies
        for bad_tech in PROHIBITED_OR_UNVERIFIED_TECH:
            pattern = rf"\b{re.escape(bad_tech)}\b"
            if re.search(pattern, claim_lower):
                return EvidenceVerificationResult(
                    is_supported=False,
                    confidence=0.0,
                    claim=claim_clean,
                    conflicts=[f"Candidate has no verified production experience with '{bad_tech}'."],
                    reasoning=f"Claim mentions '{bad_tech}', which is not present in Shubham Prakash's verified knowledge base.",
                )

        # Check for inflated years of experience
        years_match = re.search(r"(\d+)\+?\s*(?:years|yrs)", claim_lower)
        if years_match:
            claimed_years = int(years_match.group(1))
            actual_years = self.kb.profile.preferences.total_experience_years
            if claimed_years > actual_years + 0.5:
                return EvidenceVerificationResult(
                    is_supported=False,
                    confidence=0.0,
                    claim=claim_clean,
                    conflicts=[f"Claimed {claimed_years} years experience exceeds verified tenure of ~{actual_years} years."],
                    reasoning=f"Metric discrepancy: candidate has {actual_years} years experience, but claim states {claimed_years} years.",
                )

        # Search for supporting atomic facts
        matched_evidence: list[EvidenceItem] = []
        words = set(re.findall(r"[a-zA-Z0-9_\-\.\+]+", claim_lower))

        for fact in self.atomic_facts:
            fact_claim_lower = fact.claim.lower()
            fact_words = set(re.findall(r"[a-zA-Z0-9_\-\.\+]+", fact_claim_lower))

            # Keyword overlap
            common = words.intersection(fact_words)
            keyword_overlap = [kw for kw in fact.keywords if kw.lower() in claim_lower]

            if len(keyword_overlap) >= 2 or len(common) >= 4 or fact_claim_lower in claim_lower or claim_lower in fact_claim_lower:
                confidence = 1.0 if (claim_lower in fact_claim_lower or fact_claim_lower in claim_lower) else min(0.95, 0.5 + 0.1 * len(keyword_overlap))
                matched_evidence.append(
                    EvidenceItem(
                        fact_id=fact.fact_id,
                        category=fact.category,
                        claim=fact.claim,
                        source_reference=fact.source_reference,
                        confidence=confidence,
                        matched_keywords=keyword_overlap,
                    )
                )

        if matched_evidence:
            # Sort by confidence descending
            matched_evidence.sort(key=lambda e: e.confidence, reverse=True)
            top_evidence = matched_evidence[:3]
            return EvidenceVerificationResult(
                is_supported=True,
                confidence=top_evidence[0].confidence,
                claim=claim_clean,
                supporting_evidence=top_evidence,
                reasoning=f"Claim is supported by {len(matched_evidence)} verified fact(s) in the knowledge base.",
            )

        return EvidenceVerificationResult(
            is_supported=False,
            confidence=0.2,
            claim=claim_clean,
            conflicts=["No direct evidence found in candidate knowledge base."],
            reasoning="Could not find sufficient matching facts or bullet points to verify this claim.",
        )

    def validate_resume_content(self, text: str) -> ValidationReport:
        """
        Comprehensive anti-hallucination validation of resume or cover letter content.
        Verifies every paragraph/bullet point, detects forbidden tech, and checks metrics.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        supported_claims: list[dict[str, Any]] = []
        unsupported_claims: list[str] = []
        hallucinated_skills: list[str] = []
        verified_skills_set: set[str] = set()
        metric_discrepancies: list[dict[str, Any]] = []
        warnings: list[str] = []
        errors: list[str] = []

        text_lower = text.lower()

        # 1. Prohibited / unverified tech check
        for bad_tech in PROHIBITED_OR_UNVERIFIED_TECH:
            pattern = rf"\b{re.escape(bad_tech)}\b"
            if re.search(pattern, text_lower):
                hallucinated_skills.append(bad_tech)
                errors.append(f"Forbidden or unverified technology detected: '{bad_tech}'. Candidate has no verified experience in it.")

        # 2. Extract and verify recognized skills
        all_candidate_skills = self.kb.get_all_skills()
        for skill in all_candidate_skills:
            pattern = rf"\b{re.escape(skill.lower())}\b"
            if re.search(pattern, text_lower):
                verified_skills_set.add(skill)

        # 3. Check for inflated metrics
        # Check concurrent users (verified max: 10,000)
        user_matches = re.findall(r"(\d{1,3}(?:,\d{3})+|\d+)\+?\s*(?:concurrent\s+)?users", text_lower)
        for m in user_matches:
            val = int(m.replace(",", ""))
            if val > 15000:
                metric_discrepancies.append({
                    "metric": "concurrent_users",
                    "claimed_value": val,
                    "verified_value": 10000,
                    "issue": f"Claimed {val} concurrent users exceeds verified metric of 10,000+ at TCS Digital."
                })
                errors.append(f"Inflated concurrent users metric: {val} > 10,000 verified.")

        # Check total years experience
        exp_matches = re.findall(r"(\d+)\+?\s*(?:years|yrs)\s+(?:of\s+)?(?:experience|exp)", text_lower)
        for m in exp_matches:
            val = int(m)
            if val > 4:
                metric_discrepancies.append({
                    "metric": "experience_years",
                    "claimed_value": val,
                    "verified_value": 3.2,
                    "issue": f"Claimed {val} years experience exceeds verified tenure of 3+ years."
                })
                errors.append(f"Inflated experience tenure: {val} years > 3+ years verified.")

        # 4. Line-by-line claim verification
        bullet_lines = [l.lstrip("*-•◦ ") for l in lines if len(l.split()) >= 4 and not l.startswith("#")]

        for line in bullet_lines:
            res = self.verify_claim(line)
            if res.is_supported:
                supported_claims.append({
                    "claim": line,
                    "confidence": res.confidence,
                    "primary_fact_id": res.supporting_evidence[0].fact_id if res.supporting_evidence else None,
                    "source": res.supporting_evidence[0].source_reference if res.supporting_evidence else None,
                })
            else:
                unsupported_claims.append(line)
                warnings.append(f"Unverified claim: '{line[:80]}...'")

        # Determine overall pass/fail status
        passed = (len(errors) == 0) and (len(hallucinated_skills) == 0) and (len(metric_discrepancies) == 0)
        
        # Calculate confidence score
        total_claims = len(supported_claims) + len(unsupported_claims)
        ratio = (len(supported_claims) / total_claims) if total_claims > 0 else 1.0
        confidence_score = round(ratio * 0.9 if passed else ratio * 0.4, 2)

        return ValidationReport(
            passed=passed,
            confidence_score=confidence_score,
            supported_claims_count=len(supported_claims),
            unsupported_claims_count=len(unsupported_claims),
            supported_claims=supported_claims,
            unsupported_claims=unsupported_claims,
            hallucinated_skills=hallucinated_skills,
            verified_skills=sorted(list(verified_skills_set)),
            metric_discrepancies=metric_discrepancies,
            warnings=warnings,
            errors=errors,
        )


_ENGINE_INSTANCE: EvidenceEngine | None = None


def get_evidence_engine() -> EvidenceEngine:
    """Singleton getter for EvidenceEngine."""
    global _ENGINE_INSTANCE
    if _ENGINE_INSTANCE is None:
        _ENGINE_INSTANCE = EvidenceEngine()
    return _ENGINE_INSTANCE

