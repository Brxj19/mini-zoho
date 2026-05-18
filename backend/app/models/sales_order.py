from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import SalesOrderStatusEnum


class SalesOrder(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "sales_orders"
    __table_args__ = (
        UniqueConstraint("tenant_id", "so_number", name="uq_sales_orders_tenant_number"),
        Index("ix_sales_orders_tenant_status", "tenant_id", "status"),
        Index("ix_sales_orders_tenant_customer", "tenant_id", "customer_id"),
        Index("ix_sales_orders_tenant_order_date", "tenant_id", "order_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    so_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[SalesOrderStatusEnum] = mapped_column(
        Enum(SalesOrderStatusEnum, name="sales_order_status_enum"),
        nullable=False,
        default=SalesOrderStatusEnum.DRAFT,
        index=True,
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
