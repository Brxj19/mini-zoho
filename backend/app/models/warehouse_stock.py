from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin


class WarehouseStock(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "warehouse_stock"
    __table_args__ = (
        UniqueConstraint("tenant_id", "warehouse_id", "product_id", name="uq_warehouse_stock_tenant_wh_product"),
        Index("ix_warehouse_stock_tenant_product", "tenant_id", "product_id"),
        Index("ix_warehouse_stock_tenant_warehouse", "tenant_id", "warehouse_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
