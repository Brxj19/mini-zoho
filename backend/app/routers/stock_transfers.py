from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import RoleEnum, StockTransferStatusEnum
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.common import PaginationMeta
from app.schemas.stock_transfer import (
    StockTransferCreate,
    StockTransferListResponse,
    StockTransferResponse,
    StockTransferStatusAction,
    StockTransferUpdate,
    StockTransferItemResponse,
)
from app.services.stock_transfer_service import StockTransferService

router = APIRouter()


def request_meta(request: Request) -> dict[str, str | None]:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


def serialize_transfer(transfer, items) -> StockTransferResponse:
    return StockTransferResponse(
        id=transfer.id,
        tenant_id=transfer.tenant_id,
        source_warehouse_id=transfer.source_warehouse_id,
        destination_warehouse_id=transfer.destination_warehouse_id,
        status=transfer.status,
        notes=transfer.notes,
        created_by=transfer.created_by,
        created_at=transfer.created_at,
        updated_at=transfer.updated_at,
        items=[StockTransferItemResponse.model_validate(item) for item in items],
    )


@router.get("/transfers", response_model=StockTransferListResponse)
def list_transfers(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    status_filter: StockTransferStatusEnum | None = Query(default=None, alias="status"),
    source_warehouse_id: int | None = Query(default=None),
    destination_warehouse_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
) -> StockTransferListResponse:
    page, page_size = pagination
    service = StockTransferService(db)
    transfers, total = service.list_transfers(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        status_filter=status_filter,
        source_warehouse_id=source_warehouse_id,
        destination_warehouse_id=destination_warehouse_id,
        search=search,
    )
    items = []
    for transfer in transfers:
        _, transfer_items = service.get_transfer_for_user(current_user=current_user, transfer_id=transfer.id)
        items.append(serialize_transfer(transfer, transfer_items))
    return StockTransferListResponse(items=items, meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/transfers", response_model=StockTransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(
    payload: StockTransferCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
    tenant_id: int | None = Query(default=None),
) -> StockTransferResponse:
    transfer, items = StockTransferService(db).create_transfer(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return serialize_transfer(transfer, items)


@router.get("/transfers/{transfer_id}", response_model=StockTransferResponse)
def get_transfer(transfer_id: int, db: DbSession, current_user: CurrentUser) -> StockTransferResponse:
    transfer, items = StockTransferService(db).get_transfer_for_user(current_user=current_user, transfer_id=transfer_id)
    return serialize_transfer(transfer, items)


@router.patch("/transfers/{transfer_id}", response_model=StockTransferResponse)
def update_transfer(
    transfer_id: int,
    payload: StockTransferUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> StockTransferResponse:
    transfer, items = StockTransferService(db).update_transfer(current_user=current_user, transfer_id=transfer_id, payload=payload)
    return serialize_transfer(transfer, items)


@router.post("/transfers/{transfer_id}/in-transit", response_model=StockTransferResponse)
def mark_transfer_in_transit(
    transfer_id: int,
    payload: StockTransferStatusAction,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> StockTransferResponse:
    transfer, items = StockTransferService(db).mark_in_transit(current_user=current_user, transfer_id=transfer_id, notes=payload.notes)
    return serialize_transfer(transfer, items)


@router.post("/transfers/{transfer_id}/complete", response_model=StockTransferResponse)
def complete_transfer(
    transfer_id: int,
    payload: StockTransferStatusAction,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> StockTransferResponse:
    transfer, items = StockTransferService(db).complete_transfer(
        current_user=current_user,
        transfer_id=transfer_id,
        notes=payload.notes,
        request_meta=request_meta(request),
    )
    return serialize_transfer(transfer, items)


@router.post("/transfers/{transfer_id}/cancel", response_model=StockTransferResponse)
def cancel_transfer(
    transfer_id: int,
    payload: StockTransferStatusAction,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> StockTransferResponse:
    transfer, items = StockTransferService(db).cancel_transfer(current_user=current_user, transfer_id=transfer_id, notes=payload.notes)
    return serialize_transfer(transfer, items)
