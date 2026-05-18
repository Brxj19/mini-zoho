from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import InventoryTransactionTypeEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class StockInRequest(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int = Field(gt=0)
    note: str | None = None
    reference_type: str | None = Field(default=None, max_length=100)
    reference_id: int | None = None


class StockOutRequest(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int = Field(gt=0)
    note: str | None = None
    reference_type: str | None = Field(default=None, max_length=100)
    reference_id: int | None = None


class StockAdjustmentRequest(BaseModel):
    product_id: int
    warehouse_id: int
    quantity_delta: int
    note: str = Field(min_length=3)
    reference_type: str | None = Field(default=None, max_length=100)
    reference_id: int | None = None


class InventoryTransactionResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    product_id: int
    warehouse_id: int
    source_warehouse_id: int | None
    destination_warehouse_id: int | None
    transaction_type: InventoryTransactionTypeEnum
    quantity: int
    reference_type: str | None
    reference_id: int | None
    note: str | None
    created_by: int
    created_at: datetime


class InventoryTransactionListResponse(BaseModel):
    items: list[InventoryTransactionResponse]
    meta: PaginationMeta


class LowStockItemResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    warehouse_id: int
    warehouse_name: str
    available_quantity: int
    reorder_level: int


class LowStockListResponse(BaseModel):
    items: list[LowStockItemResponse]
    meta: PaginationMeta
