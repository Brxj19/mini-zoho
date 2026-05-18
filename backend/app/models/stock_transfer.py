from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import StockTransferStatusEnum


class StockTransfer(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "stock_transfers"
    __table_args__ = (
        Index("ix_stock_transfers_tenant_status", "tenant_id", "status"),
        Index("ix_stock_transfers_tenant_source", "tenant_id", "source_warehouse_id"),
        Index("ix_stock_transfers_tenant_destination", "tenant_id", "destination_warehouse_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    destination_warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    status: Mapped[StockTransferStatusEnum] = mapped_column(
        Enum(StockTransferStatusEnum, name="stock_transfer_status_enum"),
        nullable=False,
        default=StockTransferStatusEnum.DRAFT,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
