from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.enums import NotificationTypeEnum
from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_many(self, notifications: list[Notification]) -> list[Notification]:
        if notifications:
            self.db.add_all(notifications)
            self.db.flush()
        return notifications

    def get_by_id(self, notification_id: int) -> Notification | None:
        return self.db.get(Notification, notification_id)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        user_id: int | None = None,
        tenant_id: int | None = None,
        is_read: bool | None = None,
        notification_type: NotificationTypeEnum | None = None,
    ) -> tuple[list[Notification], int]:
        query: Select[tuple[Notification]] = select(Notification)
        count_query = select(func.count(Notification.id))

        if user_id is not None:
            query = query.where(Notification.user_id == user_id)
            count_query = count_query.where(Notification.user_id == user_id)
        if tenant_id is not None:
            query = query.where(Notification.tenant_id == tenant_id)
            count_query = count_query.where(Notification.tenant_id == tenant_id)
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
            count_query = count_query.where(Notification.is_read == is_read)
        if notification_type is not None:
            query = query.where(Notification.type == notification_type)
            count_query = count_query.where(Notification.type == notification_type)

        query = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def count_unread(self, *, user_id: int) -> int:
        statement = select(func.count(Notification.id)).where(Notification.user_id == user_id, Notification.is_read.is_(False))
        return self.db.scalar(statement) or 0

    def mark_all_read(self, *, user_id: int) -> int:
        notifications = list(self.db.scalars(select(Notification).where(Notification.user_id == user_id, Notification.is_read.is_(False))).all())
        for notification in notifications:
            notification.is_read = True
            self.db.add(notification)
        self.db.flush()
        return len(notifications)
