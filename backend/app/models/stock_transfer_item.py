from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StockTransferItem(Base):
    __tablename__ = "stock_transfer_items"
    __table_args__ = (
        UniqueConstraint("stock_transfer_id", "product_id", name="uq_stock_transfer_items_transfer_product"),
        Index("ix_stock_transfer_items_transfer_product", "stock_transfer_id", "product_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stock_transfer_id: Mapped[int] = mapped_column(ForeignKey("stock_transfers.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
