from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import RoleEnum
from app.schemas.audit_log import AuditLogListResponse, AuditLogResponse
from app.schemas.common import PaginationMeta
from app.services.audit_log_service import AuditLogService

router = APIRouter()


@router.get("/", response_model=AuditLogListResponse)
def list_audit_logs(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    search: str | None = Query(default=None),
) -> AuditLogListResponse:
    page, page_size = pagination
    items, total = AuditLogService(db).list_logs(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )
