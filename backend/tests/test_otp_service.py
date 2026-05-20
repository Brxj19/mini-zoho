from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException

from app.models.enums import OtpChallengeStatusEnum, OtpChannelEnum, OtpPurposeEnum
from app.services import email_service as email_service_module
from app.services import otp_service as otp_service_module
from app.services.otp_service import OtpService


def test_create_and_verify_email_otp(db, tenant_context, monkeypatch):
    monkeypatch.setattr(otp_service_module.settings, "env", "development")
    monkeypatch.setattr(email_service_module.settings, "email_enabled", False)

    service = OtpService(db)
    challenge, raw_code = service.create_otp(
        destination=tenant_context.user.email,
        channel=OtpChannelEnum.EMAIL,
        purpose=OtpPurposeEnum.SIGNUP_VERIFY,
        tenant_id=tenant_context.tenant.id,
        user_id=tenant_context.user.id,
    )

    assert raw_code is not None
    assert challenge.dev_plaintext_code == raw_code
    verified = service.verify_otp(challenge_id=challenge.id, code=raw_code)
    assert verified.status == OtpChallengeStatusEnum.VERIFIED
    assert verified.consumed_at is not None


def test_invalid_otp_increments_attempts(db, tenant_context, monkeypatch):
    monkeypatch.setattr(otp_service_module.settings, "env", "development")
    monkeypatch.setattr(email_service_module.settings, "email_enabled", False)

    service = OtpService(db)
    challenge, _raw_code = service.create_otp(
        destination=tenant_context.user.email,
        channel=OtpChannelEnum.EMAIL,
        purpose=OtpPurposeEnum.SIGNUP_VERIFY,
        tenant_id=tenant_context.tenant.id,
        user_id=tenant_context.user.id,
    )

    with pytest.raises(HTTPException) as exc:
        service.verify_otp(challenge_id=challenge.id, code="000000")

    assert exc.value.status_code == 400
    db.refresh(challenge)
    assert challenge.attempts == 1
    assert challenge.status == OtpChallengeStatusEnum.PENDING


def test_expire_old_otps_marks_pending_records_expired(db, tenant_context, monkeypatch):
    monkeypatch.setattr(otp_service_module.settings, "env", "development")
    monkeypatch.setattr(email_service_module.settings, "email_enabled", False)

    service = OtpService(db)
    challenge, _raw_code = service.create_otp(
        destination=tenant_context.user.email,
        channel=OtpChannelEnum.EMAIL,
        purpose=OtpPurposeEnum.SIGNUP_VERIFY,
        tenant_id=tenant_context.tenant.id,
        user_id=tenant_context.user.id,
    )
    challenge.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    db.add(challenge)
    db.flush()

    expired = service.expire_old_otps()
    db.refresh(challenge)

    assert expired == 1
    assert challenge.status == OtpChallengeStatusEnum.EXPIRED
