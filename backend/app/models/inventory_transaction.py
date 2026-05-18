from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin
from app.models.enums import InventoryTransactionTypeEnum


class InventoryTransaction(TenantOwnedMixin, Base):
    __tablename__ = "inventory_transactions"
    __table_args__ = (
        Index("ix_inventory_tx_tenant_product", "tenant_id", "product_id"),
        Index("ix_inventory_tx_tenant_warehouse", "tenant_id", "warehouse_id"),
        Index("ix_inventory_tx_tenant_type", "tenant_id", "transaction_type"),
        Index("ix_inventory_tx_tenant_created_by", "tenant_id", "created_by"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    source_warehouse_id: Mapped[int | None] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    destination_warehouse_id: Mapped[int | None] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    transaction_type: Mapped[InventoryTransactionTypeEnum] = mapped_column(
        Enum(InventoryTransactionTypeEnum, name="inventory_transaction_type_enum"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
