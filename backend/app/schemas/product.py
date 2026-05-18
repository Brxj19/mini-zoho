from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import RecordStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    sku: str = Field(min_length=1, max_length=100)
    barcode: str | None = Field(default=None, max_length=100)
    category_id: int | None = None
    brand_id: int | None = None
    vendor_id: int | None = None
    description: str | None = None
    unit: str = Field(default="unit", min_length=1, max_length=64)
    cost_price: Decimal = Field(default=0, ge=0)
    selling_price: Decimal = Field(default=0, ge=0)
    reorder_level: int = Field(default=0, ge=0)
    status: RecordStatusEnum = RecordStatusEnum.ACTIVE


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    barcode: str | None = Field(default=None, max_length=100)
    category_id: int | None = None
    brand_id: int | None = None
    vendor_id: int | None = None
    description: str | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=64)
    cost_price: Decimal | None = Field(default=None, ge=0)
    selling_price: Decimal | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)
    status: RecordStatusEnum | None = None


class ProductResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    name: str
    sku: str
    barcode: str | None
    category_id: int | None
    brand_id: int | None
    vendor_id: int | None
    description: str | None
    unit: str
    cost_price: Decimal
    selling_price: Decimal
    reorder_level: int
    status: RecordStatusEnum
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    meta: PaginationMeta


class ProductStockItem(BaseModel):
    warehouse_id: int
    quantity: int
    reserved_quantity: int
    available_quantity: int
    reorder_level: int | None


class ProductStockSummaryResponse(BaseModel):
    product_id: int
    total_quantity: int
    reserved_quantity: int
    available_quantity: int
    warehouses: list[ProductStockItem]
