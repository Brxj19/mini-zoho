from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import BillStatusEnum


class Bill(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "bills"
    __table_args__ = (
        UniqueConstraint("tenant_id", "bill_number", name="uq_bills_tenant_number"),
        Index("ix_bills_tenant_status", "tenant_id", "status"),
        Index("ix_bills_tenant_purchase_order", "tenant_id", "purchase_order_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"), nullable=False, index=True)
    bill_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    bill_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[BillStatusEnum] = mapped_column(
        Enum(BillStatusEnum, name="bill_status_enum"),
        nullable=False,
        default=BillStatusEnum.DRAFT,
        index=True,
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
