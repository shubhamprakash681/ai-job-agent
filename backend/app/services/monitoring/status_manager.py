import json
from datetime import datetime, timezone
from typing import Any
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationEvent
from app.services.application.state_machine import ApplicationStateMachine
from app.services.monitoring.notifier import Notifier

logger = structlog.get_logger(__name__)


class StatusManager:
    """
    Manages application status progression, interview stages, offer packages,
    and event auditing.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.state_machine = ApplicationStateMachine()
        self.notifier = Notifier(db)

    async def update_status(
        self,
        application: Application,
        user_id: int,
        target_status: str,
        reason: str | None = None,
        notes: str | None = None,
        interview_details: dict[str, Any] | None = None,
        offer_details: dict[str, Any] | None = None,
        force: bool = False,
    ) -> Application:
        """
        Transitions an application to a target status, verifies state machine rules,
        creates audit events, and issues relevant in-app notifications.
        """
        current_status = application.status

        # 1. State machine transition check
        if not force and not self.state_machine.can_transition(current_status, target_status):
            # Allow updating interview round even if already in INTERVIEW
            if current_status == "INTERVIEW" and target_status == "INTERVIEW":
                pass
            else:
                raise ValueError(
                    f"Illegal state transition from {current_status} to {target_status}."
                )

        old_status = application.status
        application.status = target_status

        # Append notes if provided
        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        if notes:
            existing_notes = application.notes or ""
            application.notes = f"{existing_notes}\n[{timestamp_str}] {notes}".strip()

        # 2. Record specific event
        event_payload: dict[str, Any] = {
            "from_status": old_status,
            "to_status": target_status,
            "timestamp": timestamp_str,
            "reason": reason,
        }

        if target_status == "INTERVIEW":
            event_type = "INTERVIEW_SCHEDULED"
            if interview_details:
                event_payload["interview"] = interview_details
            # Issue notification
            round_name = (interview_details or {}).get("round", "Interview")
            await self.notifier.create_notification(
                user_id=user_id,
                notification_type="interview_scheduled",
                title=f"Interview Scheduled: {round_name}",
                message=f"Application #{application.id} moved to Interview stage.",
                action_url=f"/applications?id={application.id}",
                data=interview_details,
            )

        elif target_status == "OFFER":
            event_type = "OFFER_RECEIVED"
            if offer_details:
                event_payload["offer"] = offer_details
            # Issue notification
            await self.notifier.create_notification(
                user_id=user_id,
                notification_type="offer_received",
                title="Job Offer Received!",
                message=f"Congratulations! Offer recorded for Application #{application.id}.",
                action_url=f"/applications?id={application.id}",
                data=offer_details,
            )

        elif target_status == "REJECTED":
            event_type = "APPLICATION_REJECTED"
            if reason:
                event_payload["rejection_reason"] = reason

        elif target_status == "WITHDRAWN":
            event_type = "APPLICATION_WITHDRAWN"
            if reason:
                event_payload["withdrawal_reason"] = reason

        else:
            event_type = "STATUS_UPDATED"

        event = ApplicationEvent(
            application_id=application.id,
            event_type=event_type,
            event_data=json.dumps(event_payload),
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(application)

        logger.info(
            "application_status_updated",
            application_id=application.id,
            from_status=old_status,
            to_status=target_status,
            event_type=event_type,
        )

        return application

