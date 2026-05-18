from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.flush()
        self.db.refresh(log)
        return log

    def list(
        self,
        *,
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
        query: Select[tuple[AuditLog]] = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        if tenant_id is not None:
            query = query.where(AuditLog.tenant_id == tenant_id)
            count_query = count_query.where(AuditLog.tenant_id == tenant_id)
        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
            count_query = count_query.where(AuditLog.entity_type == entity_type)
        if date_from is not None:
            query = query.where(AuditLog.created_at >= date_from)
            count_query = count_query.where(AuditLog.created_at >= date_from)
        if date_to is not None:
            query = query.where(AuditLog.created_at <= date_to)
            count_query = count_query.where(AuditLog.created_at <= date_to)
        if search:
            search_filter = or_(
                AuditLog.action.ilike(f"%{search}%"),
                AuditLog.entity_type.ilike(f"%{search}%"),
                cast(AuditLog.entity_id, String).ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        query = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total
