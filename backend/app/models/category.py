from __future__ import annotations

from sqlalchemy import Enum, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantOwnedMixin, TimestampMixin
from app.models.enums import RecordStatusEnum


class Category(TenantOwnedMixin, TimestampMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_categories_tenant_name"),
        Index("ix_categories_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[RecordStatusEnum] = mapped_column(
        Enum(RecordStatusEnum, name="record_status_enum"),
        nullable=False,
        default=RecordStatusEnum.ACTIVE,
        index=True,
    )
