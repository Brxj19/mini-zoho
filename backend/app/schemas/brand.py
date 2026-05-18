from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import RecordStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta


class BrandCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    status: RecordStatusEnum = RecordStatusEnum.ACTIVE


class BrandUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    status: RecordStatusEnum | None = None


class BrandResponse(ORMBaseSchema):
    id: int
    tenant_id: int
    name: str
    description: str | None
    status: RecordStatusEnum
    created_at: datetime
    updated_at: datetime


class BrandListResponse(BaseModel):
    items: list[BrandResponse]
    meta: PaginationMeta
