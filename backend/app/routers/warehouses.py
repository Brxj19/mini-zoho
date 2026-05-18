from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import RecordStatusEnum, RoleEnum
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.auth import MessageResponse
from app.schemas.common import PaginationMeta
from app.schemas.warehouse import WarehouseCreate, WarehouseListResponse, WarehouseResponse, WarehouseUpdate
from app.services.warehouse_service import WarehouseService

router = APIRouter()


@router.get("/", response_model=WarehouseListResponse)
def list_warehouses(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    search: str | None = Query(default=None),
    status_filter: RecordStatusEnum | None = Query(default=None, alias="status"),
    is_default: bool | None = Query(default=None),
    tenant_id: int | None = Query(default=None),
) -> WarehouseListResponse:
    page, page_size = pagination
    service = WarehouseService(db)
    extra_filters = ()
    if is_default is not None:
        extra_filters = (Warehouse.is_default == is_default,)
    items, total = service.list_entities(
        current_user=current_user,
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status_filter,
        tenant_id=tenant_id,
        extra_filters=extra_filters,
    )
    return WarehouseListResponse(
        items=[WarehouseResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse(
    payload: WarehouseCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
    tenant_id: int | None = Query(default=None),
) -> WarehouseResponse:
    warehouse = WarehouseService(db).create_entity(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return WarehouseResponse.model_validate(warehouse)


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(warehouse_id: int, db: DbSession, current_user: CurrentUser) -> WarehouseResponse:
    warehouse = WarehouseService(db).get_entity_for_user(current_user=current_user, entity_id=warehouse_id)
    return WarehouseResponse.model_validate(warehouse)


@router.patch("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: int,
    payload: WarehouseUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> WarehouseResponse:
    warehouse = WarehouseService(db).update_entity(current_user=current_user, entity_id=warehouse_id, payload=payload)
    return WarehouseResponse.model_validate(warehouse)


@router.delete("/{warehouse_id}", response_model=MessageResponse)
def archive_warehouse(
    warehouse_id: int,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> MessageResponse:
    WarehouseService(db).archive_entity(current_user=current_user, entity_id=warehouse_id)
    return MessageResponse(detail="Warehouse archived successfully.")
