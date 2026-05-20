from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import TenantStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta
from app.schemas.subscription_plan import SubscriptionPlanResponse


class TenantBase(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    contact_email: str = Field(min_length=3, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = None
    gst_number: str | None = Field(default=None, max_length=64)
    business_type: str | None = Field(default=None, max_length=128)
    subscription_plan_id: int | None = None

    @field_validator("contact_email")
    @classmethod
    def normalize_contact_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("Enter a valid contact email.")
        return normalized


class TenantCreate(TenantBase):
    admin_name: str | None = Field(default=None, min_length=2, max_length=255)
    admin_email: str | None = Field(default=None, min_length=3, max_length=255)
    admin_password: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("admin_email")
    @classmethod
    def normalize_admin_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("Enter a valid admin email.")
        return normalized


class TenantUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=2, max_length=255)
    contact_email: str | None = Field(default=None, min_length=3, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = None
    gst_number: str | None = Field(default=None, max_length=64)
    business_type: str | None = Field(default=None, max_length=128)
    subscription_plan_id: int | None = None

    @field_validator("contact_email")
    @classmethod
    def normalize_optional_contact_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("Enter a valid contact email.")
        return normalized


class TenantStatusUpdate(BaseModel):
    status: TenantStatusEnum


class TenantPlanAssignment(BaseModel):
    subscription_plan_id: int


class TenantResponse(ORMBaseSchema):
    id: int
    company_name: str
    contact_email: str
    phone: str | None
    address: str | None
    gst_number: str | None
    business_type: str | None
    status: TenantStatusEnum
    subscription_plan_id: int | None
    subscription_plan: SubscriptionPlanResponse | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("contact_email")
    @classmethod
    def normalize_response_contact_email(cls, value: str) -> str:
        return value.strip().lower()


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
