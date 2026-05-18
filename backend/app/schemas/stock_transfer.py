from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import StockTransferStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class StockTransferItemInput(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class StockTransferCreate(BaseModel):
    source_warehouse_id: int
    destination_warehouse_id: int
    notes: str | None = None
    items: list[StockTransferItemInput] = Field(min_length=1)


class StockTransferUpdate(BaseModel):
    source_warehouse_id: int | None = None
    destination_warehouse_id: int | None = None
    notes: str | None = None
    items: list[StockTransferItemInput] | None = None


class StockTransferStatusAction(BaseModel):
    notes: str | None = None


class StockTransferItemResponse(ORMBaseSchema):
    id: int
    stock_transfer_id: int
    product_id: int
    quantity: int


class StockTransferResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    source_warehouse_id: int
    destination_warehouse_id: int
    status: StockTransferStatusEnum
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: list[StockTransferItemResponse]


class StockTransferListResponse(BaseModel):
    items: list[StockTransferResponse]
    meta: PaginationMeta
