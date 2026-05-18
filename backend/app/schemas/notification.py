from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import NotificationTypeEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class NotificationResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    user_id: int
    title: str
    message: str
    type: NotificationTypeEnum
    is_read: bool
    created_at: datetime
    updated_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    meta: PaginationMeta
    unread_count: int
