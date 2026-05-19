from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import SalesReturnStatusEnum


class SalesReturn(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "sales_returns"
    __table_args__ = (
        UniqueConstraint("tenant_id", "return_number", name="uq_sales_returns_tenant_number"),
        Index("ix_sales_returns_tenant_status", "tenant_id", "status"),
        Index("ix_sales_returns_tenant_sales_order", "tenant_id", "sales_order_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sales_order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    return_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    return_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[SalesReturnStatusEnum] = mapped_column(
        Enum(SalesReturnStatusEnum, name="sales_return_status_enum"),
        nullable=False,
        default=SalesReturnStatusEnum.DRAFT,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
