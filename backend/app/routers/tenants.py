from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import CurrentUser, DbSession, assert_tenant_access, get_pagination_params, require_roles
from app.models.enums import RoleEnum, TenantStatusEnum
from app.models.user import User
from app.schemas.common import PaginationMeta
from app.schemas.tenant import (
    TenantCreate,
    TenantListResponse,
    TenantPlanAssignment,
    TenantResponse,
    TenantStatusUpdate,
    TenantUpdate,
    TenantUsageResponse,
)
from app.services.tenant_service import TenantService

router = APIRouter()


@router.get("/", response_model=TenantListResponse)
def list_tenants(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    search: str | None = Query(default=None),
    status_filter: TenantStatusEnum | None = Query(default=None, alias="status"),
) -> TenantListResponse:
    page, page_size = pagination
    service = TenantService(db)
    tenant_id = None if current_user.role == RoleEnum.SUPER_ADMIN else current_user.tenant_id
    items, total = service.tenant_repository.list(
        page=page,
        page_size=page_size,
        search=search,
        status=status_filter,
        tenant_id=tenant_id,
    )
    return TenantListResponse(
        items=[TenantResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(
    payload: TenantCreate,
    db: DbSession,
    _: User = Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> TenantResponse:
    tenant = TenantService(db).create_tenant(payload)
    return TenantResponse.model_validate(tenant)


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: int, db: DbSession, current_user: CurrentUser) -> TenantResponse:
    assert_tenant_access(current_user, tenant_id)
    tenant = TenantService(db).get_tenant_or_404(tenant_id)
    return TenantResponse.model_validate(tenant)


@router.patch("/{tenant_id}", response_model=TenantResponse)
def update_tenant(tenant_id: int, payload: TenantUpdate, db: DbSession, current_user: CurrentUser) -> TenantResponse:
    assert_tenant_access(current_user, tenant_id)
    service = TenantService(db)
    tenant = service.get_tenant_or_404(tenant_id)
    updated_tenant = service.update_tenant(tenant, payload)
    return TenantResponse.model_validate(updated_tenant)


@router.patch("/{tenant_id}/plan", response_model=TenantResponse)
def assign_tenant_plan(
    tenant_id: int,
    payload: TenantPlanAssignment,
    db: DbSession,
    _: User = Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> TenantResponse:
    service = TenantService(db)
    tenant = service.get_tenant_or_404(tenant_id)
    updated_tenant = service.update_tenant(tenant, TenantUpdate(subscription_plan_id=payload.subscription_plan_id))
    return TenantResponse.model_validate(updated_tenant)


@router.patch("/{tenant_id}/status", response_model=TenantResponse)
def update_tenant_status(
    tenant_id: int,
    payload: TenantStatusUpdate,
    db: DbSession,
    _: User = Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> TenantResponse:
    service = TenantService(db)
    tenant = service.get_tenant_or_404(tenant_id)
    updated_tenant = service.update_status(tenant, payload.status)
    return TenantResponse.model_validate(updated_tenant)


@router.get("/{tenant_id}/usage", response_model=TenantUsageResponse)
def get_tenant_usage(tenant_id: int, db: DbSession, current_user: CurrentUser) -> TenantUsageResponse:
    assert_tenant_access(current_user, tenant_id)
    service = TenantService(db)
    service.get_tenant_or_404(tenant_id)
    return TenantUsageResponse(**service.get_usage(tenant_id))
