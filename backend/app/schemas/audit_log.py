from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.common import ORMBaseSchema, PaginationMeta


class AuditLogResponse(ORMBaseSchema):
    id: int
    tenant_id: int | None
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    old_value_json: dict[str, Any] | None
    new_value_json: dict[str, Any] | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    meta: PaginationMeta
