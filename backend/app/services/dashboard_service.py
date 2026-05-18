from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.models.enums import RecordStatusEnum, RoleEnum, TenantStatusEnum
from app.models.notification import Notification
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder
from app.models.tenant import Tenant
from app.models.user import User
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.repositories.inventory_repository import WarehouseStockRepository
from app.repositories.notification_repository import NotificationRepository


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.stock_repository = WarehouseStockRepository(db)
        self.notification_repository = NotificationRepository(db)

    def get_tenant_dashboard(self, *, current_user: User) -> dict:
        if current_user.role == RoleEnum.SUPER_ADMIN or current_user.tenant_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant dashboard requires a tenant user.")
        tenant_id = current_user.tenant_id

        total_products = self.db.scalar(select(func.count(Product.id)).where(Product.tenant_id == tenant_id, Product.status == RecordStatusEnum.ACTIVE)) or 0
        total_warehouses = self.db.scalar(select(func.count(Warehouse.id)).where(Warehouse.tenant_id == tenant_id, Warehouse.status == RecordStatusEnum.ACTIVE)) or 0
        total_customers = self.db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == tenant_id, Customer.status == RecordStatusEnum.ACTIVE)) or 0
        total_vendors = self.db.scalar(select(func.count(Vendor.id)).where(Vendor.tenant_id == tenant_id, Vendor.status == RecordStatusEnum.ACTIVE)) or 0
        total_sales_orders = self.db.scalar(select(func.count(SalesOrder.id)).where(SalesOrder.tenant_id == tenant_id)) or 0
        total_purchase_orders = self.db.scalar(select(func.count(PurchaseOrder.id)).where(PurchaseOrder.tenant_id == tenant_id)) or 0
        inventory_value = self.db.scalar(
            select(func.coalesce(func.sum(WarehouseStock.quantity * Product.cost_price), 0))
            .select_from(WarehouseStock)
            .join(Product, Product.id == WarehouseStock.product_id)
            .where(WarehouseStock.tenant_id == tenant_id)
        ) or Decimal("0.00")
        low_stock_count = self.db.scalar(
            select(func.count())
            .select_from(WarehouseStock)
            .join(Product, Product.id == WarehouseStock.product_id)
            .join(Warehouse, Warehouse.id == WarehouseStock.warehouse_id)
            .where(WarehouseStock.tenant_id == tenant_id)
            .where(Product.status == RecordStatusEnum.ACTIVE, Warehouse.status == RecordStatusEnum.ACTIVE)
            .where(WarehouseStock.available_quantity <= func.coalesce(WarehouseStock.reorder_level, Product.reorder_level))
        ) or 0
        recent_activities = list(
            self.db.scalars(
                select(AuditLog)
                .where(AuditLog.tenant_id == tenant_id)
                .order_by(AuditLog.created_at.desc())
                .limit(8)
            ).all()
        )
        unread_notifications = self.notification_repository.count_unread(user_id=current_user.id)
        return {
            "total_products": total_products,
            "total_warehouses": total_warehouses,
            "total_customers": total_customers,
            "total_vendors": total_vendors,
            "low_stock_items": low_stock_count,
            "total_sales_orders": total_sales_orders,
            "total_purchase_orders": total_purchase_orders,
            "inventory_value": inventory_value,
            "unread_notifications": unread_notifications,
            "recent_activities": recent_activities,
        }

    def get_super_admin_dashboard(self, *, current_user: User) -> dict:
        if current_user.role != RoleEnum.SUPER_ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admins can access this dashboard.")

        total_tenants = self.db.scalar(select(func.count(Tenant.id))) or 0
        active_tenants = self.db.scalar(select(func.count(Tenant.id)).where(Tenant.status == TenantStatusEnum.ACTIVE)) or 0
        total_users = self.db.scalar(select(func.count(User.id))) or 0
        total_products = self.db.scalar(select(func.count(Product.id))) or 0
        total_sales_orders = self.db.scalar(select(func.count(SalesOrder.id))) or 0
        total_purchase_orders = self.db.scalar(select(func.count(PurchaseOrder.id))) or 0
        recent_tenants = list(self.db.scalars(select(Tenant).order_by(Tenant.created_at.desc()).limit(6)).all())
        recent_activities = list(self.db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(10)).all())
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "total_users": total_users,
            "total_products": total_products,
            "total_sales_orders": total_sales_orders,
            "total_purchase_orders": total_purchase_orders,
            "recent_tenants": recent_tenants,
            "recent_activities": recent_activities,
        }
