from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import TenantStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta
from app.schemas.subscription_plan import SubscriptionPlanResponse


class TenantBase(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    contact_email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = None
    gst_number: str | None = Field(default=None, max_length=64)
    business_type: str | None = Field(default=None, max_length=128)
    subscription_plan_id: int | None = None


class TenantCreate(TenantBase):
    admin_name: str | None = Field(default=None, min_length=2, max_length=255)
    admin_email: EmailStr | None = None
    admin_password: str | None = Field(default=None, min_length=8, max_length=128)


class TenantUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=2, max_length=255)
    contact_email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = None
    gst_number: str | None = Field(default=None, max_length=64)
    business_type: str | None = Field(default=None, max_length=128)
    subscription_plan_id: int | None = None


class TenantStatusUpdate(BaseModel):
    status: TenantStatusEnum


class TenantPlanAssignment(BaseModel):
    subscription_plan_id: int


class TenantResponse(ORMBaseSchema):
    id: int
    company_name: str
    contact_email: EmailStr
    phone: str | None
    address: str | None
    gst_number: str | None
    business_type: str | None
    status: TenantStatusEnum
    subscription_plan_id: int | None
    subscription_plan: SubscriptionPlanResponse | None = None
    created_at: datetime
    updated_at: datetime


class UsageLimitResponse(BaseModel):
    label: str
    current: int
    limit: int | None
    remaining: int | None
    percentage: float | None
    limit_reached: bool


class TenantListResponse(BaseModel):
    items: list[TenantResponse]
    meta: PaginationMeta


class TenantUsageResponse(BaseModel):
    tenant_id: int
    plan_id: int | None = None
    plan_code: str | None = None
    plan_name: str | None = None
    total_users: int
    active_users: int
    total_products: int = 0
    total_warehouses: int = 0
    total_orders: int = 0
    total_purchase_orders: int = 0
    total_sales_orders: int = 0
    total_stock_transfers: int = 0
    monthly_sales_orders: int = 0
    monthly_purchase_orders: int = 0
    monthly_stock_transfers: int = 0
    limits: dict[str, UsageLimitResponse] = {}
