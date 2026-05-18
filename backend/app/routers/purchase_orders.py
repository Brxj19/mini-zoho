from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import PurchaseOrderStatusEnum, RoleEnum
from app.models.user import User
from app.schemas.common import PaginationMeta
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderIssueAction,
    PurchaseOrderItemResponse,
    PurchaseOrderListResponse,
    PurchaseOrderReceiveRequest,
    PurchaseOrderResponse,
    PurchaseOrderUpdate,
)
from app.services.purchase_order_service import PurchaseOrderService

router = APIRouter()


def request_meta(request: Request) -> dict[str, str | None]:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


def serialize_purchase_order(purchase_order, items) -> PurchaseOrderResponse:
    return PurchaseOrderResponse(
        id=purchase_order.id,
        tenant_id=purchase_order.tenant_id,
        vendor_id=purchase_order.vendor_id,
        po_number=purchase_order.po_number,
        order_date=purchase_order.order_date,
        expected_delivery_date=purchase_order.expected_delivery_date,
        status=purchase_order.status,
        subtotal=purchase_order.subtotal,
        tax_amount=purchase_order.tax_amount,
        total_amount=purchase_order.total_amount,
        notes=purchase_order.notes,
        created_by=purchase_order.created_by,
        created_at=purchase_order.created_at,
        updated_at=purchase_order.updated_at,
        items=[PurchaseOrderItemResponse.model_validate(item) for item in items],
    )


@router.get("/", response_model=PurchaseOrderListResponse)
def list_purchase_orders(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    status_filter: PurchaseOrderStatusEnum | None = Query(default=None, alias="status"),
    vendor_id: int | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    search: str | None = Query(default=None),
) -> PurchaseOrderListResponse:
    page, page_size = pagination
    service = PurchaseOrderService(db)
    purchase_orders, total = service.list_purchase_orders(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        status_filter=status_filter,
        vendor_id=vendor_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    items = []
    for purchase_order in purchase_orders:
        _, order_items = service.get_purchase_order_for_user(current_user=current_user, purchase_order_id=purchase_order.id)
        items.append(serialize_purchase_order(purchase_order, order_items))
    return PurchaseOrderListResponse(items=items, meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    payload: PurchaseOrderCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF)),
    tenant_id: int | None = Query(default=None),
) -> PurchaseOrderResponse:
    purchase_order, items = PurchaseOrderService(db).create_purchase_order(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return serialize_purchase_order(purchase_order, items)


@router.get("/{purchase_order_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(purchase_order_id: int, db: DbSession, current_user: CurrentUser) -> PurchaseOrderResponse:
    purchase_order, items = PurchaseOrderService(db).get_purchase_order_for_user(
        current_user=current_user,
        purchase_order_id=purchase_order_id,
    )
    return serialize_purchase_order(purchase_order, items)


@router.patch("/{purchase_order_id}", response_model=PurchaseOrderResponse)
def update_purchase_order(
    purchase_order_id: int,
    payload: PurchaseOrderUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF)),
) -> PurchaseOrderResponse:
    purchase_order, items = PurchaseOrderService(db).update_purchase_order(
        current_user=current_user,
        purchase_order_id=purchase_order_id,
        payload=payload,
    )
    return serialize_purchase_order(purchase_order, items)


@router.post("/{purchase_order_id}/issue", response_model=PurchaseOrderResponse)
def issue_purchase_order(
    purchase_order_id: int,
    payload: PurchaseOrderIssueAction,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF)),
) -> PurchaseOrderResponse:
    purchase_order, items = PurchaseOrderService(db).issue_purchase_order(
        current_user=current_user,
        purchase_order_id=purchase_order_id,
        notes=payload.notes,
    )
    return serialize_purchase_order(purchase_order, items)


@router.post("/{purchase_order_id}/receive", response_model=PurchaseOrderResponse)
def receive_purchase_order(
    purchase_order_id: int,
    payload: PurchaseOrderReceiveRequest,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF, RoleEnum.INVENTORY_MANAGER)),
) -> PurchaseOrderResponse:
    purchase_order, items = PurchaseOrderService(db).receive_purchase_order(
        current_user=current_user,
        purchase_order_id=purchase_order_id,
        payload=payload,
        request_meta=request_meta(request),
    )
    return serialize_purchase_order(purchase_order, items)


@router.post("/{purchase_order_id}/cancel", response_model=PurchaseOrderResponse)
def cancel_purchase_order(
    purchase_order_id: int,
    payload: PurchaseOrderIssueAction,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF)),
) -> PurchaseOrderResponse:
    purchase_order, items = PurchaseOrderService(db).cancel_purchase_order(
        current_user=current_user,
        purchase_order_id=purchase_order_id,
        notes=payload.notes,
    )
    return serialize_purchase_order(purchase_order, items)
