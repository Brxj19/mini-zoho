from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import PaginationMeta


class SmsOutboxResponse(BaseModel):
    id: int
    tenant_id: int | None
    to_phone: str
    message: str
    provider: str
    status: str
    provider_message_id: str | None
    error_message: str | None
    created_at: datetime
    sent_at: datetime | None


class SmsOutboxListResponse(BaseModel):
    items: list[SmsOutboxResponse]
    meta: PaginationMeta


class EmailOutboxResponse(BaseModel):
    id: int
    tenant_id: int | None
    user_id: int | None
    to_email: str
    subject: str
    html_body: str
    text_body: str | None
    provider: str
    status: str
    error_message: str | None
    created_at: datetime
    sent_at: datetime | None


class EmailOutboxListResponse(BaseModel):
    items: list[EmailOutboxResponse]
    meta: PaginationMeta
