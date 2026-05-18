from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import PurchaseOrderStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class PurchaseOrderItemInput(BaseModel):
    product_id: int
    warehouse_id: int
    quantity_ordered: int = Field(gt=0)
    unit_price: Decimal = Field(default=0, ge=0)
    tax_rate: Decimal = Field(default=0, ge=0)


class PurchaseOrderCreate(BaseModel):
    vendor_id: int
    po_number: str = Field(min_length=1, max_length=100)
    order_date: date
    expected_delivery_date: date | None = None
    notes: str | None = None
    items: list[PurchaseOrderItemInput] = Field(min_length=1)


class PurchaseOrderUpdate(BaseModel):
    vendor_id: int | None = None
    po_number: str | None = Field(default=None, min_length=1, max_length=100)
    order_date: date | None = None
    expected_delivery_date: date | None = None
    notes: str | None = None
    items: list[PurchaseOrderItemInput] | None = None


class PurchaseOrderIssueAction(BaseModel):
    notes: str | None = None


class PurchaseOrderReceiveItemInput(BaseModel):
    purchase_order_item_id: int
    quantity_received: int = Field(gt=0)


class PurchaseOrderReceiveRequest(BaseModel):
    notes: str | None = None
    items: list[PurchaseOrderReceiveItemInput] = Field(min_length=1)


class PurchaseOrderItemResponse(ORMBaseSchema):
    id: int
    purchase_order_id: int
    product_id: int
    warehouse_id: int
    quantity_ordered: int
    quantity_received: int
    unit_price: Decimal
    tax_rate: Decimal
    total_price: Decimal


class PurchaseOrderResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    vendor_id: int
    po_number: str
    order_date: date
    expected_delivery_date: date | None
    status: PurchaseOrderStatusEnum
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseOrderItemResponse]


class PurchaseOrderListResponse(BaseModel):
    items: list[PurchaseOrderResponse]
    meta: PaginationMeta
