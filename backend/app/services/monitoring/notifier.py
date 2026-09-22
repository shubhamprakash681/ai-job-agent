import json
from datetime import datetime, timezone, timedelta
from typing import Any
import structlog
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import Notification

logger = structlog.get_logger(__name__)


class Notifier:
    """
    In-app notification system managing alerts for follow-ups, interview updates,
    and application status changes.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        action_url: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            action_url=action_url,
            data=json.dumps(data) if data else None,
            read=False,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        logger.info(
            "notification_created",
            notification_id=notification.id,
            user_id=user_id,
            type=notification_type,
            title=title,
        )
        return notification

    async def get_unread_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.read == False,
            )
        )
        return result.scalar() or 0

    async def list_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.read == False)
        query = query.order_by(Notification.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        stmt = (
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(read=True)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    async def mark_all_as_read(self, user_id: int) -> int:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.read == False,
            )
            .values(read=True)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount

