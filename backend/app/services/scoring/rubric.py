import json
import re
from datetime import datetime, timezone
from typing import Any

from app.models.job import Job


def score_role_relevance(title: str, description: str, role_category: str | None = None) -> int:
    """
    Score role relevance up to 25 points based on candidate target roles (Section 15):
    - Java + React full stack: 25
    - Distributed systems / Kafka streaming: 24
    - Java backend / Spring Boot: 22
    - Full stack engineer (Java focus): 20
    - React frontend: 12
    - Node backend: 10
    - Unrelated tech stack: 0 - 5
    """
    title_lower = (title or "").lower()
    desc_lower = (description or "").lower()
    combo_text = f"{title_lower} {desc_lower}"

    # Category override if provided
    if role_category:
        cat_upper = role_category.upper()
        if cat_upper == "JAVA_REACT_FULLSTACK":
            return 25
        if cat_upper == "DISTRIBUTED_SYSTEMS":
            return 24
        if cat_upper == "JAVA_BACKEND":
            return 22
        if cat_upper == "FULLSTACK_ENGINEER":
            return 20
        if cat_upper == "UNRELATED":
            return 0

    has_java = bool(re.search(r"\bjava\b", combo_text) or "spring" in combo_text)
    has_react = "react" in combo_text
    has_distributed = "kafka" in combo_text or "distributed" in combo_text or "streaming" in combo_text
    is_fullstack = "full stack" in title_lower or "fullstack" in title_lower

    if has_java and has_react:
        return 25
    if has_distributed and has_java:
        return 24
    if has_java and (is_fullstack or "microservices" in combo_text):
        return 23
    if has_java:
        return 22
    if is_fullstack:
        return 18
    if has_react:
        return 12
    if "node" in combo_text or "typescript" in combo_text:
        return 10
    return 0


def score_core_skills(skills: list[str], text: str) -> tuple[int, list[str], list[str]]:
    """
    Score core skills up to 25 points:
    Java (6), Spring Boot (6), REST/Microservices (5), React/TypeScript (5), SQL/PostgreSQL (3).
    Returns (score, matched_skills, missing_skills).
    """
    text_lower = text.lower()
    matched: list[str] = []
    missing: list[str] = []
    score = 0

    # 1. Java
    if re.search(r"\bjava\b", text_lower) or any("java" == s.lower() for s in skills):
        score += 6
        matched.append("Java")
    else:
        missing.append("Java")

    # 2. Spring Boot
    if "spring boot" in text_lower or "springboot" in text_lower or any("spring" in s.lower() for s in skills):
        score += 6
        matched.append("Spring Boot")
    elif "spring" in text_lower:
        score += 4
        matched.append("Spring Framework")
    else:
        missing.append("Spring Boot")

    # 3. REST / Microservices
    if "microservice" in text_lower or "microservices" in text_lower or "rest" in text_lower:
        score += 5
        matched.append("REST / Microservices")
    else:
        missing.append("Microservices")

    # 4. React / TypeScript
    if "react" in text_lower or "typescript" in text_lower:
        score += 5
        if "react" in text_lower:
            matched.append("React")
        if "typescript" in text_lower:
            matched.append("TypeScript")
    else:
        missing.append("React")

    # 5. Database / SQL / PostgreSQL
    if any(db in text_lower for db in ["postgres", "postgresql", "sql", "mysql", "jpa", "hibernate"]):
        score += 3
        matched.append("SQL / PostgreSQL")
    else:
        missing.append("PostgreSQL")

    return min(25, score), matched, missing


def score_distributed_systems(skills: list[str], text: str) -> tuple[int, list[str]]:
    """
    Score distributed systems & scale up to 15 points (Section 15):
    - Kafka: 5
    - Redis / Caching: 3
    - RabbitMQ / Message Queues: 2
    - WebSockets / Real-time: 2
    - API Gateway / Eureka / High Availability: 3
    """
    text_lower = text.lower()
    matched: list[str] = []
    score = 0

    if "kafka" in text_lower:
        score += 5
        matched.append("Kafka")

    if "redis" in text_lower or "caching" in text_lower:
        score += 3
        matched.append("Redis")

    if "rabbitmq" in text_lower or "activemq" in text_lower or "sqs" in text_lower:
        score += 2
        matched.append("Message Queues")

    if "websocket" in text_lower or "web socket" in text_lower or "sse" in text_lower or "real-time" in text_lower:
        score += 2
        matched.append("WebSockets / Real-Time")

    if any(term in text_lower for term in ["api gateway", "eureka", "resilience4j", "high scale", "distributed", "event-driven"]):
        score += 3
        matched.append("Distributed Architecture")

    return min(15, score), matched


def score_experience(experience_min: float | None, experience_max: float | None, title: str) -> tuple[int, list[str]]:
    """
    Score experience fit up to 15 points.
    Candidate has ~3.2 years experience (ideal range 2.5 - 5.0 years).
    Heavy penalties for Staff, Principal, Director, Architect titles.
    """
    title_lower = title.lower()
    risks: list[str] = []

    # Title penalty
    is_senior_executive = any(t in title_lower for t in ["principal", "staff engineer", "director", "vp ", "vice president", "chief architect"])
    if is_senior_executive:
        risks.append(f"Title '{title}' represents executive/staff level beyond ~3.2 yrs experience.")
        return 0, risks

    if experience_min is None:
        return 10, risks  # Unspecified but not penalised heavily

    # Perfect sweet spot: 2.0 to 4.5 years
    if 2.0 <= experience_min <= 4.0:
        return 15, risks

    # Viable range: 1.0 - 3.0 years
    if 1.0 <= experience_min < 2.0:
        return 12, risks

    # Stretch range: 4.0 - 5.0 years
    if 4.0 < experience_min <= 5.0:
        risks.append(f"Experience requirement ({experience_min}+ yrs) is slightly above candidate's ~3.2 yrs.")
        return 8, risks

    # High stretch: 5.0 - 5.5 years
    if 5.0 < experience_min <= 5.5:
        risks.append(f"Experience requirement ({experience_min}+ yrs) is high for candidate's ~3.2 yrs.")
        return 4, risks

    # > 5.5 years should have been rejected by prefilters
    if experience_min > 5.5:
        risks.append(f"Experience requirement ({experience_min}+ yrs) strictly exceeds candidate profile.")
        return 0, risks

    # Entry level (< 1 yr)
    return 8, risks


def score_location(locations: list[str], remote: bool) -> tuple[int, list[str]]:
    """
    Score location up to 10 points (Section 15):
    - Bangalore / Hyderabad / Pune / Mumbai: 10
    - Remote India: 10
    - Delhi NCR / Chennai / Kolkata: 6
    - Other India: 4
    - Outside India: 0
    """
    warnings: list[str] = []
    if remote:
        return 10, warnings

    locs_lower = [l.lower() for l in locations]
    if not locs_lower:
        return 8, warnings  # Default Indian tech context

    tier1 = ["mumbai", "bengaluru", "bangalore", "hyderabad", "pune", "remote"]
    tier2 = ["delhi", "noida", "gurgaon", "gurugram", "chennai", "kolkata", "ahmedabad"]

    if any(any(t in loc for t in tier1) for loc in locs_lower):
        return 10, warnings

    if any(any(t in loc for t in tier2) for loc in locs_lower):
        warnings.append(f"Job in secondary location: {', '.join(locations)}")
        return 6, warnings

    # Other India
    warnings.append(f"Job in non-primary tech hub: {', '.join(locations)}")
    return 4, warnings


def score_job_quality(source: str, salary_min: int | None, description: str, posted_at: datetime | None) -> tuple[int, list[str]]:
    """
    Score job quality & recency up to 10 points (Section 15):
    - Direct ATS (Greenhouse, Lever): +3
    - Transparent salary disclosed: +2
    - Detailed clear job description (> 400 chars): +3
    - Fresh posting (< 7 days): +2
    """
    score = 0
    strengths: list[str] = []

    # 1. Direct ATS Source
    if source.lower() in ["greenhouse", "lever"]:
        score += 3
        strengths.append("Direct ATS board (high response likelihood)")
    elif source.lower() == "manual":
        score += 2

    # 2. Transparent Salary
    if salary_min and salary_min > 0:
        score += 2
        strengths.append("Transparent salary compensation")

    # 3. Description Depth
    if len(description or "") > 400:
        score += 3

    # 4. Freshness
    if posted_at:
        now = datetime.now(timezone.utc)
        if posted_at.tzinfo is None:
            posted_at = posted_at.replace(tzinfo=timezone.utc)
        age_days = (now - posted_at).total_seconds() / 86400
        if age_days <= 3:
            score += 2
            strengths.append("Freshly posted (< 3 days)")
        elif age_days <= 7:
            score += 1

    return min(10, max(2, score)), strengths

