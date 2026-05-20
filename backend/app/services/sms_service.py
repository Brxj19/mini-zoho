from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.sms_outbox import SmsOutbox

settings = get_settings()


class SmsProvider(Protocol):
    def send_sms(self, *, tenant_id: int | None, to: str, message: str) -> SmsOutbox:
        ...


class LocalSmsOutboxProvider:
    def __init__(self, db: Session) -> None:
        self.db = db

    def send_sms(self, *, tenant_id: int | None, to: str, message: str) -> SmsOutbox:
        outbox = SmsOutbox(
            tenant_id=tenant_id,
            to_phone=to,
            message=message,
            provider="local_outbox",
            status="SENT",
            sent_at=datetime.now(UTC),
        )
        self.db.add(outbox)
        self.db.flush()
        return outbox


class TwilioSmsProvider:
    def __init__(self, db: Session) -> None:
        self.db = db

    def send_sms(self, *, tenant_id: int | None, to: str, message: str) -> SmsOutbox:
        outbox = SmsOutbox(
            tenant_id=tenant_id,
            to_phone=to,
            message=message,
            provider="twilio",
            status="FAILED",
            error_message="Twilio provider is not configured in this development build.",
        )
        self.db.add(outbox)
        self.db.flush()
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Twilio SMS sending is not configured in this environment.",
        )


class SmsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.provider: SmsProvider = self._resolve_provider()

    def send_sms(self, *, tenant_id: int | None, to: str, message: str) -> SmsOutbox:
        return self.provider.send_sms(tenant_id=tenant_id, to=to, message=message)

    def list_outbox(self) -> list[SmsOutbox]:
        return list(self.db.scalars(select(SmsOutbox).order_by(SmsOutbox.created_at.desc())).all())

    def _resolve_provider(self) -> SmsProvider:
        if settings.env.lower() == "development" or settings.sms_provider.lower() == "local_outbox":
            return LocalSmsOutboxProvider(self.db)
        if settings.sms_provider.lower() == "twilio":
            return TwilioSmsProvider(self.db)
        return LocalSmsOutboxProvider(self.db)
