from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import RecordStatusEnum


class Product(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_products_tenant_sku"),
        UniqueConstraint("tenant_id", "barcode", name="uq_products_tenant_barcode"),
        Index("ix_products_tenant_status", "tenant_id", "status"),
        Index("ix_products_tenant_category", "tenant_id", "category_id"),
        Index("ix_products_tenant_brand", "tenant_id", "brand_id"),
        Index("ix_products_tenant_vendor", "tenant_id", "vendor_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id"), nullable=True, index=True)
    vendor_id: Mapped[int | None] = mapped_column(ForeignKey("vendors.id"), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(64), nullable=False, default="unit")
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    serial_tracking_enabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    batch_tracking_enabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    expiry_tracking_enabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    warranty_tracking_enabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    status: Mapped[RecordStatusEnum] = mapped_column(
        Enum(RecordStatusEnum, name="record_status_enum"),
        nullable=False,
        default=RecordStatusEnum.ACTIVE,
        index=True,
    )
