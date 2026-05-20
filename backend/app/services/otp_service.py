from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.models.enums import OtpChallengeStatusEnum, OtpChannelEnum, OtpPurposeEnum
from app.models.otp_challenge import OtpChallenge
from app.services.email_service import EmailService
from app.services.sms_service import SmsService

settings = get_settings()


class OtpService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.email_service = EmailService(db)
        self.sms_service = SmsService(db)

    def create_otp(
        self,
        *,
        destination: str,
        channel: OtpChannelEnum,
        purpose: OtpPurposeEnum,
        tenant_id: int | None = None,
        user_id: int | None = None,
    ) -> tuple[OtpChallenge, str | None]:
        code = f"{secrets.randbelow(1_000_000):06d}"
        challenge = OtpChallenge(
            tenant_id=tenant_id,
            user_id=user_id,
            channel=channel,
            purpose=purpose,
            destination=destination.strip(),
            otp_hash=hash_password(code),
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.otp_ttl_minutes),
            attempts=0,
            max_attempts=settings.otp_max_attempts,
            status=OtpChallengeStatusEnum.PENDING,
            dev_plaintext_code=code if settings.env.lower() == "development" else None,
        )
        self.db.add(challenge)
        self.db.flush()
        self._dispatch_otp(challenge=challenge, code=code)
        return challenge, code if settings.env.lower() == "development" else None

    def verify_otp(self, *, challenge_id: int, code: str) -> OtpChallenge:
        challenge = self._get_challenge(challenge_id)
        self._expire_if_needed(challenge)
        if challenge.status != OtpChallengeStatusEnum.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This OTP challenge is no longer active.")
        if challenge.attempts >= challenge.max_attempts:
            challenge.status = OtpChallengeStatusEnum.BLOCKED
            self.db.add(challenge)
            self.db.flush()
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="OTP verification attempts exceeded.")

        challenge.attempts += 1
        if not verify_password(code, challenge.otp_hash):
            if challenge.attempts >= challenge.max_attempts:
                challenge.status = OtpChallengeStatusEnum.BLOCKED
            self.db.add(challenge)
            self.db.flush()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code.")

        challenge.status = OtpChallengeStatusEnum.VERIFIED
        challenge.consumed_at = datetime.now(UTC)
        self.db.add(challenge)
        self.db.flush()
        return challenge

    def resend_otp(self, *, challenge_id: int) -> tuple[OtpChallenge, str | None]:
        challenge = self._get_challenge(challenge_id)
        if challenge.status == OtpChallengeStatusEnum.VERIFIED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This OTP challenge is already verified.")
        challenge.status = OtpChallengeStatusEnum.EXPIRED
        self.db.add(challenge)
        self.db.flush()
        return self.create_otp(
            destination=challenge.destination,
            channel=challenge.channel,
            purpose=challenge.purpose,
            tenant_id=challenge.tenant_id,
            user_id=challenge.user_id,
        )

    def expire_old_otps(self) -> int:
        now = datetime.now(UTC)
        challenges = list(
            self.db.scalars(
                select(OtpChallenge).where(
                    OtpChallenge.status == OtpChallengeStatusEnum.PENDING,
                    OtpChallenge.expires_at < now,
                )
            ).all()
        )
        for challenge in challenges:
            challenge.status = OtpChallengeStatusEnum.EXPIRED
            self.db.add(challenge)
        self.db.flush()
        return len(challenges)

    def _dispatch_otp(self, *, challenge: OtpChallenge, code: str) -> None:
        message = f"Your Northstar Inventory verification code is {code}. It expires in {settings.otp_ttl_minutes} minutes."
        if challenge.channel == OtpChannelEnum.EMAIL:
            self.email_service.send_template_email(
                template_name="otp_email",
                context={"code": code, "purpose": challenge.purpose.value.replace("_", " ").title(), "ttl_minutes": settings.otp_ttl_minutes},
                to=challenge.destination,
                subject="Your Northstar Inventory verification code",
                tenant_id=challenge.tenant_id,
                user_id=challenge.user_id,
            )
            return
        self.sms_service.send_sms(
            tenant_id=challenge.tenant_id,
            to=challenge.destination,
            message=message,
        )

    def _get_challenge(self, challenge_id: int) -> OtpChallenge:
        challenge = self.db.get(OtpChallenge, challenge_id)
        if not challenge:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP challenge not found.")
        return challenge

    def _expire_if_needed(self, challenge: OtpChallenge) -> None:
        if challenge.status == OtpChallengeStatusEnum.PENDING and challenge.expires_at < datetime.now(UTC):
            challenge.status = OtpChallengeStatusEnum.EXPIRED
            self.db.add(challenge)
            self.db.flush()
