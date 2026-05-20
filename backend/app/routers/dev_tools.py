from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.config import get_settings
from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.models.email_outbox import EmailOutbox
from app.models.enums import RoleEnum
from app.models.sms_outbox import SmsOutbox
from app.schemas.common import PaginationMeta
from app.schemas.dev_tools import (
    EmailOutboxListResponse,
    EmailOutboxResponse,
    SmsOutboxListResponse,
    SmsOutboxResponse,
)

router = APIRouter()
settings = get_settings()


def _assert_dev_mode() -> None:
    if settings.env.lower() != "development":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Development tooling is disabled.")


@router.get("/sms-outbox", response_model=SmsOutboxListResponse)
def list_sms_outbox(
    db: DbSession,
    _: CurrentUser = Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> SmsOutboxListResponse:
    _assert_dev_mode()
    items = list(db.scalars(select(SmsOutbox).order_by(SmsOutbox.created_at.desc())).all())
    return SmsOutboxListResponse(
        items=[SmsOutboxResponse.model_validate(item, from_attributes=True) for item in items],
        meta=PaginationMeta(page=1, page_size=len(items) or 1, total=len(items)),
    )


@router.get("/email-outbox", response_model=EmailOutboxListResponse)
def list_email_outbox(
    db: DbSession,
    _: CurrentUser = Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> EmailOutboxListResponse:
    _assert_dev_mode()
    items = list(db.scalars(select(EmailOutbox).order_by(EmailOutbox.created_at.desc())).all())
    return EmailOutboxListResponse(
        items=[EmailOutboxResponse.model_validate(item, from_attributes=True) for item in items],
        meta=PaginationMeta(page=1, page_size=len(items) or 1, total=len(items)),
    )
