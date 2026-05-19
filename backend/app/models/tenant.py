from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import TenantStatusEnum


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    business_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[TenantStatusEnum] = mapped_column(
        Enum(TenantStatusEnum, name="tenant_status_enum"),
        nullable=False,
        default=TenantStatusEnum.ACTIVE,
        index=True,
    )
    subscription_plan_id: Mapped[int | None] = mapped_column(ForeignKey("subscription_plans.id"), nullable=True)

    users = relationship("User", back_populates="tenant")
    subscription_plan = relationship("SubscriptionPlan")
