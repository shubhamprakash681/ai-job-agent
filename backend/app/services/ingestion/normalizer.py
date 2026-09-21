import json
import re
from datetime import datetime, timezone
from typing import Any
from app.services.candidate.kb_loader import get_candidate_kb
from app.services.ingestion.base import RawJobData
from app.services.ingestion.dedup import compute_content_hash


KNOWN_INDIAN_CITIES = [
    "mumbai",
    "bengaluru",
    "bangalore",
    "pune",
    "hyderabad",
    "delhi",
    "noida",
    "gurugram",
    "gurgaon",
    "chennai",
    "kolkata",
    "ahmedabad",
    "kochi",
    "cochin",
    "indore",
    "chandigarh",
]

FRAUD_PATTERNS = [
    r"registration\s+fee",
    r"security\s+deposit",
    r"pay\s+before\s+joining",
    r"telegram\s+(?:task|channel|group)",
    r"whatsapp\s+only\s+to\s+apply",
    r"crypto\s+(?:wallet|task)",
    r"part-time\s+data\s+entry\s+earn\s+\d+",
]


def clean_job_title(raw_title: str) -> str:
    """Strip recruiting noise, emojis, and urgency flags from title."""
    cleaned = raw_title.strip()
    # Remove emojis
    cleaned = re.sub(r"[^\x00-\x7F]+", " ", cleaned)
    # Remove urgency prefixes/suffixes
    noise_patterns = [
        r"(?i)\b(urgent|urgently|immediate|hiring\s+now|immediate\s+joiner|walk-?in)\b",
        r"(?i)\b(hot\s+job|apply\s+now|great\s+opportunity)\b",
        r"[!|/\\*\-_]{2,}",
    ]
    for p in noise_patterns:
        cleaned = re.sub(p, " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or raw_title


def parse_locations(raw_location: str | None, text_for_remote_check: str = "") -> tuple[list[str], bool]:
    """Parse city names and remote flag from location string and description."""
    cities: list[str] = []
    is_remote = False

    combined = f"{raw_location or ''} {text_for_remote_check}".lower()

    if re.search(r"\b(remote|work\s+from\s+home|wfh|anywhere)\b", combined):
        is_remote = True

    if raw_location:
        loc_lower = raw_location.lower()
        for city in KNOWN_INDIAN_CITIES:
            if re.search(rf"\b{re.escape(city)}\b", loc_lower):
                # Standardize city names
                if city in ("bangalore", "bengaluru"):
                    standard = "Bengaluru"
                elif city in ("gurgaon", "gurugram"):
                    standard = "Gurugram"
                elif city in ("kochi", "cochin"):
                    standard = "Kochi"
                else:
                    standard = city.title()

                if standard not in cities:
                    cities.append(standard)

    if not cities and is_remote:
        cities.append("Remote")
    elif not cities and raw_location:
        # Fallback to cleaned raw location
        cities.append(raw_location.strip().split(",")[0].strip().title())

    return cities, is_remote


def parse_experience(raw_exp: str | None, text: str = "") -> tuple[float | None, float | None]:
    """Extract min and max experience in years from strings like '3 - 5 yrs' or '3+ years'."""
    combined = f"{raw_exp or ''} {text}".lower()

    # Pattern: 3 - 5 years or 3 to 5 yrs
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years|yrs|year|yr)", combined)
    if range_match:
        return float(range_match.group(1)), float(range_match.group(2))

    # Pattern: 3+ years or min 3 yrs
    min_match = re.search(r"(?:min(?:imum)?\s+)?(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year|yr)", combined)
    if min_match:
        val = float(min_match.group(1))
        return val, val + 3.0  # reasonable upper bound

    return None, None


def parse_salary(raw_sal: str | None, text: str = "") -> tuple[int | None, int | None, str]:
    """Extract salary min, max and currency."""
    currency = "INR"
    combined = f"{raw_sal or ''} {text}".lower()

    # Check currency
    if "$" in combined or "usd" in combined:
        currency = "USD"
        # Example: $100,000 - $140,000 or 100k - 140k
        usd_k_range = re.search(r"\$?(\d{2,3})k?\s*(?:-|to)\s*\$?(\d{2,3})k", combined)
        if usd_k_range:
            min_k = int(usd_k_range.group(1))
            max_k = int(usd_k_range.group(2))
            return min_k * 1000, max_k * 1000, "USD"

    # INR LPA matching: e.g. "12 - 18 lpa" or "15 to 25 lakhs"
    lpa_range = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs|lakh|lac|lacs)", combined)
    if lpa_range:
        min_lakh = float(lpa_range.group(1))
        max_lakh = float(lpa_range.group(2))
        return int(min_lakh * 100000), int(max_lakh * 100000), "INR"

    lpa_single = re.search(r"(\d+(?:\.\d+)?)\s*(?:lpa|lakhs|lakh|lac|lacs)", combined)
    if lpa_single:
        val = int(float(lpa_single.group(1)) * 100000)
        return val, val, "INR"

    return None, None, currency


def extract_skills_from_text(text: str, extra_tags: list[str] | None = None) -> tuple[list[str], list[str], list[str]]:
    """
    Extract skills by scanning against the candidate skills taxonomy.
    Returns (all_skills, required_skills, preferred_skills).
    """
    try:
        kb = get_candidate_kb()
        all_canonical_skills = kb.get_all_skills()
    except Exception:
        all_canonical_skills = ["Java", "Spring Boot", "React", "Node.js", "Kafka", "Redis", "PostgreSQL", "Docker", "AWS EC2"]

    found_skills: set[str] = set()
    text_lower = text.lower()

    for skill in all_canonical_skills:
        pattern = rf"\b{re.escape(skill.lower())}\b"
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    if extra_tags:
        for tag in extra_tags:
            tag_clean = tag.strip()
            for skill in all_canonical_skills:
                if skill.lower() == tag_clean.lower():
                    found_skills.add(skill)

    skills_list = sorted(list(found_skills))
    # Heuristic: split into required vs preferred based on proximity to keywords
    required = [s for s in skills_list if re.search(rf"(?i)(must\s+have|required|mandatory|proficient\s+in).*?{re.escape(s)}", text) or True]
    preferred = [s for s in skills_list if s not in required]

    return skills_list, skills_list, []


def assess_fraud_risk(text: str) -> str:
    """Assess fraud risk: 'none', 'low', 'medium', 'high'."""
    text_lower = text.lower()
    matches = 0
    for p in FRAUD_PATTERNS:
        if re.search(p, text_lower):
            matches += 1

    if matches >= 2:
        return "high"
    elif matches == 1:
        return "medium"
    return "none"


def normalize_job_data(raw: RawJobData) -> dict[str, Any]:
    """
    Normalize raw scraped or manually entered job data into canonical database fields.
    """
    cleaned_title = clean_job_title(raw.title)
    cleaned_company = raw.company.strip() if raw.company else "Unknown Company"

    desc = raw.description or ""
    locations, is_remote = parse_locations(raw.raw_location, text_for_remote_check=desc)
    is_remote = is_remote or raw.is_remote

    exp_min, exp_max = parse_experience(raw.raw_experience, text=desc)
    sal_min, sal_max, currency = parse_salary(raw.raw_salary, text=desc)
    skills, required_skills, preferred_skills = extract_skills_from_text(f"{raw.title} {desc}", raw.skill_tags)
    fraud_risk = assess_fraud_risk(f"{cleaned_title} {cleaned_company} {desc}")

    primary_loc = locations[0] if locations else "Mumbai"
    content_hash = compute_content_hash(cleaned_company, cleaned_title, primary_loc)

    return {
        "source": raw.source,
        "source_job_id": raw.source_job_id,
        "url": raw.url,
        "canonical_url": raw.url,
        "title": cleaned_title,
        "company": cleaned_company,
        "locations": json.dumps(locations),
        "remote": is_remote,
        "experience_min": exp_min,
        "experience_max": exp_max,
        "employment_type": "full_time",
        "salary_min": sal_min,
        "salary_max": sal_max,
        "currency": currency,
        "description": desc,
        "skills": json.dumps(skills),
        "required_skills": json.dumps(required_skills),
        "preferred_skills": json.dumps(preferred_skills),
        "posted_at": raw.posted_at or datetime.now(timezone.utc),
        "application_url": raw.application_url or raw.url,
        "source_type": raw.source_type,
        "raw_content_hash": content_hash,
        "status": "active",
        "fraud_risk": fraud_risk,
    }

