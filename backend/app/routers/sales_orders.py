from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import RoleEnum, SalesOrderStatusEnum
from app.models.user import User
from app.schemas.common import PaginationMeta
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderItemResponse,
    SalesOrderListResponse,
    SalesOrderResponse,
    SalesOrderStatusAction,
    SalesOrderUpdate,
)
from app.services.sales_order_service import SalesOrderService

router = APIRouter()


def request_meta(request: Request) -> dict[str, str | None]:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


def serialize_sales_order(sales_order, items) -> SalesOrderResponse:
    return SalesOrderResponse(
        id=sales_order.id,
        tenant_id=sales_order.tenant_id,
        customer_id=sales_order.customer_id,
        so_number=sales_order.so_number,
        order_date=sales_order.order_date,
        status=sales_order.status,
        subtotal=sales_order.subtotal,
        tax_amount=sales_order.tax_amount,
        discount_amount=sales_order.discount_amount,
        total_amount=sales_order.total_amount,
        notes=sales_order.notes,
        created_by=sales_order.created_by,
        created_at=sales_order.created_at,
        updated_at=sales_order.updated_at,
        items=[SalesOrderItemResponse.model_validate(item) for item in items],
    )


@router.get("/", response_model=SalesOrderListResponse)
def list_sales_orders(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    status_filter: SalesOrderStatusEnum | None = Query(default=None, alias="status"),
    customer_id: int | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    search: str | None = Query(default=None),
) -> SalesOrderListResponse:
    page, page_size = pagination
    service = SalesOrderService(db)
    sales_orders, total = service.list_sales_orders(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        status_filter=status_filter,
        customer_id=customer_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    items = []
    for sales_order in sales_orders:
        _, order_items = service.get_sales_order_for_user(current_user=current_user, sales_order_id=sales_order.id)
        items.append(serialize_sales_order(sales_order, order_items))
    return SalesOrderListResponse(items=items, meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
def create_sales_order(
    payload: SalesOrderCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
    tenant_id: int | None = Query(default=None),
) -> SalesOrderResponse:
    sales_order, items = SalesOrderService(db).create_sales_order(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return serialize_sales_order(sales_order, items)


@router.get("/{sales_order_id}", response_model=SalesOrderResponse)
def get_sales_order(sales_order_id: int, db: DbSession, current_user: CurrentUser) -> SalesOrderResponse:
    sales_order, items = SalesOrderService(db).get_sales_order_for_user(
        current_user=current_user,
        sales_order_id=sales_order_id,
    )
    return serialize_sales_order(sales_order, items)


@router.patch("/{sales_order_id}", response_model=SalesOrderResponse)
def update_sales_order(
    sales_order_id: int,
    payload: SalesOrderUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> SalesOrderResponse:
    sales_order, items = SalesOrderService(db).update_sales_order(
        current_user=current_user,
        sales_order_id=sales_order_id,
        payload=payload,
    )
    return serialize_sales_order(sales_order, items)


@router.post("/{sales_order_id}/confirm", response_model=SalesOrderResponse)
def confirm_sales_order(
    sales_order_id: int,
    payload: SalesOrderStatusAction,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> SalesOrderResponse:
    sales_order, items = SalesOrderService(db).confirm_sales_order(
        current_user=current_user,
        sales_order_id=sales_order_id,
        notes=payload.notes,
        request_meta=request_meta(request),
    )
    return serialize_sales_order(sales_order, items)


@router.post("/{sales_order_id}/pack", response_model=SalesOrderResponse)
def pack_sales_order(
    sales_order_id: int,
    payload: SalesOrderStatusAction,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> SalesOrderResponse:
    sales_order, items = SalesOrderService(db).mark_packed(
        current_user=current_user,
        sales_order_id=sales_order_id,
        notes=payload.notes,
    )
    return serialize_sales_order(sales_order, items)


@router.post("/{sales_order_id}/ship", response_model=SalesOrderResponse)
def ship_sales_order(
    sales_order_id: int,
    payload: SalesOrderStatusAction,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> SalesOrderResponse:
    sales_order, items = SalesOrderService(db).mark_shipped(
        current_user=current_user,
        sales_order_id=sales_order_id,
        notes=payload.notes,
    )
    return serialize_sales_order(sales_order, items)


@router.post("/{sales_order_id}/deliver", response_model=SalesOrderResponse)
def deliver_sales_order(
    sales_order_id: int,
    payload: SalesOrderStatusAction,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF, RoleEnum.INVENTORY_MANAGER)),
) -> SalesOrderResponse:
    sales_order, items = SalesOrderService(db).mark_delivered(
        current_user=current_user,
        sales_order_id=sales_order_id,
        notes=payload.notes,
        request_meta=request_meta(request),
    )
    return serialize_sales_order(sales_order, items)


@router.post("/{sales_order_id}/cancel", response_model=SalesOrderResponse)
def cancel_sales_order(
    sales_order_id: int,
    payload: SalesOrderStatusAction,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> SalesOrderResponse:
    sales_order, items = SalesOrderService(db).cancel_sales_order(
        current_user=current_user,
        sales_order_id=sales_order_id,
        notes=payload.notes,
        request_meta=request_meta(request),
    )
    return serialize_sales_order(sales_order, items)
