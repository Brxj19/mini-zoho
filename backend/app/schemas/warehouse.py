from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import RecordStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class WarehouseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    code: str = Field(min_length=2, max_length=64)
    address: str | None = None
    city: str | None = Field(default=None, max_length=128)
    state: str | None = Field(default=None, max_length=128)
    country: str | None = Field(default=None, max_length=128)
    manager_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    is_default: bool = False
    status: RecordStatusEnum = RecordStatusEnum.ACTIVE


class WarehouseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    code: str | None = Field(default=None, min_length=2, max_length=64)
    address: str | None = None
    city: str | None = Field(default=None, max_length=128)
    state: str | None = Field(default=None, max_length=128)
    country: str | None = Field(default=None, max_length=128)
    manager_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    is_default: bool | None = None
    status: RecordStatusEnum | None = None


class WarehouseResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    name: str
    code: str
    address: str | None
    city: str | None
    state: str | None
    country: str | None
    manager_name: str | None
    phone: str | None
    is_default: bool
    status: RecordStatusEnum
    created_at: datetime
    updated_at: datetime


class WarehouseListResponse(BaseModel):
    items: list[WarehouseResponse]
    meta: PaginationMeta
