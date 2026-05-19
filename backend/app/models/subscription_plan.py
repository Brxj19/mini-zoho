from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SubscriptionPlan(TimestampMixin, Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    monthly_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    annual_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    max_users: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_products: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_warehouses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_monthly_sales_orders: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_monthly_purchase_orders: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_monthly_stock_transfers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    barcode_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    advanced_inventory_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    integrations_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_assistant_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
