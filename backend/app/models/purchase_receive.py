from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import PurchaseReceiveStatusEnum


class PurchaseReceive(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "purchase_receives"
    __table_args__ = (
        UniqueConstraint("tenant_id", "receive_number", name="uq_purchase_receives_tenant_number"),
        Index("ix_purchase_receives_tenant_status", "tenant_id", "status"),
        Index("ix_purchase_receives_tenant_purchase_order", "tenant_id", "purchase_order_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"), nullable=False, index=True)
    receive_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    received_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[PurchaseReceiveStatusEnum] = mapped_column(
        Enum(PurchaseReceiveStatusEnum, name="purchase_receive_status_enum"),
        nullable=False,
        default=PurchaseReceiveStatusEnum.POSTED,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
