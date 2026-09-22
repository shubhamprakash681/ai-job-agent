import re
from typing import Any
import structlog
from app.schemas.monitoring import EmailParseResponse

logger = structlog.get_logger(__name__)

# Meeting link regex patterns
MEETING_LINK_PATTERNS = [
    r"https?://meet\.google\.com/[a-z0-9\-]+",
    r"https?://[a-zA-Z0-9\.\-]*zoom\.us/[a-zA-Z0-9\/\?=\-_&]+",
    r"https?://teams\.microsoft\.com/[a-zA-Z0-9\/\?=\-_&]+",
    r"https?://calendly\.com/[a-zA-Z0-9\/\?=\-_&]+",
]

# Assessment platform indicators
ASSESSMENT_PLATFORMS = [
    ("HackerRank", r"hackerrank\.com"),
    ("CodeSignal", r"codesignal\.com"),
    ("LeetCode", r"leetcode\.com"),
    ("Karat", r"karat\.com"),
    ("TestGorilla", r"testgorilla\.com"),
    ("Codility", r"codility\.com"),
]

# Classification phrase weights
INTENT_INDICATORS = {
    "INTERVIEW_INVITATION": [
        "invitation to interview",
        "invite you to interview",
        "schedule an interview",
        "next steps in our interview process",
        "speak with our team",
        "technical screen",
        "system design interview",
        "hiring manager conversation",
        "schedule a call",
        "discuss the role with our engineering",
        "would love to chat",
        "round 1",
        "round 2",
        "interview confirmation",
    ],
    "ASSESSMENT_REQUEST": [
        "coding assessment",
        "online assessment",
        "coding challenge",
        "technical assessment",
        "take-home test",
        "take-home assignment",
        "complete the assessment",
        "coding test",
        "hackerrank test",
    ],
    "REJECTION": [
        "after careful consideration",
        "decided to move forward with other candidates",
        "not moving forward",
        "will not be proceeding",
        "unable to offer you an interview",
        "decided to pursue other applicants",
        "wishing you the best in your job search",
        "impressed with your background, but",
        "we will keep your resume on file",
        "at this time we have decided",
    ],
    "OFFER": [
        "offer of employment",
        "pleased to offer you",
        "formal offer",
        "official offer",
        "welcome to the team",
        "compensation package",
        "attached offer letter",
    ],
    "APPLICATION_RECEIVED": [
        "thank you for applying",
        "we have received your application",
        "application confirmation",
        "application received",
        "successfully submitted",
        "confirm receipt of your application",
    ],
    "GENERAL_INQUIRY": [
        "what is your notice period",
        "are you open to relocating",
        "current ctc",
        "expected compensation",
        "work authorization",
        "available to join",
    ],
}


class EmailParser:
    """
    Parses incoming recruiter communications, extracts key metadata (meeting links,
    dates, platforms), classifies email intent, and matches the email against
    candidate applications.
    """

    @classmethod
    def parse_email(
        cls,
        raw_email_text: str,
        sender: str | None = None,
        subject: str | None = None,
    ) -> EmailParseResponse:
        full_text = f"{subject or ''}\n{sender or ''}\n{raw_email_text}".strip()
        lower_text = full_text.lower()

        # 1. Classify Intent
        classification, confidence = cls._classify_intent(lower_text)

        # 2. Extract Meeting Links
        meeting_links = []
        for pattern in MEETING_LINK_PATTERNS:
            found = re.findall(pattern, full_text, flags=re.IGNORECASE)
            meeting_links.extend(found)

        # 3. Extract Assessment Platform
        detected_platform = None
        for name, pattern in ASSESSMENT_PLATFORMS:
            if re.search(pattern, lower_text):
                detected_platform = name
                break

        # 4. Extract Deadline or Timing hints
        deadline_hint = None
        deadline_matches = re.findall(
            r"(within \d+ (?:days|hours)|by [A-Za-z]+ \d+|before [A-Za-z]+ \d+|\d{1,2}\/\d{1,2}\/\d{2,4})",
            full_text,
            flags=re.IGNORECASE,
        )
        if deadline_matches:
            deadline_hint = deadline_matches[0]

        # 5. Extract Company & Role Hints
        company_extracted = cls._extract_company(full_text, sender)
        role_extracted = cls._extract_role(full_text, subject)

        key_details: dict[str, Any] = {}
        if meeting_links:
            key_details["meeting_links"] = list(set(meeting_links))
        if detected_platform:
            key_details["assessment_platform"] = detected_platform
        if deadline_hint:
            key_details["deadline"] = deadline_hint
        if sender:
            key_details["sender"] = sender
        if subject:
            key_details["subject"] = subject

        # Determine Suggested Status
        suggested_status = None
        if classification in ("INTERVIEW_INVITATION", "ASSESSMENT_REQUEST"):
            suggested_status = "INTERVIEW"
        elif classification == "REJECTION":
            suggested_status = "REJECTED"
        elif classification == "OFFER":
            suggested_status = "OFFER"
        elif classification == "APPLICATION_RECEIVED":
            suggested_status = "APPLIED"

        return EmailParseResponse(
            classification=classification,
            confidence=confidence,
            company_extracted=company_extracted,
            role_extracted=role_extracted,
            key_details=key_details,
            suggested_status=suggested_status,
        )

    @staticmethod
    def _classify_intent(lower_text: str) -> tuple[str, float]:
        scores: dict[str, int] = {}
        for intent, phrases in INTENT_INDICATORS.items():
            score = 0
            for phrase in phrases:
                if phrase in lower_text:
                    # Give high weight to explicit indicators
                    score += 2 if len(phrase.split()) > 2 else 1
            if score > 0:
                scores[intent] = score

        if not scores:
            return "UNKNOWN", 0.3

        best_intent = max(scores.items(), key=lambda item: item[1])
        # Calculate approximate confidence (0.6 to 0.98)
        confidence = min(0.98, 0.60 + (best_intent[1] * 0.10))
        return best_intent[0], round(confidence, 2)

    @staticmethod
    def _extract_company(text: str, sender: str | None) -> str | None:
        # Check sender domain e.g. recruiter@swiggy.in or careers@amazon.com
        if sender and "@" in sender:
            domain_part = sender.split("@")[-1].lower()
            # Remove common mail hosts
            if domain_part not in ("gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"):
                company_hint = domain_part.split(".")[0].capitalize()
                return company_hint

        # Regex for "at <Company>" or "with <Company>" or "team at <Company>"
        company_patterns = [
            r"(?:at|with|join)\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s+(?:team|careers|engineering|\.|\,|$))",
            r"(?:from)\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s+(?:recruiting|team|\.|\,|$))",
        ]
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                candidate_company = match.group(1).strip()
                if len(candidate_company) > 2 and len(candidate_company) < 30:
                    return candidate_company
        return None

    @staticmethod
    def _extract_role(text: str, subject: str | None) -> str | None:
        role_search_text = f"{subject or ''}\n{text}"
        patterns = [
            r"(?:for the position of|role of|for the role of|position:|role:)\s*([A-Za-z0-9\s\/\+\-]+?)(?:\s+position|\s+role|\.|\,|$)",
            r"(Senior\s+[A-Za-z0-9\s\/\+\-]+?(?:Engineer|Developer))",
            r"([A-Za-z0-9\s\/\+\-]+?(?:Software Engineer|Backend Engineer|Fullstack Engineer|Developer))",
        ]
        for pattern in patterns:
            match = re.search(pattern, role_search_text, flags=re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                if 4 < len(extracted) < 50:
                    return extracted
        return None

    @classmethod
    def match_to_applications(
        cls,
        parsed: EmailParseResponse,
        applications: list[dict[str, Any]],  # List of {id, company, title, status}
    ) -> tuple[int | None, str | None]:
        """
        Match the parsed email to the most suitable existing application.
        Returns: (matched_application_id, rationale)
        """
        if not applications:
            return None, "No active applications available in system."

        best_app_id = None
        best_score = 0
        best_rationale = ""

        extracted_company = (parsed.company_extracted or "").lower()
        extracted_role = (parsed.role_extracted or "").lower()

        for app in applications:
            score = 0
            reasons = []
            app_company = (app.get("company") or "").lower()
            app_title = (app.get("title") or "").lower()

            # 1. Company Name Match
            if extracted_company and app_company:
                if extracted_company == app_company:
                    score += 50
                    reasons.append(f"Exact company match ('{app.get('company')}')")
                elif extracted_company in app_company or app_company in extracted_company:
                    score += 35
                    reasons.append(f"Partial company match ('{app.get('company')}')")

            # 2. Sender Domain in Company Name
            sender = parsed.key_details.get("sender", "").lower()
            if app_company and app_company in sender:
                score += 30
                reasons.append(f"Sender contains company name ('{app.get('company')}')")

            # 3. Role / Title Match
            if extracted_role and app_title:
                if extracted_role in app_title or app_title in extracted_role:
                    score += 20
                    reasons.append(f"Job title match ('{app.get('title')}')")
                else:
                    # Check shared keywords
                    words_extracted = set(re.findall(r"\w+", extracted_role))
                    words_app = set(re.findall(r"\w+", app_title))
                    common = words_extracted.intersection(words_app) - {"developer", "engineer", "senior", "lead", "and", "the"}
                    if common:
                        score += 15
                        reasons.append(f"Matched role keywords: {', '.join(common)}")

            if score > best_score:
                best_score = score
                best_app_id = app["id"]
                best_rationale = "; ".join(reasons)

        if best_score >= 25:
            return best_app_id, f"High confidence match ({best_score} pts): {best_rationale}"
        elif best_score > 0:
            return best_app_id, f"Moderate confidence match ({best_score} pts): {best_rationale}"
        else:
            return None, "Could not correlate with existing applications."

