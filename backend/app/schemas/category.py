from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import RecordStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    status: RecordStatusEnum = RecordStatusEnum.ACTIVE


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    status: RecordStatusEnum | None = None


class CategoryResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    name: str
    description: str | None
    status: RecordStatusEnum
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    meta: PaginationMeta
