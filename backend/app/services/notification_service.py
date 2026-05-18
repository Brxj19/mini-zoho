from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.enums import NotificationTypeEnum, RoleEnum
from app.models.notification import Notification
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = NotificationRepository(db)
        self.user_repository = UserRepository(db)

    def create_for_tenant_users(
        self,
        *,
        tenant_id: int,
        title: str,
        message: str,
        notification_type: NotificationTypeEnum,
    ) -> list[Notification]:
        users = self.user_repository.list_active_by_tenant(tenant_id)
        notifications = [
            Notification(
                tenant_id=tenant_id,
                user_id=user.id,
                title=title,
                message=message,
                type=notification_type,
                is_read=False,
            )
            for user in users
        ]
        return self.repository.create_many(notifications)

    def list_notifications(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        is_read: bool | None = None,
        notification_type: NotificationTypeEnum | None = None,
    ) -> tuple[list[Notification], int, int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=False)
        user_id = None if current_user.role == RoleEnum.SUPER_ADMIN and tenant_id is not None else current_user.id
        items, total = self.repository.list(
            page=page,
            page_size=page_size,
            user_id=user_id,
            tenant_id=scoped_tenant_id,
            is_read=is_read,
            notification_type=notification_type,
        )
        unread_count = self.repository.count_unread(user_id=current_user.id)
        return items, total, unread_count

    def mark_as_read(self, *, current_user: User, notification_id: int) -> Notification:
        notification = self.repository.get_by_id(notification_id)
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
        if current_user.role != RoleEnum.SUPER_ADMIN and notification.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this notification.")
        notification.is_read = True
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_read(self, *, current_user: User) -> int:
        updated = self.repository.mark_all_read(user_id=current_user.id)
        self.db.commit()
        return updated

    def notify_low_stock(self, *, tenant_id: int, product_name: str, sku: str, warehouse_name: str, available_quantity: int, reorder_level: int) -> None:
        self.create_for_tenant_users(
            tenant_id=tenant_id,
            title="Low stock alert",
            message=f"{product_name} ({sku}) in {warehouse_name} is low on stock: {available_quantity} available, reorder level {reorder_level}.",
            notification_type=NotificationTypeEnum.LOW_STOCK,
        )

    def notify_purchase_receive(self, *, tenant_id: int, po_number: str, actor_name: str) -> None:
        self.create_for_tenant_users(
            tenant_id=tenant_id,
            title="Purchase received",
            message=f"Purchase order {po_number} received stock updates by {actor_name}.",
            notification_type=NotificationTypeEnum.PURCHASE_RECEIVE,
        )

    def notify_order_status(self, *, tenant_id: int, order_kind: str, order_number: str, status_label: str) -> None:
        self.create_for_tenant_users(
            tenant_id=tenant_id,
            title=f"{order_kind} status updated",
            message=f"{order_kind} {order_number} moved to {status_label}.",
            notification_type=NotificationTypeEnum.ORDER_STATUS,
        )

    def notify_suspicious_adjustment(self, *, tenant_id: int, product_name: str, warehouse_name: str, quantity_delta: int, actor_name: str) -> None:
        self.create_for_tenant_users(
            tenant_id=tenant_id,
            title="Suspicious stock adjustment",
            message=f"{actor_name} adjusted {product_name} in {warehouse_name} by {quantity_delta}. Review this adjustment if unexpected.",
            notification_type=NotificationTypeEnum.STOCK_ALERT,
        )
