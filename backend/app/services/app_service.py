from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    ActivityLog,
    AuditLog,
    Brand,
    Category,
    Customer,
    InventoryAdjustment,
    InventoryTransaction,
    Notification,
    Product,
    PurchaseOrder,
    SalesOrder,
    StockTransfer,
    Tenant,
    User,
    Vendor,
    Warehouse,
)
from app.schemas.app import CreateItemRequest, CreatePurchaseOrderRequest, CreateSalesOrderRequest


def _scope_clause(model, user):
    if user.role == "SUPER_ADMIN":
        return None
    return model.tenant_id == user.tenant_id


def _scoped_query(model, db: Session, user):
    stmt = select(model)
    clause = _scope_clause(model, user)
    if clause is not None:
        stmt = stmt.where(clause)
    return stmt


def _money(value: Decimal | float | int) -> str:
    return f"₹{float(value):,.0f}"


def get_dashboard_data(db: Session, user) -> dict:
    if user.role == "SUPER_ADMIN":
        total_tenants = db.scalar(select(func.count(Tenant.id))) or 0
        active_tenants = db.scalar(select(func.count(Tenant.id)).where(Tenant.status == "ACTIVE")) or 0
        disabled_tenants = db.scalar(select(func.count(Tenant.id)).where(Tenant.status == "DISABLED")) or 0
        total_users = db.scalar(select(func.count(User.id))) or 0
        total_products = db.scalar(select(func.count(Product.id))) or 0
        total_orders = (db.scalar(select(func.count(SalesOrder.id))) or 0) + (db.scalar(select(func.count(PurchaseOrder.id))) or 0)
        recent_activity = [serialize_activity_log(log) for log in db.scalars(select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(5))]
        return {
            "role": "SUPER_ADMIN",
            "metrics": [
                {"label": "Total Tenants", "value": total_tenants, "delta": "Platform view", "tone": "info"},
                {"label": "Active Tenants", "value": active_tenants, "delta": "Healthy accounts", "tone": "positive"},
                {"label": "Disabled Tenants", "value": disabled_tenants, "delta": "Needs review", "tone": "warning"},
                {"label": "Platform Users", "value": total_users, "delta": f"{total_products} products tracked", "tone": "neutral"},
            ],
            "recent_activities": recent_activity,
            "super_admin_summary": {
                "total_products": total_products,
                "total_orders": total_orders,
            },
        }

    products = list(db.scalars(_scoped_query(Product, db, user).order_by(Product.created_at.desc())))
    purchase_orders = list(db.scalars(_scoped_query(PurchaseOrder, db, user).order_by(PurchaseOrder.created_at.desc())))
    sales_orders = list(db.scalars(_scoped_query(SalesOrder, db, user).order_by(SalesOrder.created_at.desc())))
    low_stock = [product for product in products if product.stock_on_hand <= product.reorder_level and product.status != "INACTIVE"]

    sales_activity = {
        "To Be Packed": len([order for order in sales_orders if order.status == "CONFIRMED"]),
        "To Be Shipped": len([order for order in sales_orders if order.status == "PACKED"]),
        "To Be Delivered": len([order for order in sales_orders if order.status == "SHIPPED"]),
        "To Be Invoiced": len([order for order in sales_orders if order.status in {"CONFIRMED", "PACKED"}]),
    }
    purchase_activity = {
        "To Be Received": len([order for order in purchase_orders if order.status == "ISSUED"]),
        "Receive In Progress": len([order for order in purchase_orders if order.status == "PARTIALLY_RECEIVED"]),
    }
    notifications = [serialize_notification(item) for item in db.scalars(_scoped_query(Notification, db, user).order_by(Notification.created_at.desc()).limit(5))]
    recent_activity = [serialize_activity_log(log) for log in db.scalars(_scoped_query(ActivityLog, db, user).order_by(ActivityLog.created_at.desc()).limit(5))]

    return {
        "role": user.role,
        "metrics": [
            {"label": "Quantity in Hand", "value": sum(product.stock_on_hand for product in products), "delta": f"{len(products)} active SKUs", "tone": "positive"},
            {"label": "Quantity to be Received", "value": len([order for order in purchase_orders if order.status in {'ISSUED', 'PARTIALLY_RECEIVED'}]), "delta": "Open purchase orders", "tone": "info"},
            {"label": "Low-stock Items", "value": len(low_stock), "delta": "Needs reorder", "tone": "warning"},
            {"label": "Sales Orders", "value": len(sales_orders), "delta": "Live order pipeline", "tone": "neutral"},
        ],
        "sales_activity": [{"label": key, "value": value} for key, value in sales_activity.items()],
        "product_details": [
            {"label": "Low-stock items", "value": len(low_stock)},
            {"label": "All item groups", "value": db.scalar(select(func.count(Category.id)).where(Category.tenant_id == user.tenant_id)) or 0},
            {"label": "All items", "value": len(products)},
            {"label": "Unconfirmed items", "value": len([product for product in products if product.status == "INACTIVE"])},
            {"label": "Active items", "value": f"{round((len([p for p in products if p.status == 'ACTIVE']) / max(len(products), 1)) * 100)}%"},
        ],
        "top_selling_items": [serialize_top_product(product) for product in sorted(products, key=lambda item: item.stock_on_hand)[:3]],
        "top_stocked_items": [serialize_top_stock(product) for product in sorted(products, key=lambda item: item.stock_on_hand, reverse=True)[:3]],
        "pending_actions": {
            "sales": [{"label": key, "value": value} for key, value in sales_activity.items()],
            "purchases": [{"label": key, "value": value} for key, value in purchase_activity.items()],
            "inventory": [{"label": "Below Reorder Level", "value": len(low_stock)}],
        },
        "recent_activities": recent_activity,
        "notifications": notifications,
    }


def list_module_rows(db: Session, user, module: str) -> list[dict]:
    mapping = {
        "items": lambda: [serialize_product(item, db) for item in db.scalars(_scoped_query(Product, db, user).order_by(Product.created_at.desc()))],
        "warehouses": lambda: [serialize_warehouse(item) for item in db.scalars(_scoped_query(Warehouse, db, user).order_by(Warehouse.created_at.desc()))],
        "customers": lambda: [serialize_customer(item) for item in db.scalars(_scoped_query(Customer, db, user).order_by(Customer.created_at.desc()))],
        "vendors": lambda: [serialize_vendor(item) for item in db.scalars(_scoped_query(Vendor, db, user).order_by(Vendor.created_at.desc()))],
        "sales-orders": lambda: [serialize_sales_order(item) for item in db.scalars(_scoped_query(SalesOrder, db, user).order_by(SalesOrder.created_at.desc()))],
        "purchase-orders": lambda: [serialize_purchase_order(item) for item in db.scalars(_scoped_query(PurchaseOrder, db, user).order_by(PurchaseOrder.created_at.desc()))],
        "stock-transfers": lambda: [serialize_transfer(item) for item in db.scalars(_scoped_query(StockTransfer, db, user).order_by(StockTransfer.created_at.desc()))],
        "inventory-adjustments": lambda: [serialize_adjustment(item) for item in db.scalars(_scoped_query(InventoryAdjustment, db, user).order_by(InventoryAdjustment.created_at.desc()))],
        "transactions": lambda: [serialize_transaction(item) for item in db.scalars(_scoped_query(InventoryTransaction, db, user).order_by(InventoryTransaction.created_at.desc()))],
        "users": lambda: [serialize_user(item) for item in db.scalars(_scoped_query(User, db, user).order_by(User.created_at.desc()))],
        "tenants": lambda: [serialize_tenant(item, db) for item in db.scalars(select(Tenant).order_by(Tenant.created_at.desc()))],
        "activity-logs": lambda: [serialize_activity_log(item) for item in db.scalars(_scoped_query(ActivityLog, db, user).order_by(ActivityLog.created_at.desc()))],
        "audit-logs": lambda: [serialize_audit_log(item) for item in db.scalars(_scoped_query(AuditLog, db, user).order_by(AuditLog.created_at.desc()))],
        "low-stock": lambda: [serialize_product(item, db) for item in db.scalars(_scoped_query(Product, db, user).where(Product.stock_on_hand <= Product.reorder_level).order_by(Product.stock_on_hand.asc()))],
    }
    if module not in mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown module.")
    return mapping[module]()


def get_record_detail(db: Session, user, module: str, record_id: int) -> dict:
    if module == "items":
        product = db.get(Product, record_id)
        if product is None or (user.role != "SUPER_ADMIN" and product.tenant_id != user.tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
        return {
            **serialize_product(product, db),
            "costPrice": _money(product.cost_price),
            "unit": product.unit,
            "barcode": product.barcode,
            "description": product.sales_description,
            "transactions": [serialize_transaction(item) for item in db.scalars(_scoped_query(InventoryTransaction, db, user).where(InventoryTransaction.product_name == product.name).order_by(InventoryTransaction.created_at.desc()).limit(6))],
        }

    if module == "warehouses":
        warehouse = db.get(Warehouse, record_id)
        if warehouse is None or (user.role != "SUPER_ADMIN" and warehouse.tenant_id != user.tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found.")
        items = [serialize_product(item, db) for item in db.scalars(_scoped_query(Product, db, user).order_by(Product.stock_on_hand.desc()).limit(5))]
        transactions = [serialize_transaction(item) for item in db.scalars(_scoped_query(InventoryTransaction, db, user).where(InventoryTransaction.warehouse_name == warehouse.name).order_by(InventoryTransaction.created_at.desc()).limit(6))]
        return {**serialize_warehouse(warehouse), "items": items, "transactions": transactions}

    if module == "sales-orders":
        order = db.get(SalesOrder, record_id)
        if order is None or (user.role != "SUPER_ADMIN" and order.tenant_id != user.tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found.")
        payload = serialize_sales_order(order)
        payload["items"] = json.loads(order.items_json)
        payload["notes"] = order.notes
        return payload

    if module == "purchase-orders":
        order = db.get(PurchaseOrder, record_id)
        if order is None or (user.role != "SUPER_ADMIN" and order.tenant_id != user.tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found.")
        payload = serialize_purchase_order(order)
        payload["items"] = json.loads(order.items_json)
        payload["notes"] = order.notes
        return payload

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown record type.")


def create_item(db: Session, user, payload: CreateItemRequest) -> dict:
    if user.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super admin cannot create tenant-scoped items without a tenant.")

    category = db.scalar(select(Category).where(Category.tenant_id == user.tenant_id, Category.name == payload.category_name))
    if category is None:
        category = Category(tenant_id=user.tenant_id, name=payload.category_name, status="ACTIVE")
        db.add(category)
        db.flush()

    brand = db.scalar(select(Brand).where(Brand.tenant_id == user.tenant_id, Brand.name == payload.brand_name))
    if brand is None:
        brand = Brand(tenant_id=user.tenant_id, name=payload.brand_name, status="ACTIVE")
        db.add(brand)
        db.flush()

    product = Product(
        tenant_id=user.tenant_id,
        category_id=category.id,
        brand_id=brand.id,
        name=payload.name,
        sku=payload.sku,
        unit=payload.unit,
        barcode=payload.barcode,
        selling_price=payload.selling_price,
        cost_price=payload.cost_price,
        stock_on_hand=payload.stock_on_hand,
        reorder_level=payload.reorder_level,
        status="LOW_STOCK" if payload.stock_on_hand <= payload.reorder_level and payload.stock_on_hand > 0 else "ACTIVE",
        sales_description=payload.sales_description,
        purchase_description=payload.purchase_description,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return serialize_product(product, db)


def create_sales_order(db: Session, user, payload: CreateSalesOrderRequest) -> dict:
    if user.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super admin cannot create tenant-scoped sales orders.")

    order_number = _next_document_number(db, SalesOrder, "SO", 210)
    amount = sum(line.quantity * line.rate for line in payload.items)
    order = SalesOrder(
        tenant_id=user.tenant_id,
        order_number=order_number,
        reference_number=payload.reference_number,
        customer_name=payload.customer_name,
        status=payload.status.upper().replace(" ", "_"),
        amount=amount,
        order_date=date.fromisoformat(payload.order_date),
        expected_shipment_date=date.fromisoformat(payload.expected_shipment_date) if payload.expected_shipment_date else None,
        items_json=json.dumps(
            [
                {
                    "name": line.item_name,
                    "warehouse": line.warehouse_name,
                    "quantity": line.quantity,
                    "rate": line.rate,
                }
                for line in payload.items
            ]
        ),
        notes=payload.notes,
    )
    db.add(order)
    db.add(
        ActivityLog(
            tenant_id=user.tenant_id,
            actor_name=user.name,
            action=f"Created sales order {order_number}",
            module="Sales Orders",
        )
    )
    db.commit()
    db.refresh(order)
    return serialize_sales_order(order)


def create_purchase_order(db: Session, user, payload: CreatePurchaseOrderRequest) -> dict:
    if user.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super admin cannot create tenant-scoped purchase orders.")

    order_number = _next_document_number(db, PurchaseOrder, "PO", 204)
    amount = sum(line.quantity * line.rate for line in payload.items)
    order = PurchaseOrder(
        tenant_id=user.tenant_id,
        order_number=order_number,
        reference_number=payload.reference_number,
        vendor_name=payload.vendor_name,
        status=payload.status.upper().replace(" ", "_"),
        amount=amount,
        order_date=date.fromisoformat(payload.order_date),
        expected_delivery_date=date.fromisoformat(payload.expected_delivery_date) if payload.expected_delivery_date else None,
        items_json=json.dumps(
            [
                {
                    "name": line.item_name,
                    "warehouse": line.warehouse_name,
                    "quantity": line.quantity,
                    "rate": line.rate,
                }
                for line in payload.items
            ]
        ),
        notes=payload.notes,
    )
    db.add(order)
    db.add(
        ActivityLog(
            tenant_id=user.tenant_id,
            actor_name=user.name,
            action=f"Created purchase order {order_number}",
            module="Purchase Orders",
        )
    )
    db.commit()
    db.refresh(order)
    return serialize_purchase_order(order)


def update_order_status(db: Session, user, module: str, record_id: int, status_value: str) -> dict:
    model = SalesOrder if module == "sales-orders" else PurchaseOrder
    order = db.get(model, record_id)
    if order is None or (user.role != "SUPER_ADMIN" and order.tenant_id != user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    order.status = status_value.upper().replace(" ", "_")
    db.add(
        ActivityLog(
            tenant_id=order.tenant_id,
            actor_name=user.name,
            action=f"Updated {order.order_number} to {order.status.replace('_', ' ')}",
            module="Sales Orders" if module == "sales-orders" else "Purchase Orders",
        )
    )
    db.commit()
    db.refresh(order)
    return serialize_sales_order(order) if module == "sales-orders" else serialize_purchase_order(order)


def list_notifications(db: Session, user) -> list[dict]:
    rows = db.scalars(_scoped_query(Notification, db, user).order_by(Notification.created_at.desc()))
    return [serialize_notification(item) for item in rows]


def mark_notification_read(db: Session, user, notification_id: int) -> dict:
    notification = db.get(Notification, notification_id)
    if notification is None or (user.role != "SUPER_ADMIN" and notification.tenant_id not in {None, user.tenant_id}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    notification.unread = False
    db.commit()
    db.refresh(notification)
    return serialize_notification(notification)


def mark_all_notifications_read(db: Session, user) -> dict:
    rows = db.scalars(_scoped_query(Notification, db, user))
    for item in rows:
        item.unread = False
    db.commit()
    return {"detail": "Notifications marked as read."}


def report_catalog() -> list[dict]:
    return [
        {
            "title": "Inventory Reports",
            "reports": [
                {"key": "inventory-summary", "title": "Inventory Summary", "description": "High-level stock health and catalog numbers."},
                {"key": "stock-movement", "title": "Stock Movement", "description": "Track stock in, out, adjustments, and transfers."},
                {"key": "warehouse-stock", "title": "Warehouse Stock", "description": "Warehouse-level item counts and availability."},
            ],
        },
        {
            "title": "Sales Reports",
            "reports": [{"key": "sales-orders", "title": "Sales Orders", "description": "Order status, volume, and collection-ready records."}],
        },
        {
            "title": "Purchase Reports",
            "reports": [{"key": "purchase-orders", "title": "Purchase Orders", "description": "Receiving progress and vendor-facing order summaries."}],
        },
        {
            "title": "Activity Reports",
            "reports": [{"key": "activity-log", "title": "Activity Stream", "description": "Recent system activity and operator actions."}],
        },
    ]


def report_rows(db: Session, user, report_key: str) -> list[dict]:
    if report_key == "inventory-summary":
        products = list(db.scalars(_scoped_query(Product, db, user)))
        return [
            {"metric": "Active items", "value": len([item for item in products if item.status == "ACTIVE"])},
            {"metric": "Low-stock items", "value": len([item for item in products if item.stock_on_hand <= item.reorder_level])},
            {"metric": "Out-of-stock items", "value": len([item for item in products if item.stock_on_hand == 0])},
            {"metric": "Stock value", "value": _money(sum(float(item.cost_price) * item.stock_on_hand for item in products))},
        ]
    if report_key == "stock-movement":
        return list_module_rows(db, user, "transactions")
    if report_key == "warehouse-stock":
        return list_module_rows(db, user, "warehouses")
    if report_key == "purchase-orders":
        return list_module_rows(db, user, "purchase-orders")
    if report_key == "sales-orders":
        return list_module_rows(db, user, "sales-orders")
    if report_key == "activity-log":
        return list_module_rows(db, user, "activity-logs")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown report.")


def serialize_product(product: Product, db: Session) -> dict:
    category = db.get(Category, product.category_id) if product.category_id else None
    brand = db.get(Brand, product.brand_id) if product.brand_id else None
    status_value = product.status
    if product.stock_on_hand <= product.reorder_level and product.stock_on_hand > 0:
        status_value = "LOW_STOCK"
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "category": category.name if category else "Uncategorized",
        "brand": brand.name if brand else "Unbranded",
        "stockOnHand": product.stock_on_hand,
        "reorderLevel": product.reorder_level,
        "sellingPrice": _money(product.selling_price),
        "status": status_value,
        "barcode": product.barcode,
    }


def serialize_warehouse(warehouse: Warehouse) -> dict:
    return {
        "id": warehouse.id,
        "name": warehouse.name,
        "location": f"{warehouse.city}, {warehouse.state}",
        "stockCount": warehouse.stock_count,
        "manager": warehouse.manager_name,
        "primary": warehouse.is_primary,
        "status": warehouse.status,
    }


def serialize_vendor(vendor: Vendor) -> dict:
    return {
        "id": vendor.id,
        "name": vendor.name,
        "email": vendor.email,
        "phone": vendor.phone,
        "city": vendor.city,
        "status": vendor.status,
    }


def serialize_customer(customer: Customer) -> dict:
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "city": customer.city,
        "status": customer.status,
    }


def serialize_sales_order(order: SalesOrder) -> dict:
    return {
        "id": order.id,
        "orderNumber": order.order_number,
        "date": order.order_date.isoformat(),
        "reference": order.reference_number,
        "customerName": order.customer_name,
        "status": order.status,
        "amount": _money(order.amount),
    }


def serialize_purchase_order(order: PurchaseOrder) -> dict:
    return {
        "id": order.id,
        "orderNumber": order.order_number,
        "date": order.order_date.isoformat(),
        "reference": order.reference_number,
        "vendorName": order.vendor_name,
        "status": order.status,
        "amount": _money(order.amount),
    }


def serialize_transfer(transfer: StockTransfer) -> dict:
    return {
        "id": transfer.id,
        "transferNumber": transfer.transfer_number,
        "source": transfer.source_warehouse,
        "destination": transfer.destination_warehouse,
        "status": transfer.status,
        "items": transfer.items_count,
        "updatedAt": transfer.updated_at.strftime("%Y-%m-%d %H:%M"),
    }


def serialize_adjustment(adjustment: InventoryAdjustment) -> dict:
    return {
        "id": adjustment.id,
        "adjustmentNumber": adjustment.adjustment_number,
        "date": adjustment.created_at.strftime("%Y-%m-%d"),
        "warehouse": adjustment.warehouse_name,
        "reason": adjustment.reason,
        "status": adjustment.status,
        "quantity": f"{adjustment.quantity:+d}",
    }


def serialize_transaction(transaction: InventoryTransaction) -> dict:
    return {
        "id": transaction.id,
        "date": transaction.created_at.strftime("%Y-%m-%d %H:%M"),
        "type": transaction.transaction_type,
        "product": transaction.product_name,
        "warehouse": transaction.warehouse_name,
        "user": transaction.actor_name,
        "reference": transaction.reference_number,
        "quantity": f"{transaction.quantity:+d}",
    }


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "lastLogin": user.last_login_at.strftime("%Y-%m-%d %H:%M") if user.last_login_at else "Never",
    }


def serialize_tenant(tenant: Tenant, db: Session) -> dict:
    user_count = db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant.id)) or 0
    return {
        "id": tenant.id,
        "companyName": tenant.company_name,
        "contactEmail": tenant.contact_email,
        "plan": tenant.plan,
        "status": tenant.status,
        "users": user_count,
    }


def serialize_activity_log(log: ActivityLog) -> dict:
    return {
        "id": log.id,
        "actor": log.actor_name,
        "action": log.action,
        "module": log.module,
        "createdAt": log.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def serialize_audit_log(log: AuditLog) -> dict:
    return {
        "id": log.id,
        "actor": log.actor_name,
        "action": log.action,
        "module": log.module,
        "severity": log.severity,
        "createdAt": log.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def serialize_notification(notification: Notification) -> dict:
    return {
        "id": notification.id,
        "title": notification.title,
        "detail": notification.detail,
        "time": notification.created_at.strftime("%Y-%m-%d %H:%M"),
        "unread": notification.unread,
    }


def serialize_top_product(product: Product) -> dict:
    return {
        "name": product.name,
        "sku": product.sku,
        "units": max(product.stock_on_hand // 3, 4),
        "revenue": _money(float(product.selling_price) * max(product.stock_on_hand // 3, 4)),
    }


def serialize_top_stock(product: Product) -> dict:
    return {
        "name": product.name,
        "quantity": product.stock_on_hand,
        "value": _money(float(product.cost_price) * product.stock_on_hand),
    }


def _next_document_number(db: Session, model, prefix: str, base_number: int) -> str:
    number_values = []
    for value in db.scalars(select(model.order_number)):
        try:
            number_values.append(int(str(value).split("-")[-1]))
        except (TypeError, ValueError):
            continue

    if not number_values:
        return f"{prefix}-{base_number}"
    return f"{prefix}-{max(number_values) + 1}"
