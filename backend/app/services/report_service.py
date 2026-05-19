from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.audit_log import AuditLog
from app.models.category import Category
from app.models.customer import Customer
from app.models.enums import InventoryTransactionTypeEnum, PurchaseOrderStatusEnum, RecordStatusEnum, RoleEnum, SalesOrderStatusEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder
from app.models.user import User
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def inventory_summary(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
        category_id: int | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                Product.id,
                Product.name,
                Product.sku,
                Category.name,
                func.coalesce(func.sum(WarehouseStock.quantity), 0),
                func.coalesce(func.sum(WarehouseStock.reserved_quantity), 0),
                func.coalesce(func.sum(WarehouseStock.available_quantity), 0),
                Product.cost_price,
            )
            .select_from(Product)
            .join(Category, Category.id == Product.category_id, isouter=True)
            .join(WarehouseStock, WarehouseStock.product_id == Product.id, isouter=True)
            .where(Product.tenant_id == scoped_tenant_id)
            .where(Product.status == RecordStatusEnum.ACTIVE)
            .group_by(Product.id, Product.name, Product.sku, Category.name, Product.cost_price)
            .order_by(Product.name.asc())
        )
        if warehouse_id is not None:
            statement = statement.where(or_(WarehouseStock.warehouse_id == warehouse_id, WarehouseStock.warehouse_id.is_(None)))
        if product_id is not None:
            statement = statement.where(Product.id == product_id)
        if category_id is not None:
            statement = statement.where(Product.category_id == category_id)

        rows = []
        for row in self.db.execute(statement).all():
            total_quantity = int(row[4] or 0)
            rows.append(
                {
                    "product_id": row[0],
                    "product_name": row[1],
                    "sku": row[2],
                    "category_name": row[3],
                    "total_quantity": total_quantity,
                    "reserved_quantity": int(row[5] or 0),
                    "available_quantity": int(row[6] or 0),
                    "cost_price": str(row[7]),
                    "inventory_value": str((Decimal(row[7] or 0) * total_quantity).quantize(Decimal("0.01"))),
                }
            )
        return rows

    def stock_movement(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
        category_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                InventoryTransaction.id,
                InventoryTransaction.created_at,
                InventoryTransaction.transaction_type,
                InventoryTransaction.quantity,
                Product.id,
                Product.name,
                Product.sku,
                Warehouse.id,
                Warehouse.name,
                InventoryTransaction.reference_type,
                InventoryTransaction.reference_id,
            )
            .join(Product, Product.id == InventoryTransaction.product_id)
            .join(Warehouse, Warehouse.id == InventoryTransaction.warehouse_id)
            .where(InventoryTransaction.tenant_id == scoped_tenant_id)
            .order_by(InventoryTransaction.created_at.desc())
        )
        if warehouse_id is not None:
            statement = statement.where(InventoryTransaction.warehouse_id == warehouse_id)
        if product_id is not None:
            statement = statement.where(InventoryTransaction.product_id == product_id)
        if category_id is not None:
            statement = statement.where(Product.category_id == category_id)
        if date_from is not None:
            statement = statement.where(InventoryTransaction.created_at >= date_from)
        if date_to is not None:
            statement = statement.where(InventoryTransaction.created_at <= date_to)
        return [
            {
                "transaction_id": row[0],
                "created_at": row[1].isoformat(),
                "transaction_type": row[2].value,
                "quantity": row[3],
                "product_id": row[4],
                "product_name": row[5],
                "sku": row[6],
                "warehouse_id": row[7],
                "warehouse_name": row[8],
                "reference_type": row[9],
                "reference_id": row[10],
            }
            for row in self.db.execute(statement).all()
        ]

    def low_stock(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
        category_id: int | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                WarehouseStock.product_id,
                Product.name,
                Product.sku,
                WarehouseStock.warehouse_id,
                Warehouse.name,
                WarehouseStock.available_quantity,
                func.coalesce(WarehouseStock.reorder_level, Product.reorder_level),
            )
            .join(Product, Product.id == WarehouseStock.product_id)
            .join(Warehouse, Warehouse.id == WarehouseStock.warehouse_id)
            .where(WarehouseStock.tenant_id == scoped_tenant_id)
            .where(Product.status == RecordStatusEnum.ACTIVE, Warehouse.status == RecordStatusEnum.ACTIVE)
            .where(WarehouseStock.available_quantity <= func.coalesce(WarehouseStock.reorder_level, Product.reorder_level))
            .order_by(WarehouseStock.available_quantity.asc(), Product.name.asc())
        )
        if warehouse_id is not None:
            statement = statement.where(WarehouseStock.warehouse_id == warehouse_id)
        if product_id is not None:
            statement = statement.where(WarehouseStock.product_id == product_id)
        if category_id is not None:
            statement = statement.where(Product.category_id == category_id)
        return [
            {
                "product_id": row[0],
                "product_name": row[1],
                "sku": row[2],
                "warehouse_id": row[3],
                "warehouse_name": row[4],
                "available_quantity": row[5],
                "reorder_level": row[6],
            }
            for row in self.db.execute(statement).all()
        ]

    def out_of_stock(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
        category_id: int | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                WarehouseStock.product_id,
                Product.name,
                Product.sku,
                WarehouseStock.warehouse_id,
                Warehouse.name,
                WarehouseStock.available_quantity,
                func.coalesce(WarehouseStock.reorder_level, Product.reorder_level),
            )
            .join(Product, Product.id == WarehouseStock.product_id)
            .join(Warehouse, Warehouse.id == WarehouseStock.warehouse_id)
            .where(WarehouseStock.tenant_id == scoped_tenant_id)
            .where(Product.status == RecordStatusEnum.ACTIVE, Warehouse.status == RecordStatusEnum.ACTIVE)
            .where(WarehouseStock.available_quantity <= 0)
            .order_by(Product.name.asc(), Warehouse.name.asc())
        )
        if warehouse_id is not None:
            statement = statement.where(WarehouseStock.warehouse_id == warehouse_id)
        if product_id is not None:
            statement = statement.where(WarehouseStock.product_id == product_id)
        if category_id is not None:
            statement = statement.where(Product.category_id == category_id)
        return [
            {
                "product_id": row[0],
                "product_name": row[1],
                "sku": row[2],
                "warehouse_id": row[3],
                "warehouse_name": row[4],
                "available_quantity": row[5],
                "reorder_level": row[6],
            }
            for row in self.db.execute(statement).all()
        ]

    def warehouse_stock(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
        category_id: int | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                Warehouse.id,
                Warehouse.name,
                Product.id,
                Product.name,
                Product.sku,
                WarehouseStock.quantity,
                WarehouseStock.reserved_quantity,
                WarehouseStock.available_quantity,
            )
            .select_from(WarehouseStock)
            .join(Warehouse, Warehouse.id == WarehouseStock.warehouse_id)
            .join(Product, Product.id == WarehouseStock.product_id)
            .where(WarehouseStock.tenant_id == scoped_tenant_id)
            .order_by(Warehouse.name.asc(), Product.name.asc())
        )
        if warehouse_id is not None:
            statement = statement.where(WarehouseStock.warehouse_id == warehouse_id)
        if product_id is not None:
            statement = statement.where(WarehouseStock.product_id == product_id)
        if category_id is not None:
            statement = statement.where(Product.category_id == category_id)
        return [
            {
                "warehouse_id": row[0],
                "warehouse_name": row[1],
                "product_id": row[2],
                "product_name": row[3],
                "sku": row[4],
                "quantity": row[5],
                "reserved_quantity": row[6],
                "available_quantity": row[7],
            }
            for row in self.db.execute(statement).all()
        ]

    def product_valuation(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
        category_id: int | None = None,
    ) -> list[dict]:
        return self.inventory_summary(
            current_user=current_user,
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            category_id=category_id,
        )

    def purchase_orders(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        vendor_id: int | None = None,
        status_filter: PurchaseOrderStatusEnum | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                PurchaseOrder.id,
                PurchaseOrder.po_number,
                PurchaseOrder.order_date,
                PurchaseOrder.expected_delivery_date,
                PurchaseOrder.status,
                PurchaseOrder.total_amount,
                Vendor.id,
                Vendor.name,
            )
            .join(Vendor, Vendor.id == PurchaseOrder.vendor_id)
            .where(PurchaseOrder.tenant_id == scoped_tenant_id)
            .order_by(PurchaseOrder.order_date.desc(), PurchaseOrder.id.desc())
        )
        if vendor_id is not None:
            statement = statement.where(PurchaseOrder.vendor_id == vendor_id)
        if status_filter is not None:
            statement = statement.where(PurchaseOrder.status == status_filter)
        if date_from is not None:
            statement = statement.where(PurchaseOrder.order_date >= date_from)
        if date_to is not None:
            statement = statement.where(PurchaseOrder.order_date <= date_to)
        return [
            {
                "purchase_order_id": row[0],
                "po_number": row[1],
                "order_date": row[2].isoformat(),
                "expected_delivery_date": row[3].isoformat() if row[3] else None,
                "status": row[4].value,
                "total_amount": str(row[5]),
                "vendor_id": row[6],
                "vendor_name": row[7],
            }
            for row in self.db.execute(statement).all()
        ]

    def vendor_purchase_summary(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        vendor_id: int | None = None,
        status_filter: PurchaseOrderStatusEnum | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                Vendor.id,
                Vendor.name,
                func.count(PurchaseOrder.id),
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0),
                func.sum(case((PurchaseOrder.status == PurchaseOrderStatusEnum.ISSUED, 1), else_=0)),
                func.sum(case((PurchaseOrder.status == PurchaseOrderStatusEnum.PARTIALLY_RECEIVED, 1), else_=0)),
                func.sum(case((PurchaseOrder.status == PurchaseOrderStatusEnum.RECEIVED, 1), else_=0)),
                func.sum(case((PurchaseOrder.status == PurchaseOrderStatusEnum.CANCELLED, 1), else_=0)),
            )
            .select_from(PurchaseOrder)
            .join(Vendor, Vendor.id == PurchaseOrder.vendor_id)
            .where(PurchaseOrder.tenant_id == scoped_tenant_id)
            .group_by(Vendor.id, Vendor.name)
            .order_by(func.coalesce(func.sum(PurchaseOrder.total_amount), 0).desc(), Vendor.name.asc())
        )
        if vendor_id is not None:
            statement = statement.where(PurchaseOrder.vendor_id == vendor_id)
        if status_filter is not None:
            statement = statement.where(PurchaseOrder.status == status_filter)
        if date_from is not None:
            statement = statement.where(PurchaseOrder.order_date >= date_from)
        if date_to is not None:
            statement = statement.where(PurchaseOrder.order_date <= date_to)
        return [
            {
                "vendor_id": row[0],
                "vendor_name": row[1],
                "purchase_order_count": int(row[2] or 0),
                "total_purchase_amount": str(row[3]),
                "issued_orders": int(row[4] or 0),
                "partially_received_orders": int(row[5] or 0),
                "received_orders": int(row[6] or 0),
                "cancelled_orders": int(row[7] or 0),
            }
            for row in self.db.execute(statement).all()
        ]

    def sales_orders(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        customer_id: int | None = None,
        status_filter: SalesOrderStatusEnum | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                SalesOrder.id,
                SalesOrder.so_number,
                SalesOrder.order_date,
                SalesOrder.status,
                SalesOrder.total_amount,
                Customer.id,
                Customer.name,
            )
            .join(Customer, Customer.id == SalesOrder.customer_id)
            .where(SalesOrder.tenant_id == scoped_tenant_id)
            .order_by(SalesOrder.order_date.desc(), SalesOrder.id.desc())
        )
        if customer_id is not None:
            statement = statement.where(SalesOrder.customer_id == customer_id)
        if status_filter is not None:
            statement = statement.where(SalesOrder.status == status_filter)
        if date_from is not None:
            statement = statement.where(SalesOrder.order_date >= date_from)
        if date_to is not None:
            statement = statement.where(SalesOrder.order_date <= date_to)
        return [
            {
                "sales_order_id": row[0],
                "so_number": row[1],
                "order_date": row[2].isoformat(),
                "status": row[3].value,
                "total_amount": str(row[4]),
                "customer_id": row[5],
                "customer_name": row[6],
            }
            for row in self.db.execute(statement).all()
        ]

    def customer_sales_summary(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        customer_id: int | None = None,
        status_filter: SalesOrderStatusEnum | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                Customer.id,
                Customer.name,
                func.count(SalesOrder.id),
                func.coalesce(func.sum(SalesOrder.total_amount), 0),
                func.sum(case((SalesOrder.status == SalesOrderStatusEnum.CONFIRMED, 1), else_=0)),
                func.sum(case((SalesOrder.status == SalesOrderStatusEnum.PACKED, 1), else_=0)),
                func.sum(case((SalesOrder.status == SalesOrderStatusEnum.SHIPPED, 1), else_=0)),
                func.sum(case((SalesOrder.status == SalesOrderStatusEnum.DELIVERED, 1), else_=0)),
                func.sum(case((SalesOrder.status == SalesOrderStatusEnum.CANCELLED, 1), else_=0)),
            )
            .select_from(SalesOrder)
            .join(Customer, Customer.id == SalesOrder.customer_id)
            .where(SalesOrder.tenant_id == scoped_tenant_id)
            .group_by(Customer.id, Customer.name)
            .order_by(func.coalesce(func.sum(SalesOrder.total_amount), 0).desc(), Customer.name.asc())
        )
        if customer_id is not None:
            statement = statement.where(SalesOrder.customer_id == customer_id)
        if status_filter is not None:
            statement = statement.where(SalesOrder.status == status_filter)
        if date_from is not None:
            statement = statement.where(SalesOrder.order_date >= date_from)
        if date_to is not None:
            statement = statement.where(SalesOrder.order_date <= date_to)
        return [
            {
                "customer_id": row[0],
                "customer_name": row[1],
                "sales_order_count": int(row[2] or 0),
                "total_sales_amount": str(row[3]),
                "confirmed_orders": int(row[4] or 0),
                "packed_orders": int(row[5] or 0),
                "shipped_orders": int(row[6] or 0),
                "delivered_orders": int(row[7] or 0),
                "cancelled_orders": int(row[8] or 0),
            }
            for row in self.db.execute(statement).all()
        ]

    def inventory_adjustments(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
        category_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                InventoryTransaction.id,
                InventoryTransaction.created_at,
                InventoryTransaction.quantity,
                InventoryTransaction.note,
                Product.id,
                Product.name,
                Product.sku,
                Warehouse.id,
                Warehouse.name,
                InventoryTransaction.reference_type,
                InventoryTransaction.reference_id,
            )
            .join(Product, Product.id == InventoryTransaction.product_id)
            .join(Warehouse, Warehouse.id == InventoryTransaction.warehouse_id)
            .where(InventoryTransaction.tenant_id == scoped_tenant_id)
            .where(InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.ADJUSTMENT)
            .order_by(InventoryTransaction.created_at.desc())
        )
        if warehouse_id is not None:
            statement = statement.where(InventoryTransaction.warehouse_id == warehouse_id)
        if product_id is not None:
            statement = statement.where(InventoryTransaction.product_id == product_id)
        if category_id is not None:
            statement = statement.where(Product.category_id == category_id)
        if date_from is not None:
            statement = statement.where(InventoryTransaction.created_at >= date_from)
        if date_to is not None:
            statement = statement.where(InventoryTransaction.created_at <= date_to)
        return [
            {
                "adjustment_id": row[0],
                "created_at": row[1].isoformat(),
                "quantity_delta": row[2],
                "note": row[3],
                "product_id": row[4],
                "product_name": row[5],
                "sku": row[6],
                "warehouse_id": row[7],
                "warehouse_name": row[8],
                "reference_type": row[9],
                "reference_id": row[10],
            }
            for row in self.db.execute(statement).all()
        ]

    def audit_logs(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        user_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        scoped_tenant_id = self._tenant_scope(current_user, tenant_id)
        statement = (
            select(
                AuditLog.id,
                AuditLog.created_at,
                AuditLog.action,
                AuditLog.entity_type,
                AuditLog.entity_id,
                AuditLog.user_id,
            )
            .where(AuditLog.tenant_id == scoped_tenant_id if scoped_tenant_id is not None else True)
            .order_by(AuditLog.created_at.desc())
        )
        if current_user.role != RoleEnum.SUPER_ADMIN:
            statement = statement.where(AuditLog.tenant_id == scoped_tenant_id)
        if user_id is not None:
            statement = statement.where(AuditLog.user_id == user_id)
        if action:
            statement = statement.where(AuditLog.action == action)
        if entity_type:
            statement = statement.where(AuditLog.entity_type == entity_type)
        if date_from is not None:
            statement = statement.where(AuditLog.created_at >= date_from)
        if date_to is not None:
            statement = statement.where(AuditLog.created_at <= date_to)
        return [
            {
                "audit_log_id": row[0],
                "created_at": row[1].isoformat(),
                "action": row[2],
                "entity_type": row[3],
                "entity_id": row[4],
                "user_id": row[5],
            }
            for row in self.db.execute(statement).all()
        ]

    def _tenant_scope(self, current_user: User, tenant_id: int | None) -> int | None:
        return resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
