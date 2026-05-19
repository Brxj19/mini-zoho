from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import BillStatusEnum, InvoiceStatusEnum, PackageStatusEnum, RoleEnum, SalesReturnStatusEnum
from app.models.user import User
from app.schemas.business_workflow import (
    BillCreate,
    BillListResponse,
    BillResponse,
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    PackageCreate,
    PackageItemResponse,
    PackageListResponse,
    PackageResponse,
    PurchaseReceiveCreate,
    PurchaseReceiveItemResponse,
    PurchaseReceiveListResponse,
    PurchaseReceiveResponse,
    SalesReturnCreate,
    SalesReturnItemResponse,
    SalesReturnListResponse,
    SalesReturnResponse,
    WorkflowActionPayload,
)
from app.schemas.common import PaginationMeta
from app.services.business_workflow_service import BusinessWorkflowService

router = APIRouter()


def request_meta(request: Request) -> dict[str, str | None]:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


def serialize_package(package, items) -> PackageResponse:
    return PackageResponse(
        id=package.id,
        tenant_id=package.tenant_id,
        sales_order_id=package.sales_order_id,
        package_number=package.package_number,
        status=package.status,
        notes=package.notes,
        created_by=package.created_by,
        created_at=package.created_at,
        updated_at=package.updated_at,
        items=[PackageItemResponse.model_validate(item) for item in items],
    )


def serialize_sales_return(sales_return, items) -> SalesReturnResponse:
    return SalesReturnResponse(
        id=sales_return.id,
        tenant_id=sales_return.tenant_id,
        sales_order_id=sales_return.sales_order_id,
        customer_id=sales_return.customer_id,
        return_number=sales_return.return_number,
        return_date=sales_return.return_date,
        status=sales_return.status,
        notes=sales_return.notes,
        created_by=sales_return.created_by,
        created_at=sales_return.created_at,
        updated_at=sales_return.updated_at,
        items=[SalesReturnItemResponse.model_validate(item) for item in items],
    )


def serialize_purchase_receive(purchase_receive, items) -> PurchaseReceiveResponse:
    return PurchaseReceiveResponse(
        id=purchase_receive.id,
        tenant_id=purchase_receive.tenant_id,
        purchase_order_id=purchase_receive.purchase_order_id,
        vendor_id=purchase_receive.vendor_id,
        receive_number=purchase_receive.receive_number,
        received_at=purchase_receive.received_at,
        status=purchase_receive.status,
        notes=purchase_receive.notes,
        created_by=purchase_receive.created_by,
        created_at=purchase_receive.created_at,
        updated_at=purchase_receive.updated_at,
        items=[PurchaseReceiveItemResponse.model_validate(item) for item in items],
    )


@router.get("/packages", response_model=PackageListResponse)
def list_packages(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    status_filter: PackageStatusEnum | None = Query(default=None, alias="status"),
    sales_order_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
) -> PackageListResponse:
    page, page_size = pagination
    service = BusinessWorkflowService(db)
    records, total = service.list_packages(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        status_filter=status_filter,
        sales_order_id=sales_order_id,
        search=search,
    )
    items = [serialize_package(record, service.get_package_for_user(current_user=current_user, package_id=record.id)[1]) for record in records]
    return PackageListResponse(items=items, meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/packages", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
def create_package(
    payload: PackageCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
    tenant_id: int | None = Query(default=None),
) -> PackageResponse:
    record, items = BusinessWorkflowService(db).create_package(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return serialize_package(record, items)


@router.get("/packages/{package_id}", response_model=PackageResponse)
def get_package(package_id: int, db: DbSession, current_user: CurrentUser) -> PackageResponse:
    record, items = BusinessWorkflowService(db).get_package_for_user(current_user=current_user, package_id=package_id)
    return serialize_package(record, items)


@router.post("/packages/{package_id}/pack", response_model=PackageResponse)
def pack_package(
    package_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> PackageResponse:
    record, items = BusinessWorkflowService(db).transition_package(current_user=current_user, package_id=package_id, next_status=PackageStatusEnum.PACKED, notes=payload.notes)
    return serialize_package(record, items)


@router.post("/packages/{package_id}/ship", response_model=PackageResponse)
def ship_package(
    package_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> PackageResponse:
    record, items = BusinessWorkflowService(db).transition_package(current_user=current_user, package_id=package_id, next_status=PackageStatusEnum.SHIPPED, notes=payload.notes)
    return serialize_package(record, items)


@router.post("/packages/{package_id}/deliver", response_model=PackageResponse)
def deliver_package(
    package_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> PackageResponse:
    record, items = BusinessWorkflowService(db).transition_package(current_user=current_user, package_id=package_id, next_status=PackageStatusEnum.DELIVERED, notes=payload.notes)
    return serialize_package(record, items)


@router.post("/packages/{package_id}/cancel", response_model=PackageResponse)
def cancel_package(
    package_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> PackageResponse:
    record, items = BusinessWorkflowService(db).transition_package(current_user=current_user, package_id=package_id, next_status=PackageStatusEnum.CANCELLED, notes=payload.notes)
    return serialize_package(record, items)


@router.get("/invoices", response_model=InvoiceListResponse)
def list_invoices(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    status_filter: InvoiceStatusEnum | None = Query(default=None, alias="status"),
    customer_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
) -> InvoiceListResponse:
    page, page_size = pagination
    items, total = BusinessWorkflowService(db).list_invoices(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        status_filter=status_filter,
        customer_id=customer_id,
        search=search,
    )
    return InvoiceListResponse(items=[InvoiceResponse.model_validate(item) for item in items], meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
    tenant_id: int | None = Query(default=None),
) -> InvoiceResponse:
    return InvoiceResponse.model_validate(BusinessWorkflowService(db).create_invoice(current_user=current_user, payload=payload, tenant_id=tenant_id))


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: DbSession, current_user: CurrentUser) -> InvoiceResponse:
    return InvoiceResponse.model_validate(BusinessWorkflowService(db).get_invoice_for_user(current_user=current_user, invoice_id=invoice_id))


@router.post("/invoices/{invoice_id}/send", response_model=InvoiceResponse)
def send_invoice(
    invoice_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> InvoiceResponse:
    return InvoiceResponse.model_validate(BusinessWorkflowService(db).transition_invoice(current_user=current_user, invoice_id=invoice_id, next_status=InvoiceStatusEnum.SENT, notes=payload.notes))


@router.post("/invoices/{invoice_id}/pay", response_model=InvoiceResponse)
def pay_invoice(
    invoice_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> InvoiceResponse:
    return InvoiceResponse.model_validate(BusinessWorkflowService(db).transition_invoice(current_user=current_user, invoice_id=invoice_id, next_status=InvoiceStatusEnum.PAID, notes=payload.notes))


@router.post("/invoices/{invoice_id}/void", response_model=InvoiceResponse)
def void_invoice(
    invoice_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> InvoiceResponse:
    return InvoiceResponse.model_validate(BusinessWorkflowService(db).transition_invoice(current_user=current_user, invoice_id=invoice_id, next_status=InvoiceStatusEnum.VOID, notes=payload.notes))


@router.get("/sales-returns", response_model=SalesReturnListResponse)
def list_sales_returns(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    status_filter: SalesReturnStatusEnum | None = Query(default=None, alias="status"),
    customer_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
) -> SalesReturnListResponse:
    page, page_size = pagination
    service = BusinessWorkflowService(db)
    records, total = service.list_sales_returns(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        status_filter=status_filter,
        customer_id=customer_id,
        search=search,
    )
    items = [serialize_sales_return(record, service.get_sales_return_for_user(current_user=current_user, sales_return_id=record.id)[1]) for record in records]
    return SalesReturnListResponse(items=items, meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/sales-returns", response_model=SalesReturnResponse, status_code=status.HTTP_201_CREATED)
def create_sales_return(
    payload: SalesReturnCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF, RoleEnum.INVENTORY_MANAGER)),
    tenant_id: int | None = Query(default=None),
) -> SalesReturnResponse:
    record, items = BusinessWorkflowService(db).create_sales_return(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return serialize_sales_return(record, items)


@router.get("/sales-returns/{sales_return_id}", response_model=SalesReturnResponse)
def get_sales_return(sales_return_id: int, db: DbSession, current_user: CurrentUser) -> SalesReturnResponse:
    record, items = BusinessWorkflowService(db).get_sales_return_for_user(current_user=current_user, sales_return_id=sales_return_id)
    return serialize_sales_return(record, items)


@router.post("/sales-returns/{sales_return_id}/receive", response_model=SalesReturnResponse)
def receive_sales_return(
    sales_return_id: int,
    payload: WorkflowActionPayload,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF, RoleEnum.INVENTORY_MANAGER)),
) -> SalesReturnResponse:
    record, items = BusinessWorkflowService(db).receive_sales_return(
        current_user=current_user,
        sales_return_id=sales_return_id,
        notes=payload.notes,
        request_meta=request_meta(request),
    )
    return serialize_sales_return(record, items)


@router.post("/sales-returns/{sales_return_id}/refund", response_model=SalesReturnResponse)
def refund_sales_return(
    sales_return_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> SalesReturnResponse:
    record, items = BusinessWorkflowService(db).refund_sales_return(current_user=current_user, sales_return_id=sales_return_id, notes=payload.notes)
    return serialize_sales_return(record, items)


@router.post("/sales-returns/{sales_return_id}/cancel", response_model=SalesReturnResponse)
def cancel_sales_return(
    sales_return_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> SalesReturnResponse:
    record, items = BusinessWorkflowService(db).cancel_sales_return(current_user=current_user, sales_return_id=sales_return_id, notes=payload.notes)
    return serialize_sales_return(record, items)


@router.get("/purchase-receives", response_model=PurchaseReceiveListResponse)
def list_purchase_receives(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    purchase_order_id: int | None = Query(default=None),
    vendor_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
) -> PurchaseReceiveListResponse:
    page, page_size = pagination
    service = BusinessWorkflowService(db)
    records, total = service.list_purchase_receives(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        purchase_order_id=purchase_order_id,
        vendor_id=vendor_id,
        search=search,
    )
    items = [serialize_purchase_receive(record, service.get_purchase_receive_for_user(current_user=current_user, purchase_receive_id=record.id)[1]) for record in records]
    return PurchaseReceiveListResponse(items=items, meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/purchase-receives", response_model=PurchaseReceiveResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_receive(
    payload: PurchaseReceiveCreate,
    request: Request,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF, RoleEnum.INVENTORY_MANAGER)),
    tenant_id: int | None = Query(default=None),
) -> PurchaseReceiveResponse:
    record, items = BusinessWorkflowService(db).create_purchase_receive(
        current_user=current_user,
        payload=payload,
        request_meta=request_meta(request),
        tenant_id=tenant_id,
    )
    return serialize_purchase_receive(record, items)


@router.get("/purchase-receives/{purchase_receive_id}", response_model=PurchaseReceiveResponse)
def get_purchase_receive(purchase_receive_id: int, db: DbSession, current_user: CurrentUser) -> PurchaseReceiveResponse:
    record, items = BusinessWorkflowService(db).get_purchase_receive_for_user(current_user=current_user, purchase_receive_id=purchase_receive_id)
    return serialize_purchase_receive(record, items)


@router.get("/bills", response_model=BillListResponse)
def list_bills(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    tenant_id: int | None = Query(default=None),
    status_filter: BillStatusEnum | None = Query(default=None, alias="status"),
    vendor_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
) -> BillListResponse:
    page, page_size = pagination
    items, total = BusinessWorkflowService(db).list_bills(
        current_user=current_user,
        page=page,
        page_size=page_size,
        tenant_id=tenant_id,
        status_filter=status_filter,
        vendor_id=vendor_id,
        search=search,
    )
    return BillListResponse(items=[BillResponse.model_validate(item) for item in items], meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.post("/bills", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
def create_bill(
    payload: BillCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF)),
    tenant_id: int | None = Query(default=None),
) -> BillResponse:
    return BillResponse.model_validate(BusinessWorkflowService(db).create_bill(current_user=current_user, payload=payload, tenant_id=tenant_id))


@router.get("/bills/{bill_id}", response_model=BillResponse)
def get_bill(bill_id: int, db: DbSession, current_user: CurrentUser) -> BillResponse:
    return BillResponse.model_validate(BusinessWorkflowService(db).get_bill_for_user(current_user=current_user, bill_id=bill_id))


@router.post("/bills/{bill_id}/post", response_model=BillResponse)
def post_bill(
    bill_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF)),
) -> BillResponse:
    return BillResponse.model_validate(BusinessWorkflowService(db).transition_bill(current_user=current_user, bill_id=bill_id, next_status=BillStatusEnum.POSTED, notes=payload.notes))


@router.post("/bills/{bill_id}/pay", response_model=BillResponse)
def pay_bill(
    bill_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF)),
) -> BillResponse:
    return BillResponse.model_validate(BusinessWorkflowService(db).transition_bill(current_user=current_user, bill_id=bill_id, next_status=BillStatusEnum.PAID, notes=payload.notes))


@router.post("/bills/{bill_id}/void", response_model=BillResponse)
def void_bill(
    bill_id: int,
    payload: WorkflowActionPayload,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.PURCHASE_STAFF)),
) -> BillResponse:
    return BillResponse.model_validate(BusinessWorkflowService(db).transition_bill(current_user=current_user, bill_id=bill_id, next_status=BillStatusEnum.VOID, notes=payload.notes))
