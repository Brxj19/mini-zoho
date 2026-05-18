from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import SalesOrderStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class SalesOrderItemInput(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(default=0, ge=0)
    tax_rate: Decimal = Field(default=0, ge=0)
    discount: Decimal = Field(default=0, ge=0)


class SalesOrderCreate(BaseModel):
    customer_id: int
    so_number: str = Field(min_length=1, max_length=100)
    order_date: date
    notes: str | None = None
    items: list[SalesOrderItemInput] = Field(min_length=1)


class SalesOrderUpdate(BaseModel):
    customer_id: int | None = None
    so_number: str | None = Field(default=None, min_length=1, max_length=100)
    order_date: date | None = None
    notes: str | None = None
    items: list[SalesOrderItemInput] | None = None


class SalesOrderStatusAction(BaseModel):
    notes: str | None = None


class SalesOrderItemResponse(ORMBaseSchema):
    id: int
    sales_order_id: int
    product_id: int
    warehouse_id: int
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal
    discount: Decimal
    total_price: Decimal


class SalesOrderResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    customer_id: int
    so_number: str
    order_date: date
    status: SalesOrderStatusEnum
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[SalesOrderItemResponse]


class SalesOrderListResponse(BaseModel):
    items: list[SalesOrderResponse]
    meta: PaginationMeta
