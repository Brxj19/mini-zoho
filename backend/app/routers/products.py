from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import RoleEnum, RecordStatusEnum
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.common import PaginationMeta
from app.schemas.inventory import InventoryTransactionListResponse, InventoryTransactionResponse
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductStockItem,
    ProductStockSummaryResponse,
    ProductUpdate,
)
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
def list_products(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    search: str | None = Query(default=None),
    status_filter: RecordStatusEnum | None = Query(default=None, alias="status"),
    category_id: int | None = Query(default=None),
    brand_id: int | None = Query(default=None),
    vendor_id: int | None = Query(default=None),
    tenant_id: int | None = Query(default=None),
) -> ProductListResponse:
    page, page_size = pagination
    items, total = ProductService(db).list_products(
        current_user=current_user,
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status_filter,
        category_id=category_id,
        brand_id=brand_id,
        vendor_id=vendor_id,
        tenant_id=tenant_id,
    )
    return ProductListResponse(
        items=[ProductResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
    tenant_id: int | None = Query(default=None),
) -> ProductResponse:
    product = ProductService(db).create_product(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: DbSession, current_user: CurrentUser) -> ProductResponse:
    product = ProductService(db).get_product_for_user(current_user=current_user, product_id=product_id)
    return ProductResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> ProductResponse:
    product = ProductService(db).update_product(current_user=current_user, product_id=product_id, payload=payload)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", response_model=MessageResponse)
def archive_product(
    product_id: int,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> MessageResponse:
    ProductService(db).archive_product(current_user=current_user, product_id=product_id)
    return MessageResponse(detail="Product archived successfully.")


@router.get("/{product_id}/stock", response_model=ProductStockSummaryResponse)
def get_product_stock(product_id: int, db: DbSession, current_user: CurrentUser) -> ProductStockSummaryResponse:
    product, summary, warehouses = InventoryService(db).get_product_stock_breakdown(current_user=current_user, product_id=product_id)
    return ProductStockSummaryResponse(
        product_id=product.id,
        total_quantity=summary["total_quantity"],
        reserved_quantity=summary["reserved_quantity"],
        available_quantity=summary["available_quantity"],
        warehouses=[
            ProductStockItem(
                warehouse_id=item.warehouse_id,
                quantity=item.quantity,
                reserved_quantity=item.reserved_quantity,
                available_quantity=item.available_quantity,
                reorder_level=item.reorder_level,
            )
            for item in warehouses
        ],
    )


@router.get("/{product_id}/transactions", response_model=InventoryTransactionListResponse)
def get_product_transactions(
    product_id: int,
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
) -> InventoryTransactionListResponse:
    page, page_size = pagination
    items, total = InventoryService(db).list_product_transactions(
        current_user=current_user,
        product_id=product_id,
        page=page,
        page_size=page_size,
    )
    return InventoryTransactionListResponse(
        items=[InventoryTransactionResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )
