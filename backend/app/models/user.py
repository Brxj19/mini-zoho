from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import RoleEnum, UserStatusEnum


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_tenant_role", "tenant_id", "role"),
        Index("ix_users_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="user_role_enum"),
        nullable=False,
        index=True,
    )
    status: Mapped[UserStatusEnum] = mapped_column(
        Enum(UserStatusEnum, name="user_status_enum"),
        nullable=False,
        default=UserStatusEnum.ACTIVE,
        index=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    phone_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant = relationship("Tenant", back_populates="users")
