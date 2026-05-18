from __future__ import annotations

from sqlalchemy import Boolean, Enum, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import RecordStatusEnum


class Warehouse(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "warehouses"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_warehouses_tenant_code"),
        Index("ix_warehouses_tenant_name", "tenant_id", "name"),
        Index("ix_warehouses_tenant_status", "tenant_id", "status"),
        Index("ix_warehouses_tenant_default", "tenant_id", "is_default"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    state: Mapped[str | None] = mapped_column(String(128), nullable=True)
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    manager_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[RecordStatusEnum] = mapped_column(
        Enum(RecordStatusEnum, name="record_status_enum"),
        nullable=False,
        default=RecordStatusEnum.ACTIVE,
        index=True,
    )
