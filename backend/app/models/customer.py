from __future__ import annotations

from sqlalchemy import Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import RecordStatusEnum


class Customer(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_tenant_name", "tenant_id", "name"),
        Index("ix_customers_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    billing_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[RecordStatusEnum] = mapped_column(
        Enum(RecordStatusEnum, name="record_status_enum"),
        nullable=False,
        default=RecordStatusEnum.ACTIVE,
        index=True,
    )
