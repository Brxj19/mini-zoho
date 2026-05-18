from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:
    def __init__(self, db: Session) -> None:
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
