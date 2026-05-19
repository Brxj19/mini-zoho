from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import TenantStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class TenantBase(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    contact_email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = None
    gst_number: str | None = Field(default=None, max_length=64)
    business_type: str | None = Field(default=None, max_length=128)


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


class TenantStatusUpdate(BaseModel):
    status: TenantStatusEnum


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
    created_at: datetime
    updated_at: datetime


class TenantListResponse(BaseModel):
    items: list[TenantResponse]
    meta: PaginationMeta


class TenantUsageResponse(BaseModel):
    tenant_id: int
    total_users: int
    active_users: int
    total_products: int = 0
    total_warehouses: int = 0
    total_orders: int = 0
    total_purchase_orders: int = 0
    total_sales_orders: int = 0
    total_stock_transfers: int = 0
