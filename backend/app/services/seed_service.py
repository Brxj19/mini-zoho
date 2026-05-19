from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.brand import Brand
from app.models.category import Category
from app.models.customer import Customer
from app.models.enums import (
    InventoryTransactionTypeEnum,
    NotificationTypeEnum,
    PurchaseOrderStatusEnum,
    RecordStatusEnum,
    RoleEnum,
    SalesOrderStatusEnum,
    StockTransferStatusEnum,
    TenantStatusEnum,
    UserStatusEnum,
)
from app.models.inventory_transaction import InventoryTransaction
from app.models.notification import Notification
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.stock_transfer import StockTransfer
from app.models.stock_transfer_item import StockTransferItem
from app.models.tenant import Tenant
from app.models.user import User
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock


DEMO_TENANT_NAME = "Northstar Retail India"


def ensure_demo_workspace(db: Session) -> None:
    existing_tenant = db.scalar(select(Tenant).where(Tenant.company_name == DEMO_TENANT_NAME))
    if existing_tenant:
        return

    tenant = Tenant(
        company_name=DEMO_TENANT_NAME,
        contact_email="ops@northstarretail.in",
        phone="+91 9876512001",
        address="12th Main Road, Indiranagar, Bengaluru",
        gst_number="29AAGCN1123A1ZX",
        business_type="Retail Furniture & Lifestyle",
        status=TenantStatusEnum.ACTIVE,
        subscription_plan_id=2,
    )
    db.add(tenant)
    db.flush()

    users = {
        "admin": User(
            tenant_id=tenant.id,
            name="Akash Sharma",
            email="akash@northstarretail.in",
            password_hash=hash_password("ChangeMe123!"),
            role=RoleEnum.TENANT_ADMIN,
            status=UserStatusEnum.ACTIVE,
            last_login_at=datetime.now(UTC),
        ),
        "inventory": User(
            tenant_id=tenant.id,
            name="Rohit Verma",
            email="rohit@northstarretail.in",
            password_hash=hash_password("ChangeMe123!"),
            role=RoleEnum.INVENTORY_MANAGER,
            status=UserStatusEnum.ACTIVE,
            last_login_at=datetime.now(UTC),
        ),
        "sales": User(
            tenant_id=tenant.id,
            name="Pooja Nair",
            email="pooja@northstarretail.in",
            password_hash=hash_password("ChangeMe123!"),
            role=RoleEnum.SALES_STAFF,
            status=UserStatusEnum.ACTIVE,
            last_login_at=datetime.now(UTC),
        ),
        "purchase": User(
            tenant_id=tenant.id,
            name="Nikhil Rao",
            email="nikhil@northstarretail.in",
            password_hash=hash_password("ChangeMe123!"),
            role=RoleEnum.PURCHASE_STAFF,
            status=UserStatusEnum.ACTIVE,
            last_login_at=datetime.now(UTC),
        ),
        "viewer": User(
            tenant_id=tenant.id,
            name="Meera Iyer",
            email="meera@northstarretail.in",
            password_hash=hash_password("ChangeMe123!"),
            role=RoleEnum.VIEWER,
            status=UserStatusEnum.ACTIVE,
            last_login_at=datetime.now(UTC),
        ),
    }
    db.add_all(users.values())
    db.flush()

    categories = {
        "furniture": Category(tenant_id=tenant.id, name="Office Furniture", description="Desks, chairs, and workstations", status=RecordStatusEnum.ACTIVE),
        "lighting": Category(tenant_id=tenant.id, name="Lighting", description="Desk and ambient lighting", status=RecordStatusEnum.ACTIVE),
        "storage": Category(tenant_id=tenant.id, name="Storage", description="Shelving, baskets, and organizers", status=RecordStatusEnum.ACTIVE),
    }
    brands = {
        "northstar": Brand(tenant_id=tenant.id, name="Northstar", description="In-house workspace range", status=RecordStatusEnum.ACTIVE),
        "sutradhar": Brand(tenant_id=tenant.id, name="Sutradhar", description="Craft-led woodwork", status=RecordStatusEnum.ACTIVE),
        "aarambh": Brand(tenant_id=tenant.id, name="Aarambh", description="Decor and utility line", status=RecordStatusEnum.ACTIVE),
    }
    db.add_all([*categories.values(), *brands.values()])
    db.flush()

    warehouses = {
        "blr": Warehouse(
            tenant_id=tenant.id,
            name="Central Warehouse",
            code="BLR-CEN",
            address="Mahadevapura Industrial Area, Bengaluru",
            city="Bengaluru",
            state="Karnataka",
            country="India",
            manager_name="Akash Sharma",
            phone="+91 9845012300",
            is_default=True,
            status=RecordStatusEnum.ACTIVE,
        ),
        "del": Warehouse(
            tenant_id=tenant.id,
            name="North Hub",
            code="DEL-NTH",
            address="Okhla Phase II, New Delhi",
            city="New Delhi",
            state="Delhi",
            country="India",
            manager_name="Pooja Nair",
            phone="+91 9810012300",
            is_default=False,
            status=RecordStatusEnum.ACTIVE,
        ),
        "pun": Warehouse(
            tenant_id=tenant.id,
            name="Pune Overflow",
            code="PUN-OVR",
            address="Bhosari MIDC, Pune",
            city="Pune",
            state="Maharashtra",
            country="India",
            manager_name="Nikhil Rao",
            phone="+91 9822012300",
            is_default=False,
            status=RecordStatusEnum.ACTIVE,
        ),
    }
    db.add_all(warehouses.values())
    db.flush()

    vendors = {
        "kaveri": Vendor(
            tenant_id=tenant.id,
            name="Kaveri Woods",
            email="sales@kaveriwoods.in",
            phone="+91 9988721001",
            gst_number="29AAKCK2190F1ZQ",
            address="Lashkar Mohalla, Mysuru",
            opening_balance=Decimal("0.00"),
            status=RecordStatusEnum.ACTIVE,
        ),
        "prakash": Vendor(
            tenant_id=tenant.id,
            name="Prakash Metal Works",
            email="orders@prakashmetal.in",
            phone="+91 9988721002",
            gst_number="24AALPP3812D1Z8",
            address="Aji GIDC, Rajkot",
            opening_balance=Decimal("0.00"),
            status=RecordStatusEnum.ACTIVE,
        ),
        "nexa": Vendor(
            tenant_id=tenant.id,
            name="Nexa Lamps",
            email="contact@nexalamps.in",
            phone="+91 9988721003",
            gst_number="09AACCN8831Q1ZS",
            address="Sector 63, Noida",
            opening_balance=Decimal("0.00"),
            status=RecordStatusEnum.ACTIVE,
        ),
    }
    customers = {
        "aarohi": Customer(
            tenant_id=tenant.id,
            name="Aarohi Interiors",
            email="ops@aarohiinteriors.in",
            phone="+91 9988731001",
            gst_number="27AAHCA0931A1ZV",
            billing_address="Lower Parel, Mumbai",
            shipping_address="Andheri East, Mumbai",
            status=RecordStatusEnum.ACTIVE,
        ),
        "blue": Customer(
            tenant_id=tenant.id,
            name="Blue Banyan Offices",
            email="buying@bluebanyan.co",
            phone="+91 9988731002",
            gst_number="36AACCB1902N1Z5",
            billing_address="Gachibowli, Hyderabad",
            shipping_address="Madhapur, Hyderabad",
            status=RecordStatusEnum.ACTIVE,
        ),
        "urban": Customer(
            tenant_id=tenant.id,
            name="Urban Nest Retail",
            email="stores@urbannest.in",
            phone="+91 9988731003",
            gst_number="24AACCU1181E1Z6",
            billing_address="Satellite, Ahmedabad",
            shipping_address="Bodakdev, Ahmedabad",
            status=RecordStatusEnum.ACTIVE,
        ),
    }
    db.add_all([*vendors.values(), *customers.values()])
    db.flush()

    products = {
        "table": Product(
            tenant_id=tenant.id,
            name="Sheesham Study Table",
            sku="NST-OFC-101",
            barcode="8906007201001",
            category_id=categories["furniture"].id,
            brand_id=brands["northstar"].id,
            vendor_id=vendors["kaveri"].id,
            description="Solid sheesham wood desk for office and study setups.",
            unit="pcs",
            cost_price=Decimal("13240.00"),
            selling_price=Decimal("18999.00"),
            reorder_level=16,
            status=RecordStatusEnum.ACTIVE,
        ),
        "chair": Product(
            tenant_id=tenant.id,
            name="Ergonomic Mesh Kursi",
            sku="NST-OFC-102",
            barcode="8906007201002",
            category_id=categories["furniture"].id,
            brand_id=brands["sutradhar"].id,
            vendor_id=vendors["prakash"].id,
            description="Breathable ergonomic chair with lumbar support.",
            unit="pcs",
            cost_price=Decimal("4980.00"),
            selling_price=Decimal("7499.00"),
            reorder_level=24,
            status=RecordStatusEnum.ACTIVE,
        ),
        "lamp": Product(
            tenant_id=tenant.id,
            name="Brass Finish Desk Lamp",
            sku="NST-LGT-103",
            barcode="8906007201003",
            category_id=categories["lighting"].id,
            brand_id=brands["aarambh"].id,
            vendor_id=vendors["nexa"].id,
            description="Warm brass desk lamp with focused task lighting.",
            unit="pcs",
            cost_price=Decimal("1540.00"),
            selling_price=Decimal("2899.00"),
            reorder_level=20,
            status=RecordStatusEnum.ACTIVE,
        ),
        "basket": Product(
            tenant_id=tenant.id,
            name="Jute Storage Basket Set",
            sku="NST-STO-104",
            barcode="8906007201004",
            category_id=categories["storage"].id,
            brand_id=brands["aarambh"].id,
            vendor_id=vendors["nexa"].id,
            description="Set of nested jute baskets for display and storage.",
            unit="set",
            cost_price=Decimal("1120.00"),
            selling_price=Decimal("2199.00"),
            reorder_level=36,
            status=RecordStatusEnum.ACTIVE,
        ),
        "copper": Product(
            tenant_id=tenant.id,
            name="Copper Bottle Gift Set",
            sku="NST-GFT-105",
            barcode="8906007201005",
            category_id=categories["storage"].id,
            brand_id=brands["sutradhar"].id,
            vendor_id=vendors["prakash"].id,
            description="Hammered copper bottle and tumbler gift set.",
            unit="set",
            cost_price=Decimal("920.00"),
            selling_price=Decimal("1599.00"),
            reorder_level=18,
            status=RecordStatusEnum.ACTIVE,
        ),
    }
    db.add_all(products.values())
    db.flush()

    stock_rows = [
        WarehouseStock(tenant_id=tenant.id, warehouse_id=warehouses["blr"].id, product_id=products["table"].id, quantity=24, reserved_quantity=2, available_quantity=22, reorder_level=16),
        WarehouseStock(tenant_id=tenant.id, warehouse_id=warehouses["del"].id, product_id=products["table"].id, quantity=10, reserved_quantity=1, available_quantity=9, reorder_level=16),
        WarehouseStock(tenant_id=tenant.id, warehouse_id=warehouses["pun"].id, product_id=products["table"].id, quantity=8, reserved_quantity=0, available_quantity=8, reorder_level=16),
        WarehouseStock(tenant_id=tenant.id, warehouse_id=warehouses["blr"].id, product_id=products["chair"].id, quantity=18, reserved_quantity=4, available_quantity=14, reorder_level=24),
        WarehouseStock(tenant_id=tenant.id, warehouse_id=warehouses["del"].id, product_id=products["chair"].id, quantity=6, reserved_quantity=0, available_quantity=6, reorder_level=24),
        WarehouseStock(tenant_id=tenant.id, warehouse_id=warehouses["blr"].id, product_id=products["lamp"].id, quantity=52, reserved_quantity=3, available_quantity=49, reorder_level=20),
        WarehouseStock(tenant_id=tenant.id, warehouse_id=warehouses["pun"].id, product_id=products["lamp"].id, quantity=24, reserved_quantity=0, available_quantity=24, reorder_level=20),
        WarehouseStock(tenant_id=tenant.id, warehouse_id=warehouses["blr"].id, product_id=products["basket"].id, quantity=64, reserved_quantity=0, available_quantity=64, reorder_level=36),
        WarehouseStock(tenant_id=tenant.id, warehouse_id=warehouses["blr"].id, product_id=products["copper"].id, quantity=12, reserved_quantity=0, available_quantity=12, reorder_level=18),
    ]
    db.add_all(stock_rows)

    purchase_orders = [
        PurchaseOrder(
            tenant_id=tenant.id,
            vendor_id=vendors["kaveri"].id,
            po_number="PO-204",
            order_date=date(2026, 5, 18),
            expected_delivery_date=date(2026, 5, 25),
            status=PurchaseOrderStatusEnum.ISSUED,
            subtotal=Decimal("105920.00"),
            tax_amount=Decimal("12710.40"),
            total_amount=Decimal("118630.40"),
            notes="Check finish consistency before warehouse acceptance.",
            created_by=users["purchase"].id,
        ),
        PurchaseOrder(
            tenant_id=tenant.id,
            vendor_id=vendors["prakash"].id,
            po_number="PO-203",
            order_date=date(2026, 5, 16),
            expected_delivery_date=date(2026, 5, 24),
            status=PurchaseOrderStatusEnum.PARTIALLY_RECEIVED,
            subtotal=Decimal("36960.00"),
            tax_amount=Decimal("4435.20"),
            total_amount=Decimal("41395.20"),
            notes="Balance shipment due by weekend.",
            created_by=users["purchase"].id,
        ),
    ]
    db.add_all(purchase_orders)
    db.flush()

    db.add_all(
        [
            PurchaseOrderItem(
                purchase_order_id=purchase_orders[0].id,
                product_id=products["table"].id,
                warehouse_id=warehouses["blr"].id,
                quantity_ordered=8,
                quantity_received=0,
                unit_price=Decimal("13240.00"),
                tax_rate=Decimal("12.00"),
                total_price=Decimal("118630.40"),
            ),
            PurchaseOrderItem(
                purchase_order_id=purchase_orders[1].id,
                product_id=products["lamp"].id,
                warehouse_id=warehouses["blr"].id,
                quantity_ordered=24,
                quantity_received=10,
                unit_price=Decimal("1540.00"),
                tax_rate=Decimal("12.00"),
                total_price=Decimal("41395.20"),
            ),
        ]
    )

    sales_orders = [
        SalesOrder(
            tenant_id=tenant.id,
            customer_id=customers["aarohi"].id,
            so_number="SO-210",
            order_date=date(2026, 5, 18),
            status=SalesOrderStatusEnum.CONFIRMED,
            subtotal=Decimal("35794.00"),
            tax_amount=Decimal("4295.28"),
            discount_amount=Decimal("1000.00"),
            total_amount=Decimal("39089.28"),
            notes="Dispatch only after final packing photos.",
            created_by=users["sales"].id,
        ),
        SalesOrder(
            tenant_id=tenant.id,
            customer_id=customers["blue"].id,
            so_number="SO-209",
            order_date=date(2026, 5, 17),
            status=SalesOrderStatusEnum.SHIPPED,
            subtotal=Decimal("18999.00"),
            tax_amount=Decimal("2279.88"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("21278.88"),
            notes="Corporate order with partial shipment approved.",
            created_by=users["sales"].id,
        ),
    ]
    db.add_all(sales_orders)
    db.flush()

    db.add_all(
        [
            SalesOrderItem(
                sales_order_id=sales_orders[0].id,
                product_id=products["chair"].id,
                warehouse_id=warehouses["blr"].id,
                quantity=4,
                unit_price=Decimal("7499.00"),
                tax_rate=Decimal("12.00"),
                discount=Decimal("1000.00"),
                total_price=Decimal("32595.52"),
            ),
            SalesOrderItem(
                sales_order_id=sales_orders[0].id,
                product_id=products["lamp"].id,
                warehouse_id=warehouses["blr"].id,
                quantity=2,
                unit_price=Decimal("2899.00"),
                tax_rate=Decimal("12.00"),
                discount=Decimal("0.00"),
                total_price=Decimal("6493.76"),
            ),
            SalesOrderItem(
                sales_order_id=sales_orders[1].id,
                product_id=products["table"].id,
                warehouse_id=warehouses["blr"].id,
                quantity=1,
                unit_price=Decimal("18999.00"),
                tax_rate=Decimal("12.00"),
                discount=Decimal("0.00"),
                total_price=Decimal("21278.88"),
            ),
        ]
    )

    transfer = StockTransfer(
        tenant_id=tenant.id,
        source_warehouse_id=warehouses["blr"].id,
        destination_warehouse_id=warehouses["del"].id,
        status=StockTransferStatusEnum.IN_TRANSIT,
        notes="Delhi project replenishment before client installation.",
        created_by=users["inventory"].id,
    )
    db.add(transfer)
    db.flush()
    db.add(
        StockTransferItem(
            stock_transfer_id=transfer.id,
            product_id=products["lamp"].id,
            quantity=6,
        )
    )

    inventory_transactions = [
        InventoryTransaction(
            tenant_id=tenant.id,
            product_id=products["table"].id,
            warehouse_id=warehouses["blr"].id,
            transaction_type=InventoryTransactionTypeEnum.STOCK_IN,
            quantity=24,
            reference_type="OPENING_BALANCE",
            reference_id=None,
            note="Initial seeded opening stock",
            created_by=users["inventory"].id,
        ),
        InventoryTransaction(
            tenant_id=tenant.id,
            product_id=products["chair"].id,
            warehouse_id=warehouses["blr"].id,
            transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_RESERVE,
            quantity=-4,
            reference_type="sales_order",
            reference_id=sales_orders[0].id,
            note="Reserved for SO-210",
            created_by=users["sales"].id,
        ),
        InventoryTransaction(
            tenant_id=tenant.id,
            product_id=products["lamp"].id,
            warehouse_id=warehouses["blr"].id,
            destination_warehouse_id=warehouses["del"].id,
            transaction_type=InventoryTransactionTypeEnum.TRANSFER_OUT,
            quantity=-6,
            reference_type="stock_transfer",
            reference_id=transfer.id,
            note="Transfer to North Hub",
            created_by=users["inventory"].id,
        ),
    ]
    db.add_all(inventory_transactions)

    db.add_all(
        [
            Notification(
                tenant_id=tenant.id,
                user_id=users["admin"].id,
                title="Low stock watchlist updated",
                message="Ergonomic Mesh Kursi and Copper Bottle Gift Set are below reorder level.",
                type=NotificationTypeEnum.LOW_STOCK,
                is_read=False,
            ),
            Notification(
                tenant_id=tenant.id,
                user_id=users["purchase"].id,
                title="Vendor receipt still pending",
                message="PO-204 is issued and awaiting receipt at Central Warehouse.",
                type=NotificationTypeEnum.PURCHASE_RECEIVE,
                is_read=False,
            ),
            Notification(
                tenant_id=tenant.id,
                user_id=users["sales"].id,
                title="Sales order ready for packing",
                message="SO-210 has reserved stock and can move to packing.",
                type=NotificationTypeEnum.ORDER_STATUS,
                is_read=False,
            ),
        ]
    )

    db.add_all(
        [
            AuditLog(
                tenant_id=tenant.id,
                user_id=users["inventory"].id,
                action="inventory.transfer.created",
                entity_type="stock_transfer",
                entity_id=transfer.id,
                new_value_json={"status": transfer.status.value},
            ),
            AuditLog(
                tenant_id=tenant.id,
                user_id=users["sales"].id,
                action="sales_order.confirmed",
                entity_type="sales_order",
                entity_id=sales_orders[0].id,
                new_value_json={"status": sales_orders[0].status.value},
            ),
            AuditLog(
                tenant_id=tenant.id,
                user_id=users["purchase"].id,
                action="purchase_order.issued",
                entity_type="purchase_order",
                entity_id=purchase_orders[0].id,
                new_value_json={"status": purchase_orders[0].status.value},
            ),
        ]
    )

    db.commit()
