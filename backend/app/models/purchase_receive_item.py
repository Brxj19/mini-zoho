from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PurchaseReceiveItem(Base):
    __tablename__ = "purchase_receive_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    purchase_receive_id: Mapped[int] = mapped_column(ForeignKey("purchase_receives.id"), nullable=False, index=True)
    purchase_order_item_id: Mapped[int] = mapped_column(ForeignKey("purchase_order_items.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=False)
