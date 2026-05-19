from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import PackageStatusEnum


class Package(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "packages"
    __table_args__ = (
        UniqueConstraint("tenant_id", "package_number", name="uq_packages_tenant_number"),
        Index("ix_packages_tenant_status", "tenant_id", "status"),
        Index("ix_packages_tenant_sales_order", "tenant_id", "sales_order_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sales_order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), nullable=False, index=True)
    package_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[PackageStatusEnum] = mapped_column(
        Enum(PackageStatusEnum, name="package_status_enum"),
        nullable=False,
        default=PackageStatusEnum.DRAFT,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
