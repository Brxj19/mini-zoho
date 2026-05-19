from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AIAssistantRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    tenant_id: int | None = None


class AIAssistantFact(BaseModel):
    label: str
    value: str | int | float


class AIAssistantResponse(BaseModel):
    answer: str
    facts: list[AIAssistantFact]
    generated_at: datetime


class ReorderSuggestionResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    warehouse_id: int
    warehouse_name: str
    available_quantity: int
    reorder_level: int
    last_30d_demand: int
    recommended_quantity: int
    reason: str


class ReorderSuggestionListResponse(BaseModel):
    items: list[ReorderSuggestionResponse]
    generated_at: datetime


class ReportSummaryRequest(BaseModel):
    report_key: str = Field(min_length=2, max_length=100)
    tenant_id: int | None = None


class ReportSummaryResponse(BaseModel):
    report_key: str
    summary: str
    generated_at: datetime


class IntegrationCatalogItem(BaseModel):
    key: str
    name: str
    category: str
    status: str
    configured: bool
    description: str


class IntegrationCatalogResponse(BaseModel):
    items: list[IntegrationCatalogItem]
