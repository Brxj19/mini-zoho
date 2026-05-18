from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Enum, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import RecordStatusEnum


class Vendor(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "vendors"
    __table_args__ = (
        Index("ix_vendors_tenant_name", "tenant_id", "name"),
        Index("ix_vendors_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    opening_balance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    status: Mapped[RecordStatusEnum] = mapped_column(
        Enum(RecordStatusEnum, name="record_status_enum"),
        nullable=False,
        default=RecordStatusEnum.ACTIVE,
        index=True,
    )
