from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import BillStatusEnum
from app.models.enums import InvoiceStatusEnum
from app.models.enums import PackageStatusEnum
from app.models.enums import PurchaseReceiveStatusEnum
from app.models.enums import SalesReturnStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class WorkflowActionPayload(BaseModel):
    notes: str | None = None


class PackageItemInput(BaseModel):
    sales_order_item_id: int
    quantity: int = Field(gt=0)


class PackageCreate(BaseModel):
    sales_order_id: int
    package_number: str = Field(min_length=1, max_length=100)
    notes: str | None = None
    items: list[PackageItemInput] = Field(min_length=1)


class PackageItemResponse(ORMBaseSchema):
    id: int
    package_id: int
    sales_order_item_id: int
    product_id: int
    warehouse_id: int
    quantity: int


class PackageResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    sales_order_id: int
    package_number: str
    status: PackageStatusEnum
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[PackageItemResponse]


class PackageListResponse(BaseModel):
    items: list[PackageResponse]
    meta: PaginationMeta


class InvoiceCreate(BaseModel):
    sales_order_id: int
    invoice_number: str = Field(min_length=1, max_length=100)
    invoice_date: date
    due_date: date | None = None
    notes: str | None = None


class InvoiceResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    sales_order_id: int
    customer_id: int
    invoice_number: str
    invoice_date: date
    due_date: date | None
    status: InvoiceStatusEnum
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    meta: PaginationMeta


class SalesReturnItemInput(BaseModel):
    sales_order_item_id: int
    warehouse_id: int
    quantity: int = Field(gt=0)
    reason: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class SalesReturnCreate(BaseModel):
    sales_order_id: int
    return_number: str = Field(min_length=1, max_length=100)
    return_date: date
    notes: str | None = None
    items: list[SalesReturnItemInput] = Field(min_length=1)


class SalesReturnItemResponse(ORMBaseSchema):
    id: int
    sales_return_id: int
    sales_order_item_id: int
    product_id: int
    warehouse_id: int
    quantity: int
    reason: str | None
    notes: str | None


class SalesReturnResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    sales_order_id: int
    customer_id: int
    return_number: str
    return_date: date
    status: SalesReturnStatusEnum
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[SalesReturnItemResponse]


class SalesReturnListResponse(BaseModel):
    items: list[SalesReturnResponse]
    meta: PaginationMeta


class PurchaseReceiveItemInput(BaseModel):
    purchase_order_item_id: int
    quantity_received: int = Field(gt=0)


class PurchaseReceiveCreate(BaseModel):
    purchase_order_id: int
    receive_number: str = Field(min_length=1, max_length=100)
    received_at: date
    notes: str | None = None
    items: list[PurchaseReceiveItemInput] = Field(min_length=1)


class PurchaseReceiveItemResponse(ORMBaseSchema):
    id: int
    purchase_receive_id: int
    purchase_order_item_id: int
    product_id: int
    warehouse_id: int
    quantity_received: int


class PurchaseReceiveResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    purchase_order_id: int
    vendor_id: int
    receive_number: str
    received_at: date
    status: PurchaseReceiveStatusEnum
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseReceiveItemResponse]


class PurchaseReceiveListResponse(BaseModel):
    items: list[PurchaseReceiveResponse]
    meta: PaginationMeta


class BillCreate(BaseModel):
    purchase_order_id: int
    bill_number: str = Field(min_length=1, max_length=100)
    bill_date: date
    due_date: date | None = None
    notes: str | None = None


class BillResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    purchase_order_id: int
    vendor_id: int
    bill_number: str
    bill_date: date
    due_date: date | None
    status: BillStatusEnum
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime


class BillListResponse(BaseModel):
    items: list[BillResponse]
    meta: PaginationMeta
