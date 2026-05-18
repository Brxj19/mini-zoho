from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.enums import RoleEnum
from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AuditLogRepository(db)

    def log(
        self,
        *,
        actor: User,
        action: str,
        entity_type: str,
        entity_id: int | None,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        return self.repository.create(
            AuditLog(
                tenant_id=actor.tenant_id,
                user_id=actor.id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_value_json=old_value,
                new_value_json=new_value,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )

    def list_logs(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        user_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
    ) -> tuple[list[AuditLog], int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        if current_user.role != RoleEnum.SUPER_ADMIN and user_id is not None and user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to these audit logs.")
        return self.repository.list(
            page=page,
            page_size=page_size,
            tenant_id=scoped_tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )
