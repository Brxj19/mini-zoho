from __future__ import annotations

from datetime import date, datetime, UTC

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.core.dependencies import CurrentUser, DbSession
from app.models.enums import PurchaseOrderStatusEnum, SalesOrderStatusEnum
from app.schemas.report import ReportTableResponse
from app.services.report_service import ReportService
from app.utils.csv_export import build_csv_response

router = APIRouter()


def serialize_filter_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def report_response(*, report_name: str, rows: list[dict], filters: dict, export: str | None) -> ReportTableResponse | StreamingResponse:
    if export == "csv":
        filename = f"{report_name.replace(' ', '_').lower()}.csv"
        return build_csv_response(filename=filename, rows=rows)
    return ReportTableResponse(
        report_name=report_name,
        generated_at=datetime.now(UTC),
        filters=filters,
        row_count=len(rows),
        rows=rows,
    )


def filter_payload(**kwargs) -> dict:
    return {key: serialize_filter_value(value) for key, value in kwargs.items() if value is not None}


@router.get("/inventory-summary", response_model=ReportTableResponse)
def inventory_summary_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).inventory_summary(
        current_user=current_user,
        tenant_id=tenant_id,
        warehouse_id=warehouse_id,
        product_id=product_id,
        category_id=category_id,
    )
    return report_response(
        report_name="Inventory Summary",
        rows=rows,
        filters=filter_payload(tenant_id=tenant_id, warehouse_id=warehouse_id, product_id=product_id, category_id=category_id),
        export=export,
    )


@router.get("/stock-movement", response_model=ReportTableResponse)
def stock_movement_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).stock_movement(
        current_user=current_user,
        tenant_id=tenant_id,
        warehouse_id=warehouse_id,
        product_id=product_id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
    )
    return report_response(
        report_name="Stock Movement",
        rows=rows,
        filters=filter_payload(
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
        ),
        export=export,
    )


@router.get("/low-stock", response_model=ReportTableResponse)
def low_stock_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).low_stock(
        current_user=current_user,
        tenant_id=tenant_id,
        warehouse_id=warehouse_id,
        product_id=product_id,
        category_id=category_id,
    )
    return report_response(
        report_name="Low Stock",
        rows=rows,
        filters=filter_payload(tenant_id=tenant_id, warehouse_id=warehouse_id, product_id=product_id, category_id=category_id),
        export=export,
    )


@router.get("/out-of-stock", response_model=ReportTableResponse)
def out_of_stock_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).out_of_stock(
        current_user=current_user,
        tenant_id=tenant_id,
        warehouse_id=warehouse_id,
        product_id=product_id,
        category_id=category_id,
    )
    return report_response(
        report_name="Out Of Stock",
        rows=rows,
        filters=filter_payload(tenant_id=tenant_id, warehouse_id=warehouse_id, product_id=product_id, category_id=category_id),
        export=export,
    )


@router.get("/warehouse-stock", response_model=ReportTableResponse)
def warehouse_stock_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).warehouse_stock(
        current_user=current_user,
        tenant_id=tenant_id,
        warehouse_id=warehouse_id,
        product_id=product_id,
        category_id=category_id,
    )
    return report_response(
        report_name="Warehouse Stock",
        rows=rows,
        filters=filter_payload(tenant_id=tenant_id, warehouse_id=warehouse_id, product_id=product_id, category_id=category_id),
        export=export,
    )


@router.get("/product-valuation", response_model=ReportTableResponse)
def product_valuation_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).product_valuation(
        current_user=current_user,
        tenant_id=tenant_id,
        warehouse_id=warehouse_id,
        product_id=product_id,
        category_id=category_id,
    )
    return report_response(
        report_name="Product Valuation",
        rows=rows,
        filters=filter_payload(tenant_id=tenant_id, warehouse_id=warehouse_id, product_id=product_id, category_id=category_id),
        export=export,
    )


@router.get("/purchase-orders", response_model=ReportTableResponse)
def purchase_order_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    vendor_id: int | None = Query(default=None),
    status_filter: PurchaseOrderStatusEnum | None = Query(default=None, alias="status"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).purchase_orders(
        current_user=current_user,
        tenant_id=tenant_id,
        vendor_id=vendor_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
    )
    return report_response(
        report_name="Purchase Orders",
        rows=rows,
        filters=filter_payload(tenant_id=tenant_id, vendor_id=vendor_id, status=status_filter.value if status_filter else None, date_from=date_from, date_to=date_to),
        export=export,
    )


@router.get("/vendor-purchase", response_model=ReportTableResponse)
def vendor_purchase_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    vendor_id: int | None = Query(default=None),
    status_filter: PurchaseOrderStatusEnum | None = Query(default=None, alias="status"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).vendor_purchase_summary(
        current_user=current_user,
        tenant_id=tenant_id,
        vendor_id=vendor_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
    )
    return report_response(
        report_name="Vendor Purchase Summary",
        rows=rows,
        filters=filter_payload(tenant_id=tenant_id, vendor_id=vendor_id, status=status_filter.value if status_filter else None, date_from=date_from, date_to=date_to),
        export=export,
    )


@router.get("/sales-orders", response_model=ReportTableResponse)
def sales_order_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    customer_id: int | None = Query(default=None),
    status_filter: SalesOrderStatusEnum | None = Query(default=None, alias="status"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).sales_orders(
        current_user=current_user,
        tenant_id=tenant_id,
        customer_id=customer_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
    )
    return report_response(
        report_name="Sales Orders",
        rows=rows,
        filters=filter_payload(tenant_id=tenant_id, customer_id=customer_id, status=status_filter.value if status_filter else None, date_from=date_from, date_to=date_to),
        export=export,
    )


@router.get("/customer-sales", response_model=ReportTableResponse)
def customer_sales_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    customer_id: int | None = Query(default=None),
    status_filter: SalesOrderStatusEnum | None = Query(default=None, alias="status"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).customer_sales_summary(
        current_user=current_user,
        tenant_id=tenant_id,
        customer_id=customer_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
    )
    return report_response(
        report_name="Customer Sales Summary",
        rows=rows,
        filters=filter_payload(tenant_id=tenant_id, customer_id=customer_id, status=status_filter.value if status_filter else None, date_from=date_from, date_to=date_to),
        export=export,
    )


@router.get("/inventory-adjustment", response_model=ReportTableResponse)
def inventory_adjustment_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    product_id: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).inventory_adjustments(
        current_user=current_user,
        tenant_id=tenant_id,
        warehouse_id=warehouse_id,
        product_id=product_id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
    )
    return report_response(
        report_name="Inventory Adjustments",
        rows=rows,
        filters=filter_payload(
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
        ),
        export=export,
    )


@router.get("/audit-logs", response_model=ReportTableResponse)
def audit_log_report(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    export: str | None = Query(default=None),
) -> ReportTableResponse | StreamingResponse:
    rows = ReportService(db).audit_logs(
        current_user=current_user,
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        date_from=date_from,
        date_to=date_to,
    )
    return report_response(
        report_name="Audit Logs",
        rows=rows,
        filters=filter_payload(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            date_from=date_from,
            date_to=date_to,
        ),
        export=export,
    )
