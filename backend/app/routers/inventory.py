from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import InventorySerialStatusEnum, InventoryTransactionTypeEnum, RoleEnum
from app.models.user import User
from app.schemas.common import PaginationMeta
from app.schemas.inventory import (
    BarcodeGenerateResponse,
    BarcodeSearchResponse,
    InventoryBatchListResponse,
    InventoryBatchResponse,
    InventorySerialListResponse,
    InventorySerialResponse,
    InventoryTransactionListResponse,
    InventoryTransactionResponse,
    LowStockItemResponse,
    LowStockListResponse,
    StockAdjustmentRequest,
    StockInRequest,
    StockOutRequest,
)
from app.services.inventory_service import InventoryService

router = APIRouter()


def request_meta(request: Request) -> dict[str, str | None]:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


@router.get("/transactions", response_model=InventoryTransactionListResponse)
def list_transactions(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    transaction_type: InventoryTransactionTypeEnum | None = Query(default=None),
    created_by: int | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
) -> InventoryTransactionListResponse:
    page, page_size = pagination
    items, total = InventoryService(db).list_transactions(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=transaction_type,
        created_by=created_by,
        date_from=date_from,
        date_to=date_to,
    )
    return InventoryTransactionListResponse(
        items=[InventoryTransactionResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/stock-in", response_model=InventoryTransactionResponse)
def stock_in(
    payload: StockInRequest,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> InventoryTransactionResponse:
    transaction = InventoryService(db).stock_in(current_user=current_user, payload=payload, request_meta=request_meta(request))
    return InventoryTransactionResponse.model_validate(transaction)


@router.post("/stock-out", response_model=InventoryTransactionResponse)
def stock_out(
    payload: StockOutRequest,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> InventoryTransactionResponse:
    transaction = InventoryService(db).stock_out(current_user=current_user, payload=payload, request_meta=request_meta(request))
    return InventoryTransactionResponse.model_validate(transaction)


@router.post("/adjust", response_model=InventoryTransactionResponse)
def adjust_stock(
    payload: StockAdjustmentRequest,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> InventoryTransactionResponse:
    transaction = InventoryService(db).adjust_stock(current_user=current_user, payload=payload, request_meta=request_meta(request))
    return InventoryTransactionResponse.model_validate(transaction)


@router.get("/barcode/generate", response_model=BarcodeGenerateResponse)
def generate_barcode(db: DbSession, current_user: CurrentUser) -> BarcodeGenerateResponse:
    barcode = InventoryService(db).generate_barcode(current_user=current_user)
    return BarcodeGenerateResponse(barcode=barcode)


@router.get("/barcode-search", response_model=BarcodeSearchResponse)
def barcode_search(barcode: str, db: DbSession, current_user: CurrentUser) -> BarcodeSearchResponse:
    product = InventoryService(db).search_product_by_barcode(current_user=current_user, barcode=barcode)
    return BarcodeSearchResponse(product_id=product.id, name=product.name, sku=product.sku, barcode=product.barcode)


@router.get("/low-stock", response_model=LowStockListResponse)
def low_stock(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
) -> LowStockListResponse:
    page, page_size = pagination
    items, total = InventoryService(db).low_stock(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        warehouse_id=warehouse_id,
        product_id=product_id,
    )
    return LowStockListResponse(
        items=[
            LowStockItemResponse(
                product_id=stock.product_id,
                product_name=product.name,
                sku=product.sku,
                warehouse_id=stock.warehouse_id,
                warehouse_name=warehouse.name,
                available_quantity=stock.available_quantity,
                reorder_level=stock.reorder_level if stock.reorder_level is not None else product.reorder_level,
            )
            for stock, product, warehouse in items
        ],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get("/batches", response_model=InventoryBatchListResponse)
def list_batches(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
) -> InventoryBatchListResponse:
    page, page_size = pagination
    items, total = InventoryService(db).list_batches(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
    )
    return InventoryBatchListResponse(
        items=[InventoryBatchResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get("/serials", response_model=InventorySerialListResponse)
def list_serials(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    status_filter: InventorySerialStatusEnum | None = Query(default=None, alias="status"),
) -> InventorySerialListResponse:
    page, page_size = pagination
    items, total = InventoryService(db).list_serials(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
        status_filter=status_filter,
    )
    return InventorySerialListResponse(
        items=[InventorySerialResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )
