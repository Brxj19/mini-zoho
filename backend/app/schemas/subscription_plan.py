from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMBaseSchema, PaginationMeta


class SubscriptionPlanBase(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    monthly_price: Decimal = Field(default=0, ge=0)
    annual_price: Decimal = Field(default=0, ge=0)
    max_users: int | None = Field(default=None, ge=1)
    max_products: int | None = Field(default=None, ge=1)
    max_warehouses: int | None = Field(default=None, ge=1)
    max_monthly_sales_orders: int | None = Field(default=None, ge=1)
    max_monthly_purchase_orders: int | None = Field(default=None, ge=1)
    max_monthly_stock_transfers: int | None = Field(default=None, ge=1)
    barcode_enabled: bool = True
    advanced_inventory_enabled: bool = False
    integrations_enabled: bool = False
    ai_assistant_enabled: bool = False


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=64)
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    monthly_price: Decimal | None = Field(default=None, ge=0)
    annual_price: Decimal | None = Field(default=None, ge=0)
    max_users: int | None = Field(default=None, ge=1)
    max_products: int | None = Field(default=None, ge=1)
    max_warehouses: int | None = Field(default=None, ge=1)
    max_monthly_sales_orders: int | None = Field(default=None, ge=1)
    max_monthly_purchase_orders: int | None = Field(default=None, ge=1)
    max_monthly_stock_transfers: int | None = Field(default=None, ge=1)
    barcode_enabled: bool | None = None
    advanced_inventory_enabled: bool | None = None
    integrations_enabled: bool | None = None
    ai_assistant_enabled: bool | None = None


class SubscriptionPlanResponse(ORMBaseSchema):
    id: int
    code: str
    name: str
    description: str | None
    monthly_price: Decimal
    annual_price: Decimal
    max_users: int | None
    max_products: int | None
    max_warehouses: int | None
    max_monthly_sales_orders: int | None
    max_monthly_purchase_orders: int | None
    max_monthly_stock_transfers: int | None
    barcode_enabled: bool
    advanced_inventory_enabled: bool
    integrations_enabled: bool
    ai_assistant_enabled: bool
    created_at: datetime
    updated_at: datetime


class SubscriptionPlanListResponse(BaseModel):
    items: list[SubscriptionPlanResponse]
    meta: PaginationMeta
