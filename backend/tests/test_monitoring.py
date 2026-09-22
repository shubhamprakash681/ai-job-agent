import json
from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.candidate import CandidateProfile
from app.models.application import Application, ApplicationEvent
from app.models.audit import Notification
from app.services.monitoring.followup_engine import (
    FollowupEngine,
    calculate_followup_status,
    BANNED_CLICHES,
)
from app.services.monitoring.email_parser import EmailParser
from app.services.monitoring.status_manager import StatusManager
from app.services.monitoring.notifier import Notifier


def test_followup_aging_calculation():
    now = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)

    # 3 days ago
    d3, f_type, _ = calculate_followup_status(now - timedelta(days=3), now=now)
    assert d3 == 3
    assert f_type == "RECENT"

    # 7 days ago
    d7, f_type, action = calculate_followup_status(now - timedelta(days=7), now=now)
    assert d7 == 7
    assert f_type == "7_DAY"
    assert "7-day follow-up" in action

    # 10 days ago
    d10, f_type, _ = calculate_followup_status(now - timedelta(days=10), now=now)
    assert d10 == 10
    assert f_type == "7_DAY"

    # 14 days ago
    d14, f_type, _ = calculate_followup_status(now - timedelta(days=14), now=now)
    assert d14 == 14
    assert f_type == "14_DAY"

    # 35 days ago
    d35, f_type, _ = calculate_followup_status(now - timedelta(days=35), now=now)
    assert d35 == 35
    assert f_type == "30_DAY_STALE"


def test_followup_email_drafting():
    job = Job(
        title="Senior Spring Boot & React Developer",
        company="Swiggy",
    )
    app = Application(
        id=1,
        job_id=1,
        candidate_id=1,
        applied_at=datetime.now(timezone.utc) - timedelta(days=8),
    )

    for tone in ["professional", "courteous", "concise"]:
        draft = FollowupEngine.generate_draft(
            application=app,
            job=job,
            tone=tone,
            recipient_name="Priya Sharma",
            recipient_email="priya@swiggy.in",
        )

        assert draft.application_id == 1
        assert "Swiggy" in draft.subject or "Swiggy" in draft.body
        assert "Shubham Prakash" in draft.body
        assert "3.2 years" in draft.body or "~3.2 years" in draft.body
        assert "TCS Digital" in draft.body
        assert "Accenture" in draft.body
        assert "30 days" in draft.body or "30-day" in draft.body
        assert "https://www.shubhamprakash681.in/" in draft.body

        # Check banned clichés
        lower_body = draft.body.lower()
        for cliche in BANNED_CLICHES:
            assert cliche not in lower_body, f"Found banned cliché: {cliche}"


def test_email_classifier_interview():
    raw_email = """
    Hi Shubham,
    Thank you for your patience. We were impressed with your application and would like to
    invite you to interview with our engineering team for the Senior Spring Boot & React Developer role at Swiggy.
    Please select a time on my calendar: https://calendly.com/swiggy-engineering/30min
    Or join directly via Google Meet: https://meet.google.com/abc-defg-hij
    Best,
    Arun (Technical Recruiter)
    """
    sender = "arun.recruiting@swiggy.in"
    subject = "Invitation to Interview: Senior Spring Boot & React Developer at Swiggy"

    parsed = EmailParser.parse_email(raw_email, sender=sender, subject=subject)

    assert parsed.classification == "INTERVIEW_INVITATION"
    assert parsed.confidence >= 0.7
    assert parsed.suggested_status == "INTERVIEW"
    assert parsed.company_extracted == "Swiggy"
    assert len(parsed.key_details.get("meeting_links", [])) >= 2


def test_email_classifier_assessment_and_rejection():
    # Assessment email
    assessment_email = """
    Hello Shubham,
    As the next step for the Java Backend Developer opening, please complete this coding assessment
    on HackerRank: https://hackerrank.com/tests/take/12345
    Please complete the assessment within 5 days.
    """
    p_assess = EmailParser.parse_email(assessment_email, subject="Online Assessment: Java Developer")
    assert p_assess.classification == "ASSESSMENT_REQUEST"
    assert p_assess.key_details.get("assessment_platform") == "HackerRank"
    assert p_assess.key_details.get("deadline") == "within 5 days"
    assert p_assess.suggested_status == "INTERVIEW"

    # Rejection email
    rejection_email = """
    Dear Candidate,
    After careful consideration, our team has decided to move forward with other candidates
    whose qualifications more closely meet our current requirements. We are not moving forward
    at this time. We wish you the best in your job search.
    """
    p_reject = EmailParser.parse_email(rejection_email, subject="Update on your application")
    assert p_reject.classification == "REJECTION"
    assert p_reject.suggested_status == "REJECTED"


def test_email_application_matching():
    apps = [
        {"id": 101, "company": "Swiggy", "title": "Senior Spring Boot & React Developer", "status": "APPLIED"},
        {"id": 102, "company": "Razorpay", "title": "Backend Engineer", "status": "APPLIED"},
    ]

    # Email for Swiggy
    parsed_swiggy = EmailParser.parse_email(
        raw_email_text="Invitation to interview for Senior Spring Boot Developer at Swiggy",
        sender="talent@swiggy.in",
        subject="Interview with Swiggy",
    )
    matched_id, rationale = EmailParser.match_to_applications(parsed_swiggy, apps)
    assert matched_id == 101
    assert "Swiggy" in rationale

    # Email for Razorpay
    parsed_razor = EmailParser.parse_email(
        raw_email_text="Next steps regarding Backend Engineer role at Razorpay",
        sender="careers@razorpay.com",
        subject="Razorpay Interview Process",
    )
    matched_id2, rationale2 = EmailParser.match_to_applications(parsed_razor, apps)
    assert matched_id2 == 102


@pytest.mark.asyncio
async def test_api_followups_and_draft(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    # Setup candidate profile
    profile = CandidateProfile(
        user_id=1,
        full_name="Shubham Prakash",
        email="test@example.com",
        location="Mumbai, India",
    )
    db_session.add(profile)
    await db_session.flush()

    # Create job & application 9 days ago
    job = Job(
        title="Full Stack Java Developer",
        company="Zomato",
        source="manual",
    )
    db_session.add(job)
    await db_session.flush()

    app = Application(
        job_id=job.id,
        candidate_id=profile.id,
        status="APPLIED",
        applied_at=datetime.now(timezone.utc) - timedelta(days=9),
    )
    db_session.add(app)
    await db_session.commit()

    # 1. GET /api/monitoring/followups
    res = await client.get("/api/monitoring/followups", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_needing_followup"] >= 1
    assert data["seven_day_count"] >= 1
    assert data["items"][0]["company"] == "Zomato"
    assert data["items"][0]["days_since_applied"] == 9
    assert data["items"][0]["followup_type"] == "7_DAY"

    # 2. POST /api/monitoring/followups/{id}/draft
    draft_res = await client.post(
        f"/api/monitoring/followups/{app.id}/draft",
        json={"tone": "professional", "recipient_name": "Rohan"},
        headers=auth_headers,
    )
    assert draft_res.status_code == 200
    draft_data = draft_res.json()
    assert draft_data["company"] == "Zomato"
    assert "Shubham Prakash" in draft_data["body"]
    assert "3.2 years" in draft_data["body"]


@pytest.mark.asyncio
async def test_api_email_parse_and_status_update(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession
):
    profile = CandidateProfile(
        user_id=1,
        full_name="Shubham Prakash",
        email="test@example.com",
    )
    db_session.add(profile)
    await db_session.flush()

    job = Job(
        title="Senior Java Developer",
        company="Paytm",
        source="manual",
    )
    db_session.add(job)
    await db_session.flush()

    app = Application(
        job_id=job.id,
        candidate_id=profile.id,
        status="APPLIED",
        applied_at=datetime.now(timezone.utc) - timedelta(days=4),
    )
    db_session.add(app)
    await db_session.commit()

    # 1. POST /api/monitoring/email/parse
    parse_res = await client.post(
        "/api/monitoring/email/parse",
        json={
            "raw_email_text": "We would like to invite you to interview for Senior Java Developer at Paytm! https://meet.google.com/xyz-abcd-efg",
            "sender": "recruiter@paytm.com",
            "subject": "Interview Invitation at Paytm",
        },
        headers=auth_headers,
    )
    assert parse_res.status_code == 200
    parse_data = parse_res.json()
    assert parse_data["classification"] == "INTERVIEW_INVITATION"
    assert parse_data["suggested_application_id"] == app.id
    assert parse_data["suggested_status"] == "INTERVIEW"

    # 2. POST /api/applications/{id}/status -> Move to INTERVIEW
    status_res = await client.post(
        f"/api/applications/{app.id}/status",
        json={
            "status": "INTERVIEW",
            "reason": "Technical Round 1 scheduled",
            "interview_details": {
                "round": "Technical Round 1",
                "interviewer": "Lead Architect",
                "scheduled_at": "2026-09-25 15:00 UTC",
                "meeting_link": "https://meet.google.com/xyz-abcd-efg",
            },
        },
        headers=auth_headers,
    )
    assert status_res.status_code == 200

    # 3. Check notifications created
    notif_res = await client.get("/api/monitoring/notifications", headers=auth_headers)
    assert notif_res.status_code == 200
    notif_data = notif_res.json()
    assert notif_data["unread_count"] >= 1
    assert any("Interview Scheduled" in n["title"] for n in notif_data["items"])

    notif_id = notif_data["items"][0]["id"]

    # 4. Mark notification read
    read_res = await client.post(f"/api/monitoring/notifications/{notif_id}/read", headers=auth_headers)
    assert read_res.status_code == 200

    # 5. Move to OFFER
    offer_res = await client.post(
        f"/api/applications/{app.id}/status",
        json={
            "status": "OFFER",
            "reason": "Offer Letter Received",
            "offer_details": {
                "base_salary": "25,00,000 INR",
                "joining_bonus": "2,00,000 INR",
                "deadline": "2026-10-01",
            },
        },
        headers=auth_headers,
    )
    assert offer_res.status_code == 200

