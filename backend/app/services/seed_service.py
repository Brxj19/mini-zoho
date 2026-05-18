from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.core.security import hash_password
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


def rebuild_schema_if_needed(db: Session) -> bool:
    inspector = inspect(db.bind)
    required_columns = {
        "products": {"stock_on_hand", "reorder_level", "selling_price", "cost_price"},
        "users": {"role", "password_hash", "status"},
        "sales_orders": {"order_number", "items_json", "status"},
    }

    should_rebuild = False
    for table_name, columns in required_columns.items():
        if not inspector.has_table(table_name):
            continue
        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        if not columns.issubset(existing_columns):
            should_rebuild = True
            break

    if should_rebuild:
        from app.models import Base

        all_tables = inspector.get_table_names()
        if all_tables:
            db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            for table_name in all_tables:
                db.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
            db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            db.commit()
        Base.metadata.create_all(bind=db.bind)

    return should_rebuild


def seed_demo_data(db: Session, super_admin_email: str, super_admin_password: str) -> None:
    existing_user = db.scalar(select(User).where(User.email == super_admin_email))
    if existing_user:
        return

    northstar = Tenant(
        company_name="Northstar Retail India",
        contact_email="ops@northstarretail.in",
        phone="+91 98765 12001",
        address="Indiranagar, Bengaluru",
        city="Bengaluru",
        state="Karnataka",
        industry="Retail",
        currency="INR",
        timezone="Asia/Kolkata",
        plan="Growth",
        status="ACTIVE",
        setup_completed=True,
    )
    sahyadri = Tenant(
        company_name="Sahyadri Living",
        contact_email="hello@sahyadriliving.in",
        phone="+91 98765 12002",
        address="Koregaon Park, Pune",
        city="Pune",
        state="Maharashtra",
        industry="Home & Lifestyle",
        currency="INR",
        timezone="Asia/Kolkata",
        plan="Starter",
        status="ACTIVE",
        setup_completed=True,
    )
    db.add_all([northstar, sahyadri])
    db.flush()

    users = [
        User(
            tenant_id=None,
            name="Brajesh Kumar",
            email=super_admin_email,
            password_hash=hash_password(super_admin_password),
            role="SUPER_ADMIN",
            status="ACTIVE",
            last_login_at=datetime.now(UTC),
        ),
        User(
            tenant_id=northstar.id,
            name="Akash Sharma",
            email="akash@northstarretail.in",
            password_hash=hash_password("ChangeMe123!"),
            role="TENANT_ADMIN",
            status="ACTIVE",
            last_login_at=datetime.now(UTC),
        ),
        User(
            tenant_id=northstar.id,
            name="Rohit Verma",
            email="rohit@northstarretail.in",
            password_hash=hash_password("ChangeMe123!"),
            role="INVENTORY_MANAGER",
            status="ACTIVE",
            last_login_at=datetime.now(UTC),
        ),
        User(
            tenant_id=northstar.id,
            name="Pooja Nair",
            email="pooja@northstarretail.in",
            password_hash=hash_password("ChangeMe123!"),
            role="SALES_STAFF",
            status="ACTIVE",
            last_login_at=datetime.now(UTC),
        ),
        User(
            tenant_id=northstar.id,
            name="Nikhil Rao",
            email="nikhil@northstarretail.in",
            password_hash=hash_password("ChangeMe123!"),
            role="PURCHASE_STAFF",
            status="ACTIVE",
            last_login_at=datetime.now(UTC),
        ),
    ]
    db.add_all(users)
    db.flush()

    categories = [
        Category(tenant_id=northstar.id, name="Office Furniture", status="ACTIVE"),
        Category(tenant_id=northstar.id, name="Lighting", status="ACTIVE"),
        Category(tenant_id=northstar.id, name="Storage", status="ACTIVE"),
    ]
    brands = [
        Brand(tenant_id=northstar.id, name="Northstar", status="ACTIVE"),
        Brand(tenant_id=northstar.id, name="Sutradhar", status="ACTIVE"),
        Brand(tenant_id=northstar.id, name="Aarambh", status="ACTIVE"),
    ]
    db.add_all(categories + brands)
    db.flush()

    warehouses = [
        Warehouse(
            tenant_id=northstar.id,
            name="Central Warehouse",
            city="Bengaluru",
            state="Karnataka",
            manager_name="Akash Sharma",
            stock_count=684,
            is_primary=True,
            status="ACTIVE",
        ),
        Warehouse(
            tenant_id=northstar.id,
            name="North Hub",
            city="Delhi",
            state="Delhi",
            manager_name="Pooja Nair",
            stock_count=228,
            is_primary=False,
            status="ACTIVE",
        ),
        Warehouse(
            tenant_id=northstar.id,
            name="Pune Overflow",
            city="Pune",
            state="Maharashtra",
            manager_name="Nikhil Rao",
            stock_count=64,
            is_primary=False,
            status="INACTIVE",
        ),
    ]
    db.add_all(warehouses)

    vendors = [
        Vendor(tenant_id=northstar.id, name="Kaveri Woods", email="sales@kaveriwoods.in", phone="+91 99887 21001", city="Mysuru", status="ACTIVE"),
        Vendor(tenant_id=northstar.id, name="Prakash Metal Works", email="orders@prakashmetal.in", phone="+91 99887 21002", city="Rajkot", status="ACTIVE"),
        Vendor(tenant_id=northstar.id, name="Nexa Lamps", email="contact@nexalamps.in", phone="+91 99887 21003", city="Noida", status="ACTIVE"),
        Vendor(tenant_id=northstar.id, name="Jutegram", email="support@jutegram.in", phone="+91 99887 21004", city="Kolkata", status="INACTIVE"),
    ]
    customers = [
        Customer(tenant_id=northstar.id, name="Aarohi Interiors", email="ops@aarohiinteriors.in", phone="+91 99887 31001", city="Mumbai", status="ACTIVE"),
        Customer(tenant_id=northstar.id, name="Blue Banyan Offices", email="buying@bluebanyan.co", phone="+91 99887 31002", city="Hyderabad", status="ACTIVE"),
        Customer(tenant_id=northstar.id, name="Craftmela Studio", email="hello@craftmela.in", phone="+91 99887 31003", city="Chennai", status="INACTIVE"),
        Customer(tenant_id=northstar.id, name="Urban Nest Retail", email="stores@urbannest.in", phone="+91 99887 31004", city="Ahmedabad", status="ACTIVE"),
    ]
    db.add_all(vendors + customers)
    db.flush()

    product_rows = [
        {
            "name": "Sheesham Study Table",
            "sku": "NST-OFC-101",
            "category": categories[0],
            "brand": brands[0],
            "barcode": "8906007201001",
            "selling_price": Decimal("18999.00"),
            "cost_price": Decimal("13240.00"),
            "stock_on_hand": 42,
            "reorder_level": 16,
            "status": "ACTIVE",
            "sales_description": "Solid sheesham wood desk for office and study setups.",
            "purchase_description": "Vendor packed in flat sections with hardware kit.",
        },
        {
            "name": "Ergonomic Mesh Kursi",
            "sku": "NST-OFC-102",
            "category": categories[0],
            "brand": brands[1],
            "barcode": "8906007201002",
            "selling_price": Decimal("7499.00"),
            "cost_price": Decimal("4980.00"),
            "stock_on_hand": 18,
            "reorder_level": 24,
            "status": "LOW_STOCK",
            "sales_description": "Breathable ergonomic chair with lumbar support.",
            "purchase_description": "Ships semi-assembled with armrest kit.",
        },
        {
            "name": "Brass Finish Desk Lamp",
            "sku": "NST-LGT-103",
            "category": categories[1],
            "brand": brands[2],
            "barcode": "8906007201003",
            "selling_price": Decimal("2899.00"),
            "cost_price": Decimal("1540.00"),
            "stock_on_hand": 76,
            "reorder_level": 20,
            "status": "ACTIVE",
            "sales_description": "Warm brass desk lamp with focused task lighting.",
            "purchase_description": "Packed with LED bulb and plug adapter.",
        },
        {
            "name": "Jute Storage Basket Set",
            "sku": "NST-STO-104",
            "category": categories[2],
            "brand": brands[2],
            "barcode": "8906007201004",
            "selling_price": Decimal("2199.00"),
            "cost_price": Decimal("1120.00"),
            "stock_on_hand": 108,
            "reorder_level": 36,
            "status": "ACTIVE",
            "sales_description": "Woven jute basket set for shelves and storage corners.",
            "purchase_description": "Set of 3 nested baskets.",
        },
        {
            "name": "Copper Bottle Gift Set",
            "sku": "NST-LFS-105",
            "category": categories[2],
            "brand": brands[1],
            "barcode": "8906007201005",
            "selling_price": Decimal("1599.00"),
            "cost_price": Decimal("920.00"),
            "stock_on_hand": 0,
            "reorder_level": 18,
            "status": "INACTIVE",
            "sales_description": "Hammered copper bottle and tumbler gift set.",
            "purchase_description": "Festival seasonal assortment.",
        },
    ]

    products = [
        Product(
            tenant_id=northstar.id,
            category_id=row["category"].id,
            brand_id=row["brand"].id,
            name=row["name"],
            sku=row["sku"],
            unit="pcs",
            barcode=row["barcode"],
            selling_price=row["selling_price"],
            cost_price=row["cost_price"],
            stock_on_hand=row["stock_on_hand"],
            reorder_level=row["reorder_level"],
            status=row["status"],
            sales_description=row["sales_description"],
            purchase_description=row["purchase_description"],
        )
        for row in product_rows
    ]
    db.add_all(products)

    sales_orders = [
        SalesOrder(
            tenant_id=northstar.id,
            order_number="SO-210",
            reference_number="REF-4901",
            customer_name="Aarohi Interiors",
            status="CONFIRMED",
            amount=Decimal("8420.00"),
            order_date=date(2026, 5, 18),
            expected_shipment_date=date(2026, 5, 22),
            items_json=json.dumps(
                [
                    {"name": "Ergonomic Mesh Kursi", "warehouse": "Central Warehouse", "quantity": 4, "rate": 7499},
                    {"name": "Brass Finish Desk Lamp", "warehouse": "Central Warehouse", "quantity": 2, "rate": 2899},
                ]
            ),
            notes="Customer requested dispatch only after final packing photos.",
        ),
        SalesOrder(
            tenant_id=northstar.id,
            order_number="SO-209",
            reference_number="REF-4900",
            customer_name="Blue Banyan Offices",
            status="PACKED",
            amount=Decimal("14220.00"),
            order_date=date(2026, 5, 17),
            expected_shipment_date=date(2026, 5, 20),
            items_json=json.dumps(
                [{"name": "Sheesham Study Table", "warehouse": "Central Warehouse", "quantity": 1, "rate": 18999}]
            ),
            notes="Corporate order, partial shipment allowed.",
        ),
    ]
    purchase_orders = [
        PurchaseOrder(
            tenant_id=northstar.id,
            order_number="PO-204",
            reference_number="V-3812",
            vendor_name="Kaveri Woods",
            status="ISSUED",
            amount=Decimal("11920.00"),
            order_date=date(2026, 5, 18),
            expected_delivery_date=date(2026, 5, 25),
            items_json=json.dumps(
                [{"name": "Sheesham Study Table", "quantity": 8, "rate": 13240}]
            ),
            notes="Need wood finish consistency check on arrival.",
        ),
        PurchaseOrder(
            tenant_id=northstar.id,
            order_number="PO-203",
            reference_number="V-3811",
            vendor_name="Prakash Metal Works",
            status="PARTIALLY_RECEIVED",
            amount=Decimal("16440.00"),
            order_date=date(2026, 5, 16),
            expected_delivery_date=date(2026, 5, 24),
            items_json=json.dumps(
                [{"name": "Brass Finish Desk Lamp", "quantity": 24, "rate": 1540}]
            ),
            notes="Balance shipment due by weekend.",
        ),
    ]
    transfers = [
        StockTransfer(
            tenant_id=northstar.id,
            transfer_number="TR-101",
            source_warehouse="Central Warehouse",
            destination_warehouse="North Hub",
            status="IN_TRANSIT",
            items_count=4,
            notes="Urgent replenishment for Delhi project dispatch.",
        ),
        StockTransfer(
            tenant_id=northstar.id,
            transfer_number="TR-100",
            source_warehouse="North Hub",
            destination_warehouse="Central Warehouse",
            status="COMPLETED",
            items_count=2,
            notes="Returned slow-moving stock to central holding.",
        ),
    ]
    adjustments = [
        InventoryAdjustment(
            tenant_id=northstar.id,
            adjustment_number="ADJ-051",
            warehouse_name="Central Warehouse",
            reason="Cycle count",
            quantity=12,
            status="COMPLETED",
        ),
        InventoryAdjustment(
            tenant_id=northstar.id,
            adjustment_number="ADJ-050",
            warehouse_name="North Hub",
            reason="Damaged stock",
            quantity=-3,
            status="COMPLETED",
        ),
    ]
    transactions = [
        InventoryTransaction(
            tenant_id=northstar.id,
            transaction_number="TX-9001",
            transaction_type="STOCK_IN",
            product_name="Sheesham Study Table",
            warehouse_name="Central Warehouse",
            actor_name="Akash Sharma",
            reference_number="PO-204",
            quantity=24,
        ),
        InventoryTransaction(
            tenant_id=northstar.id,
            transaction_number="TX-9002",
            transaction_type="TRANSFER_OUT",
            product_name="Brass Finish Desk Lamp",
            warehouse_name="Central Warehouse",
            actor_name="Rohit Verma",
            reference_number="TR-101",
            quantity=-8,
        ),
        InventoryTransaction(
            tenant_id=northstar.id,
            transaction_number="TX-9003",
            transaction_type="TRANSFER_IN",
            product_name="Brass Finish Desk Lamp",
            warehouse_name="North Hub",
            actor_name="Pooja Nair",
            reference_number="TR-101",
            quantity=8,
        ),
    ]
    activity_logs = [
        ActivityLog(tenant_id=northstar.id, actor_name="Akash Sharma", action="Completed transfer TR-100", module="Stock Transfers"),
        ActivityLog(tenant_id=northstar.id, actor_name="Pooja Nair", action="Packed sales order SO-209", module="Sales Orders"),
        ActivityLog(tenant_id=northstar.id, actor_name="Nikhil Rao", action="Issued purchase order PO-204", module="Purchase Orders"),
    ]
    audit_logs = [
        AuditLog(tenant_id=None, actor_name="Brajesh Kumar", action="Reviewed tenant plan usage", module="Tenants", severity="INFO"),
        AuditLog(tenant_id=northstar.id, actor_name="Akash Sharma", action="Adjusted stock for Ergonomic Mesh Kursi", module="Inventory", severity="WARNING"),
        AuditLog(tenant_id=None, actor_name="System", action="Generated weekly inventory snapshot", module="Reports", severity="SUCCESS"),
    ]
    notifications = [
        Notification(tenant_id=northstar.id, title="Low stock review pending", detail="Ergonomic Mesh Kursi is below reorder level.", unread=True),
        Notification(tenant_id=northstar.id, title="Purchase order ready to receive", detail="PO-204 has landed at Central Warehouse.", unread=True),
        Notification(tenant_id=None, title="Tenant growth summary updated", detail="May platform metrics are ready for review.", unread=False),
    ]

    db.add_all(sales_orders + purchase_orders + transfers + adjustments + transactions + activity_logs + audit_logs + notifications)
    db.commit()
