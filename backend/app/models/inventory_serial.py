from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import InventorySerialStatusEnum


class InventorySerial(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "inventory_serials"
    __table_args__ = (
        UniqueConstraint("tenant_id", "serial_number", name="uq_inventory_serials_tenant_serial"),
        Index("ix_inventory_serials_tenant_product", "tenant_id", "product_id"),
        Index("ix_inventory_serials_tenant_warehouse", "tenant_id", "warehouse_id"),
        Index("ix_inventory_serials_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("inventory_batches.id"), nullable=True, index=True)
    serial_number: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    warranty_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[InventorySerialStatusEnum] = mapped_column(
        Enum(InventorySerialStatusEnum, name="inventory_serial_status_enum"),
        nullable=False,
        default=InventorySerialStatusEnum.IN_STOCK,
        index=True,
    )
