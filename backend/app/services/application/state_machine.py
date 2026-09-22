import json
from datetime import datetime, timezone, timedelta
from typing import Any
import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.application import Application, ApplicationEvent

logger = structlog.get_logger(__name__)

# Valid application lifecycle states per PROMPT.md Section 24
APPLICATION_STATES = [
    "DISCOVERED",
    "SHORTLISTED",
    "ANALYZING",
    "RESUME_READY",
    "READY_TO_APPLY",
    "AWAITING_APPROVAL",
    "APPLYING",
    "APPLIED",
    "FAILED",
    "CAPTCHA_REQUIRED",
    "MANUAL_REQUIRED",
    "REJECTED",
    "INTERVIEW",
    "OFFER",
    "WITHDRAWN",
]

ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "DISCOVERED": ["SHORTLISTED", "ANALYZING", "RESUME_READY", "REJECTED"],
    "SHORTLISTED": ["ANALYZING", "RESUME_READY", "READY_TO_APPLY", "REJECTED"],
    "ANALYZING": ["SHORTLISTED", "RESUME_READY", "READY_TO_APPLY", "REJECTED"],
    "RESUME_READY": ["READY_TO_APPLY", "AWAITING_APPROVAL", "REJECTED"],
    "READY_TO_APPLY": ["AWAITING_APPROVAL", "REJECTED"],
    "AWAITING_APPROVAL": ["APPLYING", "MANUAL_REQUIRED", "REJECTED", "WITHDRAWN"],
    "APPLYING": ["APPLIED", "FAILED", "CAPTCHA_REQUIRED", "MANUAL_REQUIRED"],
    "APPLIED": ["INTERVIEW", "REJECTED", "WITHDRAWN"],
    "FAILED": ["AWAITING_APPROVAL", "MANUAL_REQUIRED", "REJECTED"],
    "CAPTCHA_REQUIRED": ["APPLIED", "MANUAL_REQUIRED", "REJECTED"],
    "MANUAL_REQUIRED": ["APPLIED", "REJECTED", "WITHDRAWN"],
    "INTERVIEW": ["OFFER", "REJECTED", "WITHDRAWN"],
    "OFFER": ["WITHDRAWN"],
    "REJECTED": [],
    "WITHDRAWN": [],
}


class ApplicationStateMachine:
    """
    Manages state transitions, business rules, safety throttles, and audit events for applications.
    """

    def __init__(self):
        self.settings = get_settings()

    def can_transition(self, current_status: str, target_status: str) -> bool:
        """Check if transition between statuses is legally permitted."""
        if current_status == target_status:
            return True
        allowed = ALLOWED_TRANSITIONS.get(current_status, [])
        return target_status in allowed

    async def get_today_applications_count(self, db: AsyncSession) -> int:
        """Count applications submitted or currently submitting in the last 24 hours / current day."""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = (
            select(func.count(Application.id))
            .where(
                Application.status.in_(["APPLYING", "APPLIED"]),
                Application.applied_at >= today_start,
            )
        )
        res = await db.execute(query)
        return res.scalar_one() or 0

    async def transition(
        self,
        app: Application,
        target_status: str,
        db: AsyncSession,
        user_approved: bool = False,
        notes: str | None = None,
        event_metadata: dict[str, Any] | None = None,
    ) -> Application:
        """
        Execute an application state transition with safety checks and event logging.
        """
        current_status = app.status or "DISCOVERED"

        if target_status not in APPLICATION_STATES:
            raise ValueError(f"Invalid application state: '{target_status}'")

        if not self.can_transition(current_status, target_status):
            raise ValueError(
                f"Illegal state transition from '{current_status}' to '{target_status}'. "
                f"Allowed transitions from '{current_status}': {ALLOWED_TRANSITIONS.get(current_status, [])}"
            )

        # Safety Check 1: Human approval requirement for APPLYING
        if target_status == "APPLYING":
            if self.settings.HUMAN_APPROVAL_REQUIRED and not user_approved:
                raise ValueError(
                    "Transition to 'APPLYING' blocked: Human approval is strictly required before submission."
                )

            # Safety Check 2: Daily application limit throttle
            today_count = await self.get_today_applications_count(db)
            daily_limit = self.settings.DAILY_APPLICATION_LIMIT
            if today_count >= daily_limit:
                raise ValueError(
                    f"Daily application limit reached: {today_count}/{daily_limit} applications processed today. "
                    "Submission blocked to prevent platform flagging."
                )

        # Update application state
        previous_status = app.status
        app.status = target_status
        if notes:
            app.notes = (app.notes or "") + f"\n[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}] {notes}"

        # Record Application Event
        event_payload = {
            "from_status": previous_status,
            "to_status": target_status,
            "user_approved": user_approved,
            "notes": notes,
            "metadata": event_metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        event = ApplicationEvent(
            application_id=app.id,
            event_type=f"STATUS_TRANSITION_{target_status}",
            event_data=json.dumps(event_payload),
        )
        db.add(event)

        logger.info(
            "Application state transitioned",
            app_id=app.id,
            from_status=previous_status,
            to_status=target_status,
            user_approved=user_approved,
        )

        return app


_STATE_MACHINE: ApplicationStateMachine | None = None


def get_state_machine() -> ApplicationStateMachine:
    global _STATE_MACHINE
    if _STATE_MACHINE is None:
        _STATE_MACHINE = ApplicationStateMachine()
    return _STATE_MACHINE

