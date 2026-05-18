from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params
from app.models.enums import NotificationTypeEnum
from app.schemas.auth import MessageResponse
from app.schemas.common import PaginationMeta
from app.schemas.notification import NotificationListResponse, NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
def list_notifications(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    is_read: bool | None = Query(default=None),
    notification_type: NotificationTypeEnum | None = Query(default=None, alias="type"),
) -> NotificationListResponse:
    page, page_size = pagination
    items, total, unread_count = NotificationService(db).list_notifications(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        is_read=is_read,
        notification_type=notification_type,
    )
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
        unread_count=unread_count,
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: int, db: DbSession, current_user: CurrentUser) -> NotificationResponse:
    notification = NotificationService(db).mark_as_read(current_user=current_user, notification_id=notification_id)
    return NotificationResponse.model_validate(notification)


@router.post("/read-all", response_model=MessageResponse)
def mark_all_notifications_read(db: DbSession, current_user: CurrentUser) -> MessageResponse:
    updated = NotificationService(db).mark_all_read(current_user=current_user)
    return MessageResponse(detail=f"Marked {updated} notifications as read.")
