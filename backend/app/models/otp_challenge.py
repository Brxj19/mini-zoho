from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import OtpChallengeStatusEnum, OtpChannelEnum, OtpPurposeEnum


class OtpChallenge(TimestampMixin, Base):
    __tablename__ = "otp_challenges"
    __table_args__ = (
        Index("ix_otp_challenges_tenant_status", "tenant_id", "status"),
        Index("ix_otp_challenges_destination_status", "destination", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    channel: Mapped[OtpChannelEnum] = mapped_column(
        Enum(OtpChannelEnum, name="otp_channel_enum"),
        nullable=False,
        index=True,
    )
    purpose: Mapped[OtpPurposeEnum] = mapped_column(
        Enum(OtpPurposeEnum, name="otp_purpose_enum"),
        nullable=False,
        index=True,
    )
    destination: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    otp_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    status: Mapped[OtpChallengeStatusEnum] = mapped_column(
        Enum(OtpChallengeStatusEnum, name="otp_challenge_status_enum"),
        nullable=False,
        default=OtpChallengeStatusEnum.PENDING,
        index=True,
    )
    dev_plaintext_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
