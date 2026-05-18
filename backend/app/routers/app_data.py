from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.app import (
    CreateItemRequest,
    CreatePurchaseOrderRequest,
    CreateSalesOrderRequest,
    StatusUpdateRequest,
)
from app.services.app_service import (
    create_item,
    create_purchase_order,
    create_sales_order,
    get_dashboard_data,
    get_record_detail,
    list_module_rows,
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    report_catalog,
    report_rows,
    update_order_status,
)

router = APIRouter(prefix="/app", tags=["app"])


@router.get("/dashboard")
def dashboard(db: DbSession, user: CurrentUser) -> dict:
    return get_dashboard_data(db, user)


@router.get("/reports/catalog")
def reports_catalog() -> dict:
    return {"groups": report_catalog()}


@router.get("/reports/{report_key}")
def report_detail(report_key: str, db: DbSession, user: CurrentUser) -> dict:
    return {"rows": report_rows(db, user, report_key)}


@router.get("/notifications/list")
def notifications(db: DbSession, user: CurrentUser) -> dict:
    return {"rows": list_notifications(db, user)}


@router.post("/notifications/{notification_id}/read")
def notification_read(notification_id: int, db: DbSession, user: CurrentUser) -> dict:
    return mark_notification_read(db, user, notification_id)


@router.post("/notifications/read-all")
def notifications_read_all(db: DbSession, user: CurrentUser) -> dict:
    return mark_all_notifications_read(db, user)


@router.post("/items")
def create_item_route(payload: CreateItemRequest, db: DbSession, user: CurrentUser) -> dict:
    return create_item(db, user, payload)


@router.post("/sales-orders")
def create_sales_order_route(payload: CreateSalesOrderRequest, db: DbSession, user: CurrentUser) -> dict:
    return create_sales_order(db, user, payload)


@router.post("/purchase-orders")
def create_purchase_order_route(payload: CreatePurchaseOrderRequest, db: DbSession, user: CurrentUser) -> dict:
    return create_purchase_order(db, user, payload)


@router.patch("/{module}/{record_id}/status")
def patch_status(module: str, record_id: int, payload: StatusUpdateRequest, db: DbSession, user: CurrentUser) -> dict:
    return update_order_status(db, user, module, record_id, payload.status)


@router.get("/{module}/{record_id}")
def detail(module: str, record_id: int, db: DbSession, user: CurrentUser) -> dict:
    return get_record_detail(db, user, module, record_id)


@router.get("/{module}")
def list_rows(module: str, db: DbSession, user: CurrentUser) -> dict:
    return {"rows": list_module_rows(db, user, module)}
