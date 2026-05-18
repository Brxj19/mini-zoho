from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import RecordStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class VendorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    gst_number: str | None = Field(default=None, max_length=64)
    address: str | None = None
    opening_balance: Decimal | None = None
    status: RecordStatusEnum = RecordStatusEnum.ACTIVE


class VendorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    gst_number: str | None = Field(default=None, max_length=64)
    address: str | None = None
    opening_balance: Decimal | None = None
    status: RecordStatusEnum | None = None


class VendorResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    name: str
    email: EmailStr | None
    phone: str | None
    gst_number: str | None
    address: str | None
    opening_balance: Decimal | None
    status: RecordStatusEnum
    created_at: datetime
    updated_at: datetime


class VendorListResponse(BaseModel):
    items: list[VendorResponse]
    meta: PaginationMeta
