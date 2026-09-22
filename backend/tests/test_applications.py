import json
from datetime import datetime, timezone
import pytest
from sqlalchemy import select

from app.models.job import Job
from app.models.application import Application, ApplicationQuestion
from app.models.candidate import CandidateProfile
from app.services.application.state_machine import get_state_machine, ALLOWED_TRANSITIONS
from app.services.application.question_engine import get_question_engine
from app.services.application.submission_engine import get_submission_engine


def test_state_machine_transition_rules():
    sm = get_state_machine()

    # Legal transitions
    assert sm.can_transition("DISCOVERED", "SHORTLISTED") is True
    assert sm.can_transition("AWAITING_APPROVAL", "APPLYING") is True
    assert sm.can_transition("APPLYING", "APPLIED") is True
    assert sm.can_transition("APPLIED", "INTERVIEW") is True

    # Illegal state jumps must be rejected
    assert sm.can_transition("DISCOVERED", "APPLIED") is False
    assert sm.can_transition("APPLIED", "DISCOVERED") is False
    assert sm.can_transition("REJECTED", "APPLIED") is False


def test_screening_question_engine():
    qe = get_question_engine()

    # 1. Notice period question
    ans1 = qe.answer_question("What is your current notice period?")
    assert ans1.confidence == 1.0
    assert "30 days" in ans1.proposed_answer
    assert ans1.requires_human is False

    # 2. Location question
    ans2 = qe.answer_question("Are you willing to relocate or work in Mumbai?")
    assert ans2.confidence == 1.0
    assert "Mumbai" in ans2.proposed_answer
    assert ans2.requires_human is False

    # 3. Work authorization question
    ans3 = qe.answer_question("Are you legally authorized to work in India?")
    assert ans3.confidence == 1.0
    assert "Indian citizen" in ans3.proposed_answer or "authorized to work" in ans3.proposed_answer
    assert ans3.requires_human is False

    # 4. Java experience question
    ans4 = qe.answer_question("How many years of experience do you have with Java and Spring Boot?")
    assert ans4.confidence == 1.0
    assert "3.2 years" in ans4.proposed_answer
    assert "TCS Digital" in ans4.proposed_answer or "Accenture" in ans4.proposed_answer

    # 5. Sensitive compensation question
    ans5 = qe.answer_question("What is your current CTC and expected CTC?")
    assert ans5.requires_human is True  # Must flag for human check


@pytest.mark.asyncio
async def test_human_approval_safety_gate(db_session):
    sm = get_state_machine()

    # Create dummy application in AWAITING_APPROVAL
    job = Job(title="Java Dev", company="Test Corp", source="manual", status="active")
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    prof = CandidateProfile(user_id=1, full_name="Shubham Prakash", email="shubham@test.com")
    db_session.add(prof)
    await db_session.commit()
    await db_session.refresh(prof)

    app = Application(
        job_id=job.id,
        candidate_id=prof.id,
        status="AWAITING_APPROVAL",
    )
    db_session.add(app)
    await db_session.commit()
    await db_session.refresh(app)

    # Attempting to move to APPLYING without human approval must fail
    with pytest.raises(ValueError, match="Human approval is strictly required"):
        await sm.transition(app, "APPLYING", db_session, user_approved=False)

    # Moving to APPLYING with user_approved=True succeeds
    await sm.transition(app, "APPLYING", db_session, user_approved=True)
    assert app.status == "APPLYING"


@pytest.mark.asyncio
async def test_daily_submission_limit_throttle(db_session):
    sm = get_state_machine()

    prof = CandidateProfile(user_id=2, full_name="Shubham Prakash", email="shubham2@test.com")
    db_session.add(prof)
    await db_session.commit()
    await db_session.refresh(prof)

    # Simulate reaching the limit by creating 10 APPLIED applications today
    for i in range(10):
        dummy_job = Job(title=f"Engineer {i}", company=f"Company {i}", source="manual", status="active")
        db_session.add(dummy_job)
        await db_session.commit()
        await db_session.refresh(dummy_job)

        dummy_app = Application(
            job_id=dummy_job.id,
            candidate_id=prof.id,
            status="APPLIED",
            applied_at=datetime.now(timezone.utc),
        )
        db_session.add(dummy_app)
    await db_session.commit()

    # Verify count is 10
    today_count = await sm.get_today_applications_count(db_session)
    assert today_count >= 10

    # 11th application in AWAITING_APPROVAL
    eleventh_job = Job(title="11th Engineer", company="Corp 11", source="manual", status="active")
    db_session.add(eleventh_job)
    await db_session.commit()
    await db_session.refresh(eleventh_job)

    eleventh_app = Application(
        job_id=eleventh_job.id,
        candidate_id=prof.id,
        status="AWAITING_APPROVAL",
    )
    db_session.add(eleventh_app)
    await db_session.commit()
    await db_session.refresh(eleventh_app)

    # Transition to APPLYING must be blocked by daily limit throttle
    with pytest.raises(ValueError, match="Daily application limit reached"):
        await sm.transition(eleventh_app, "APPLYING", db_session, user_approved=True)


@pytest.mark.asyncio
async def test_api_application_lifecycle(client, auth_headers, db_session):
    # 1. Ingest a job
    job = Job(
        source="manual",
        title="Senior Full Stack Java Engineer",
        company="Flipkart",
        description="Looking for Java 17, Spring Boot, React, and Kafka developers in Bengaluru.",
        locations='["Bengaluru"]',
        experience_min=3.0,
        status="active",
        required_skills='["Java", "Spring Boot", "React", "Kafka"]',
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # 2. POST /api/applications/prepare/{job.id} (Package packet)
    prep_resp = await client.post(
        f"/api/applications/prepare/{job.id}",
        json={"variant_id": "java-react-fullstack", "tone": "technical"},
        headers=auth_headers,
    )
    assert prep_resp.status_code == 200
    packet_data = prep_resp.json()
    assert packet_data["job_id"] == job.id
    assert packet_data["job_company"] == "Flipkart"
    assert packet_data["status"] == "AWAITING_APPROVAL"
    assert packet_data["resume_version_id"] is not None
    assert packet_data["cover_letter"] is not None
    assert len(packet_data["questions"]) >= 5
    app_id = packet_data["id"]

    # 3. GET /api/applications/{app_id} (Inspect packet details)
    detail_resp = await client.get(f"/api/applications/{app_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == app_id
    assert detail["status"] == "AWAITING_APPROVAL"
    assert len(detail["events"]) >= 1

    # 4. POST /api/applications/{app_id}/questions/{q_id} (Update question answer)
    q_to_edit = detail["questions"][0]
    q_id = q_to_edit["id"]
    update_q_resp = await client.post(
        f"/api/applications/{app_id}/questions/{q_id}",
        json={"final_answer": "I have 3.2 years of specialized enterprise Java & React experience.", "approved": True},
        headers=auth_headers,
    )
    assert update_q_resp.status_code == 200
    assert update_q_resp.json()["approved"] is True

    # 5. POST /api/applications/{app_id}/approve (Execute submission in DRY_RUN mode)
    approve_resp = await client.post(
        f"/api/applications/{app_id}/approve",
        json={"user_approved": True, "dry_run": True, "notes": "Approved for dry run test"},
        headers=auth_headers,
    )
    assert approve_resp.status_code == 200
    appr_data = approve_resp.json()
    assert appr_data["status"] == "APPLIED"
    evidence = appr_data["evidence"]
    assert evidence["mode"] == "DRY_RUN"
    assert "DRY-RUN-" in evidence["confirmation_code"]
    assert evidence["status"] == "SUCCESS"

    # 6. GET /api/applications (Verify in listing with daily count)
    list_resp = await client.get("/api/applications", headers=auth_headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    assert any(a["id"] == app_id for a in list_data["items"])
    assert list_data["daily_count"] >= 1
    assert list_data["daily_limit"] == 10

