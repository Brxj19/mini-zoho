from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(160), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(80))
    state: Mapped[str | None] = mapped_column(String(80))
    industry: Mapped[str | None] = mapped_column(String(80))
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    timezone: Mapped[str] = mapped_column(String(60), default="Asia/Kolkata", nullable=False)
    plan: Mapped[str] = mapped_column(String(50), default="Growth", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    setup_completed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)


class Brand(TimestampMixin, Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)


class Warehouse(TimestampMixin, Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    manager_name: Mapped[str] = mapped_column(String(120), nullable=False)
    stock_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)


class Vendor(TimestampMixin, Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id"))
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    sku: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(20), default="pcs", nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(80))
    selling_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    stock_on_hand: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    sales_description: Mapped[str | None] = mapped_column(Text)
    purchase_description: Mapped[str | None] = mapped_column(Text)


class SalesOrder(TimestampMixin, Base):
    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    order_number: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    reference_number: Mapped[str | None] = mapped_column(String(80))
    customer_name: Mapped[str] = mapped_column(String(140), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_shipment_date: Mapped[date | None] = mapped_column(Date)
    items_json: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class PurchaseOrder(TimestampMixin, Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    order_number: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    reference_number: Mapped[str | None] = mapped_column(String(80))
    vendor_name: Mapped[str] = mapped_column(String(140), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery_date: Mapped[date | None] = mapped_column(Date)
    items_json: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class StockTransfer(TimestampMixin, Base):
    __tablename__ = "stock_transfers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    transfer_number: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    source_warehouse: Mapped[str] = mapped_column(String(120), nullable=False)
    destination_warehouse: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    items_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class InventoryAdjustment(TimestampMixin, Base):
    __tablename__ = "inventory_adjustments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    adjustment_number: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    warehouse_name: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str] = mapped_column(String(140), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)


class InventoryTransaction(TimestampMixin, Base):
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    transaction_number: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    transaction_type: Mapped[str] = mapped_column(String(40), nullable=False)
    product_name: Mapped[str] = mapped_column(String(160), nullable=False)
    warehouse_name: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    reference_number: Mapped[str] = mapped_column(String(80), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class ActivityLog(TimestampMixin, Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), index=True)
    actor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    module: Mapped[str] = mapped_column(String(80), nullable=False)


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), index=True)
    actor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    module: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)


class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    unread: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

