from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import InventorySerialStatusEnum, InventoryTransactionTypeEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class BatchTrackingInput(BaseModel):
    batch_number: str = Field(min_length=1, max_length=128)
    expiry_date: date | None = None
    warranty_until: date | None = None


class StockInRequest(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int = Field(gt=0)
    note: str | None = None
    reference_type: str | None = Field(default=None, max_length=100)
    reference_id: int | None = None
    batch: BatchTrackingInput | None = None
    serial_numbers: list[str] = Field(default_factory=list)


class StockOutRequest(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int = Field(gt=0)
    note: str | None = None
    reference_type: str | None = Field(default=None, max_length=100)
    reference_id: int | None = None
    batch_number: str | None = Field(default=None, max_length=128)
    serial_numbers: list[str] = Field(default_factory=list)


class StockAdjustmentRequest(BaseModel):
    product_id: int
    warehouse_id: int
    quantity_delta: int
    note: str = Field(min_length=3)
    reference_type: str | None = Field(default=None, max_length=100)
    reference_id: int | None = None
    batch_number: str | None = Field(default=None, max_length=128)
    serial_numbers: list[str] = Field(default_factory=list)


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


class BarcodeGenerateResponse(BaseModel):
    barcode: str


class BarcodeSearchResponse(BaseModel):
    product_id: int
    name: str
    sku: str
    barcode: str | None


class InventoryBatchResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    product_id: int
    warehouse_id: int
    batch_number: str
    expiry_date: date | None
    warranty_until: date | None
    quantity: int
    available_quantity: int
    created_at: datetime
    updated_at: datetime


class InventoryBatchListResponse(BaseModel):
    items: list[InventoryBatchResponse]
    meta: PaginationMeta


class InventorySerialResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    product_id: int
    warehouse_id: int
    batch_id: int | None
    serial_number: str
    expires_on: date | None
    warranty_until: date | None
    status: InventorySerialStatusEnum
    created_at: datetime
    updated_at: datetime


class InventorySerialListResponse(BaseModel):
    items: list[InventorySerialResponse]
    meta: PaginationMeta
