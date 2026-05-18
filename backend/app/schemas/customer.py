from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import RecordStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    gst_number: str | None = Field(default=None, max_length=64)
    billing_address: str | None = None
    shipping_address: str | None = None
    status: RecordStatusEnum = RecordStatusEnum.ACTIVE


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    gst_number: str | None = Field(default=None, max_length=64)
    billing_address: str | None = None
    shipping_address: str | None = None
    status: RecordStatusEnum | None = None


class CustomerResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    name: str
    email: EmailStr | None
    phone: str | None
    gst_number: str | None
    billing_address: str | None
    shipping_address: str | None
    status: RecordStatusEnum
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    meta: PaginationMeta
