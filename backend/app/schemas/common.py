from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PaginationMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)


class ORMBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
