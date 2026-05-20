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
    BillStatusEnum,
    InventoryTransactionTypeEnum,
    InventorySerialStatusEnum,
    InvoiceStatusEnum,
    NotificationTypeEnum,
    PackageStatusEnum,
    PurchaseReceiveStatusEnum,
    PurchaseOrderStatusEnum,
    RecordStatusEnum,
    RoleEnum,
    SalesReturnStatusEnum,
    SalesOrderStatusEnum,
    StockTransferStatusEnum,
    TenantStatusEnum,
    UserStatusEnum,
)
from app.models.bill import Bill
from app.models.inventory_transaction import InventoryTransaction
from app.models.inventory_batch import InventoryBatch
from app.models.inventory_serial import InventorySerial
from app.models.invoice import Invoice
from app.models.notification import Notification
from app.models.package import Package
from app.models.package_item import PackageItem
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.purchase_receive import PurchaseReceive
from app.models.purchase_receive_item import PurchaseReceiveItem
from app.models.sales_return import SalesReturn
from app.models.sales_return_item import SalesReturnItem
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.stock_transfer import StockTransfer
from app.models.stock_transfer_item import StockTransferItem
from app.models.tenant import Tenant
from app.models.user import User
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock

PLATFORM_TENANT_NAME = "Northstar Platform Demo"
LARGE_TENANT_NAME = "Northstar Retail India"
SMALL_TENANT_NAME = "Clover Living Studio"
DEFAULT_PASSWORD = "ChangeMe123!"
CONNECTED_SEED_MARKER_EMAIL = "tenant.admin1@northstar-demo.local"


def ensure_demo_workspace(db: Session) -> None:
    if db.scalar(select(User.id).where(User.email == CONNECTED_SEED_MARKER_EMAIL)):
        return
    _seed_platform_workspace(db)
    _seed_large_workspace(db)
    _seed_small_workspace(db)


def _seed_platform_workspace(db: Session) -> None:
    existing_tenant = db.scalar(select(Tenant).where(Tenant.company_name == PLATFORM_TENANT_NAME))
    if existing_tenant:
        return

    tenant = Tenant(
        company_name=PLATFORM_TENANT_NAME,
        contact_email="platform-demo@northstar.in",
        phone="+91 9845011000",
        address="UB City, Bengaluru",
        gst_number="29AAACN3300P1ZZ",
        business_type="Platform Sandbox & Demo Workspace",
        status=TenantStatusEnum.ACTIVE,
        subscription_plan_id=2,
    )
    db.add(tenant)
    db.flush()

    users = _create_users(
        db,
        tenant.id,
        [
            {"key": "admin", "name": "Priya Menon", "email": "priya@platformdemo.in", "role": RoleEnum.TENANT_ADMIN},
            {"key": "viewer", "name": "Varun Bhatt", "email": "varun@platformdemo.in", "role": RoleEnum.VIEWER},
        ],
    )
    categories = _create_lookup_records(
        db,
        Category,
        tenant.id,
        [
            {"key": "ops", "name": "Ops Essentials", "description": "Tools used in platform demo kits", "status": RecordStatusEnum.ACTIVE},
            {"key": "display", "name": "Display Assets", "description": "Assets used in platform walkthroughs", "status": RecordStatusEnum.ACTIVE},
        ],
    )
    brands = _create_lookup_records(
        db,
        Brand,
        tenant.id,
        [
            {"key": "northstar", "name": "Northstar Demo", "description": "Internal demo line", "status": RecordStatusEnum.ACTIVE},
            {"key": "signal", "name": "Signal Desk", "description": "Ops utility label", "status": RecordStatusEnum.ACTIVE},
        ],
    )
    warehouses = _create_lookup_records(
        db,
        Warehouse,
        tenant.id,
        [
            {
                "key": "blr",
                "name": "Platform Demo Hub",
                "code": "PLT-BLR",
                "address": "Indiranagar, Bengaluru",
                "city": "Bengaluru",
                "state": "Karnataka",
                "country": "India",
                "manager_name": "Priya Menon",
                "phone": "+91 9845011001",
                "is_default": True,
                "status": RecordStatusEnum.ACTIVE,
            }
        ],
    )
    vendors = _create_lookup_records(
        db,
        Vendor,
        tenant.id,
        [
            {
                "key": "bharat",
                "name": "Bharat Office Supply",
                "email": "sales@bharatoffice.in",
                "phone": "+91 9900011011",
                "gst_number": "29AAFCB1001B1ZX",
                "address": "Rajajinagar, Bengaluru",
                "opening_balance": Decimal("0.00"),
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "skyline",
                "name": "Skyline Print Works",
                "email": "hello@skylineprint.in",
                "phone": "+91 9900011012",
                "gst_number": "29AAECS2001K1ZP",
                "address": "BTM Layout, Bengaluru",
                "opening_balance": Decimal("0.00"),
                "status": RecordStatusEnum.ACTIVE,
            },
        ],
    )
    customers = _create_lookup_records(
        db,
        Customer,
        tenant.id,
        [
            {
                "key": "anchor",
                "name": "Anchor Pilot Labs",
                "email": "ops@anchorpilot.in",
                "phone": "+91 9910012011",
                "gst_number": "29AAMCA1001L1ZX",
                "billing_address": "Koramangala, Bengaluru",
                "shipping_address": "Koramangala, Bengaluru",
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "retail",
                "name": "Demo Retail Lab",
                "email": "buying@demoretail.in",
                "phone": "+91 9910012012",
                "gst_number": "29AACCD2201P1ZL",
                "billing_address": "HSR Layout, Bengaluru",
                "shipping_address": "HSR Layout, Bengaluru",
                "status": RecordStatusEnum.ACTIVE,
            },
        ],
    )
    products = _create_products(
        db,
        tenant.id,
        categories,
        brands,
        vendors,
        [
            {
                "key": "kit",
                "name": "Platform Demo Starter Kit",
                "sku": "PLT-101",
                "barcode": "8906007202101",
                "category_key": "ops",
                "brand_key": "northstar",
                "vendor_key": "bharat",
                "description": "Compact inventory walkthrough kit for demos and trainings.",
                "unit": "kit",
                "cost_price": Decimal("3250.00"),
                "selling_price": Decimal("4999.00"),
                "reorder_level": 6,
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "display",
                "name": "Counter Display Stand",
                "sku": "PLT-102",
                "barcode": "8906007202102",
                "category_key": "display",
                "brand_key": "signal",
                "vendor_key": "skyline",
                "description": "Foldable display stand used in platform showcase events.",
                "unit": "pcs",
                "cost_price": Decimal("1450.00"),
                "selling_price": Decimal("2499.00"),
                "reorder_level": 8,
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "badge",
                "name": "Ops Badge Pack",
                "sku": "PLT-103",
                "barcode": "8906007202103",
                "category_key": "ops",
                "brand_key": "northstar",
                "vendor_key": "bharat",
                "description": "Printed badge and lanyard packs for internal demos.",
                "unit": "pack",
                "cost_price": Decimal("320.00"),
                "selling_price": Decimal("599.00"),
                "reorder_level": 20,
                "status": RecordStatusEnum.ACTIVE,
            },
        ],
    )
    _add_stock_rows(
        db,
        tenant.id,
        warehouses,
        products,
        [
            {"warehouse_key": "blr", "product_key": "kit", "quantity": 10, "reserved_quantity": 1, "reorder_level": 6},
            {"warehouse_key": "blr", "product_key": "display", "quantity": 7, "reserved_quantity": 0, "reorder_level": 8},
            {"warehouse_key": "blr", "product_key": "badge", "quantity": 42, "reserved_quantity": 4, "reorder_level": 20},
        ],
    )

    purchase_orders = _create_purchase_orders(
        db,
        tenant.id,
        vendors,
        warehouses,
        products,
        [
            {
                "key": "po1",
                "vendor_key": "bharat",
                "po_number": "PO-PLT-001",
                "order_date": date(2026, 5, 18),
                "expected_delivery_date": date(2026, 5, 24),
                "status": PurchaseOrderStatusEnum.RECEIVED,
                "subtotal": Decimal("6500.00"),
                "tax_amount": Decimal("780.00"),
                "total_amount": Decimal("7280.00"),
                "notes": "Demo kit top-up for internal showcase.",
                "created_by": users["admin"].id,
                "items": [
                    {
                        "product_key": "kit",
                        "warehouse_key": "blr",
                        "quantity_ordered": 2,
                        "quantity_received": 2,
                        "unit_price": Decimal("3250.00"),
                        "tax_rate": Decimal("12.00"),
                        "total_price": Decimal("7280.00"),
                    }
                ],
            }
        ],
    )
    sales_orders = _create_sales_orders(
        db,
        tenant.id,
        customers,
        warehouses,
        products,
        [
            {
                "key": "so1",
                "customer_key": "anchor",
                "so_number": "SO-PLT-001",
                "order_date": date(2026, 5, 19),
                "status": SalesOrderStatusEnum.DELIVERED,
                "subtotal": Decimal("4999.00"),
                "tax_amount": Decimal("599.88"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("5598.88"),
                "notes": "Internal pilot shipment.",
                "created_by": users["admin"].id,
                "items": [
                    {
                        "product_key": "kit",
                        "warehouse_key": "blr",
                        "quantity": 1,
                        "unit_price": Decimal("4999.00"),
                        "tax_rate": Decimal("12.00"),
                        "discount": Decimal("0.00"),
                        "total_price": Decimal("5598.88"),
                    }
                ],
            }
        ],
    )

    db.add_all(
        [
            InventoryTransaction(
                tenant_id=tenant.id,
                product_id=products["kit"].id,
                warehouse_id=warehouses["blr"].id,
                transaction_type=InventoryTransactionTypeEnum.STOCK_IN,
                quantity=10,
                reference_type="OPENING_BALANCE",
                reference_id=None,
                note="Platform seed opening stock",
                created_by=users["admin"].id,
            ),
            InventoryTransaction(
                tenant_id=tenant.id,
                product_id=products["kit"].id,
                warehouse_id=warehouses["blr"].id,
                transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_DEDUCT,
                quantity=-1,
                reference_type="sales_order",
                reference_id=sales_orders["so1"].id,
                note="Delivered to Anchor Pilot Labs",
                created_by=users["admin"].id,
            ),
        ]
    )
    db.add_all(
        [
            Notification(
                tenant_id=tenant.id,
                user_id=users["admin"].id,
                title="Demo workspace ready",
                message="Platform demo tenant has been seeded with sample inventory data.",
                type=NotificationTypeEnum.SYSTEM,
                is_read=False,
            ),
            Notification(
                tenant_id=tenant.id,
                user_id=users["viewer"].id,
                title="Display stand needs replenishment",
                message="Counter Display Stand has slipped below the reorder threshold.",
                type=NotificationTypeEnum.LOW_STOCK,
                is_read=False,
            ),
        ]
    )
    db.add_all(
        [
            AuditLog(
                tenant_id=tenant.id,
                user_id=users["admin"].id,
                action="seed.platform.created",
                entity_type="tenant",
                entity_id=tenant.id,
                new_value_json={"workspace": PLATFORM_TENANT_NAME},
            ),
            AuditLog(
                tenant_id=tenant.id,
                user_id=users["admin"].id,
                action="sales_order.delivered",
                entity_type="sales_order",
                entity_id=sales_orders["so1"].id,
                new_value_json={"status": sales_orders["so1"].status.value},
            ),
        ]
    )
    db.commit()


def _seed_large_workspace(db: Session) -> None:
    existing_tenant = db.scalar(select(Tenant).where(Tenant.company_name == LARGE_TENANT_NAME))
    if existing_tenant:
        _top_up_large_workspace(db, existing_tenant)
        return

    tenant = Tenant(
        company_name=LARGE_TENANT_NAME,
        contact_email="ops@northstarretail.in",
        phone="+91 9876512001",
        address="12th Main Road, Indiranagar, Bengaluru",
        gst_number="29AAGCN1123A1ZX",
        business_type="Retail Furniture, Decor & Lifestyle",
        status=TenantStatusEnum.ACTIVE,
        subscription_plan_id=3,
    )
    db.add(tenant)
    db.flush()

    users = _create_users(
        db,
        tenant.id,
        [
            {"key": "admin", "name": "Akash Sharma", "email": "akash@northstarretail.in", "role": RoleEnum.TENANT_ADMIN},
            {"key": "inventory", "name": "Rohit Verma", "email": "rohit@northstarretail.in", "role": RoleEnum.INVENTORY_MANAGER},
            {"key": "sales", "name": "Pooja Nair", "email": "pooja@northstarretail.in", "role": RoleEnum.SALES_STAFF},
            {"key": "purchase", "name": "Nikhil Rao", "email": "nikhil@northstarretail.in", "role": RoleEnum.PURCHASE_STAFF},
            {"key": "viewer", "name": "Meera Iyer", "email": "meera@northstarretail.in", "role": RoleEnum.VIEWER},
        ],
    )
    categories = _create_lookup_records(
        db,
        Category,
        tenant.id,
        [
            {"key": "furniture", "name": "Office Furniture", "description": "Desks, chairs, and workstations", "status": RecordStatusEnum.ACTIVE},
            {"key": "lighting", "name": "Lighting", "description": "Task and ambient lighting", "status": RecordStatusEnum.ACTIVE},
            {"key": "storage", "name": "Storage", "description": "Shelving, boxes, and organizers", "status": RecordStatusEnum.ACTIVE},
            {"key": "decor", "name": "Decor", "description": "Accent pieces and planters", "status": RecordStatusEnum.ACTIVE},
            {"key": "serveware", "name": "Serveware", "description": "Gifting and hospitality sets", "status": RecordStatusEnum.ACTIVE},
            {"key": "textiles", "name": "Soft Furnishings", "description": "Cushions, throws, and runners", "status": RecordStatusEnum.ACTIVE},
        ],
    )
    brands = _create_lookup_records(
        db,
        Brand,
        tenant.id,
        [
            {"key": "northstar", "name": "Northstar", "description": "In-house workspace range", "status": RecordStatusEnum.ACTIVE},
            {"key": "sutradhar", "name": "Sutradhar", "description": "Craft-led woodwork", "status": RecordStatusEnum.ACTIVE},
            {"key": "aarambh", "name": "Aarambh", "description": "Decor and utility line", "status": RecordStatusEnum.ACTIVE},
            {"key": "veda", "name": "Veda Home", "description": "Contemporary home accents", "status": RecordStatusEnum.ACTIVE},
            {"key": "nila", "name": "Nila Living", "description": "Soft furnishings and hosting accessories", "status": RecordStatusEnum.ACTIVE},
        ],
    )
    warehouses = _create_lookup_records(
        db,
        Warehouse,
        tenant.id,
        [
            {
                "key": "blr",
                "name": "Central Warehouse",
                "code": "BLR-CEN",
                "address": "Mahadevapura Industrial Area, Bengaluru",
                "city": "Bengaluru",
                "state": "Karnataka",
                "country": "India",
                "manager_name": "Akash Sharma",
                "phone": "+91 9845012300",
                "is_default": True,
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "del",
                "name": "North Hub",
                "code": "DEL-NTH",
                "address": "Okhla Phase II, New Delhi",
                "city": "New Delhi",
                "state": "Delhi",
                "country": "India",
                "manager_name": "Pooja Nair",
                "phone": "+91 9810012300",
                "is_default": False,
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "pun",
                "name": "Pune Overflow",
                "code": "PUN-OVR",
                "address": "Bhosari MIDC, Pune",
                "city": "Pune",
                "state": "Maharashtra",
                "country": "India",
                "manager_name": "Nikhil Rao",
                "phone": "+91 9822012300",
                "is_default": False,
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "hyd",
                "name": "South Distribution Hub",
                "code": "HYD-SOU",
                "address": "Kompally Logistics Park, Hyderabad",
                "city": "Hyderabad",
                "state": "Telangana",
                "country": "India",
                "manager_name": "Rohit Verma",
                "phone": "+91 9849012300",
                "is_default": False,
                "status": RecordStatusEnum.ACTIVE,
            },
        ],
    )
    vendors = _create_lookup_records(
        db,
        Vendor,
        tenant.id,
        [
            {"key": "kaveri", "name": "Kaveri Woods", "email": "sales@kaveriwoods.in", "phone": "+91 9988721001", "gst_number": "29AAKCK2190F1ZQ", "address": "Lashkar Mohalla, Mysuru", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "prakash", "name": "Prakash Metal Works", "email": "orders@prakashmetal.in", "phone": "+91 9988721002", "gst_number": "24AALPP3812D1Z8", "address": "Aji GIDC, Rajkot", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "nexa", "name": "Nexa Lamps", "email": "contact@nexalamps.in", "phone": "+91 9988721003", "gst_number": "09AACCN8831Q1ZS", "address": "Sector 63, Noida", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "gulmohar", "name": "Gulmohar Textiles", "email": "trade@gulmohartextiles.in", "phone": "+91 9988721004", "gst_number": "27AACCG2381J1Z4", "address": "Bhiwandi, Mumbai", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "brass", "name": "Jaipur Brass Craft", "email": "hello@jaipurbrass.in", "phone": "+91 9988721005", "gst_number": "08AACFJ0902Q1ZM", "address": "Sanganer, Jaipur", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "cane", "name": "Cane & Co", "email": "ops@caneandco.in", "phone": "+91 9988721006", "gst_number": "32AACCC9182D1ZT", "address": "Alappuzha, Kerala", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "saffron", "name": "Saffron Ceramics", "email": "sales@saffronceramics.in", "phone": "+91 9988721007", "gst_number": "07AAGCS1182F1Z5", "address": "Sikandrabad, Uttar Pradesh", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "deccan", "name": "Deccan Utility House", "email": "support@deccanutility.in", "phone": "+91 9988721008", "gst_number": "36AACCD7211N1Z9", "address": "Jeedimetla, Hyderabad", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
        ],
    )
    customers = _create_lookup_records(
        db,
        Customer,
        tenant.id,
        [
            {"key": "aarohi", "name": "Aarohi Interiors", "email": "ops@aarohiinteriors.in", "phone": "+91 9988731001", "gst_number": "27AAHCA0931A1ZV", "billing_address": "Lower Parel, Mumbai", "shipping_address": "Andheri East, Mumbai", "status": RecordStatusEnum.ACTIVE},
            {"key": "blue", "name": "Blue Banyan Offices", "email": "buying@bluebanyan.co", "phone": "+91 9988731002", "gst_number": "36AACCB1902N1Z5", "billing_address": "Gachibowli, Hyderabad", "shipping_address": "Madhapur, Hyderabad", "status": RecordStatusEnum.ACTIVE},
            {"key": "urban", "name": "Urban Nest Retail", "email": "stores@urbannest.in", "phone": "+91 9988731003", "gst_number": "24AACCU1181E1Z6", "billing_address": "Satellite, Ahmedabad", "shipping_address": "Bodakdev, Ahmedabad", "status": RecordStatusEnum.ACTIVE},
            {"key": "story", "name": "Storyline Hospitality", "email": "procurement@storyline.in", "phone": "+91 9988731004", "gst_number": "07AACCS1181L1ZM", "billing_address": "Aerocity, New Delhi", "shipping_address": "Aerocity, New Delhi", "status": RecordStatusEnum.ACTIVE},
            {"key": "loom", "name": "Loom & Leaf Homes", "email": "trade@loomandleaf.in", "phone": "+91 9988731005", "gst_number": "29AACCL5521E1ZA", "billing_address": "Whitefield, Bengaluru", "shipping_address": "Sarjapur, Bengaluru", "status": RecordStatusEnum.ACTIVE},
            {"key": "craft", "name": "Craftway Studios", "email": "orders@craftway.in", "phone": "+91 9988731006", "gst_number": "33AACCC5511P1Z1", "billing_address": "T Nagar, Chennai", "shipping_address": "Velachery, Chennai", "status": RecordStatusEnum.ACTIVE},
            {"key": "olive", "name": "Olive Workspaces", "email": "ops@oliveworkspaces.in", "phone": "+91 9988731007", "gst_number": "19AABCO7311H1ZX", "billing_address": "Salt Lake, Kolkata", "shipping_address": "New Town, Kolkata", "status": RecordStatusEnum.ACTIVE},
            {"key": "saffron", "name": "Saffron Habitat", "email": "sourcing@saffronhabitat.in", "phone": "+91 9988731008", "gst_number": "08AACCS3090N1Z4", "billing_address": "Malviya Nagar, Jaipur", "shipping_address": "Vaishali Nagar, Jaipur", "status": RecordStatusEnum.ACTIVE},
        ],
    )
    products = _create_products(
        db,
        tenant.id,
        categories,
        brands,
        vendors,
        [
            {"key": "table", "name": "Sheesham Study Table", "sku": "NST-OFC-101", "barcode": "8906007201001", "category_key": "furniture", "brand_key": "northstar", "vendor_key": "kaveri", "description": "Solid sheesham wood desk for office and study setups.", "unit": "pcs", "cost_price": Decimal("13240.00"), "selling_price": Decimal("18999.00"), "reorder_level": 16, "status": RecordStatusEnum.ACTIVE},
            {"key": "chair", "name": "Ergonomic Mesh Kursi", "sku": "NST-OFC-102", "barcode": "8906007201002", "category_key": "furniture", "brand_key": "sutradhar", "vendor_key": "prakash", "description": "Breathable ergonomic chair with lumbar support.", "unit": "pcs", "cost_price": Decimal("4980.00"), "selling_price": Decimal("7499.00"), "reorder_level": 24, "status": RecordStatusEnum.ACTIVE},
            {"key": "lamp", "name": "Brass Finish Desk Lamp", "sku": "NST-LGT-103", "barcode": "8906007201003", "category_key": "lighting", "brand_key": "aarambh", "vendor_key": "nexa", "description": "Warm brass desk lamp with focused task lighting.", "unit": "pcs", "cost_price": Decimal("1540.00"), "selling_price": Decimal("2899.00"), "reorder_level": 20, "status": RecordStatusEnum.ACTIVE},
            {"key": "basket", "name": "Jute Storage Basket Set", "sku": "NST-STO-104", "barcode": "8906007201004", "category_key": "storage", "brand_key": "aarambh", "vendor_key": "cane", "description": "Set of nested jute baskets for display and storage.", "unit": "set", "cost_price": Decimal("1120.00"), "selling_price": Decimal("2199.00"), "reorder_level": 36, "status": RecordStatusEnum.ACTIVE},
            {"key": "copper", "name": "Copper Bottle Gift Set", "sku": "NST-GFT-105", "barcode": "8906007201005", "category_key": "serveware", "brand_key": "sutradhar", "vendor_key": "brass", "description": "Hammered copper bottle and tumbler gift set.", "unit": "set", "cost_price": Decimal("920.00"), "selling_price": Decimal("1599.00"), "reorder_level": 18, "status": RecordStatusEnum.ACTIVE},
            {"key": "planter", "name": "Terrazzo Table Planter", "sku": "NST-DCR-106", "barcode": "8906007201006", "category_key": "decor", "brand_key": "veda", "vendor_key": "saffron", "description": "Minimal terrazzo planter for desk and shelf styling.", "unit": "pcs", "cost_price": Decimal("640.00"), "selling_price": Decimal("1199.00"), "reorder_level": 28, "status": RecordStatusEnum.ACTIVE},
            {"key": "runner", "name": "Block Print Table Runner", "sku": "NST-TXT-107", "barcode": "8906007201007", "category_key": "textiles", "brand_key": "nila", "vendor_key": "gulmohar", "description": "Hand block printed cotton table runner.", "unit": "pcs", "cost_price": Decimal("480.00"), "selling_price": Decimal("899.00"), "reorder_level": 30, "status": RecordStatusEnum.ACTIVE},
            {"key": "rack", "name": "Powder-Coated File Rack", "sku": "NST-STO-108", "barcode": "8906007201008", "category_key": "storage", "brand_key": "northstar", "vendor_key": "prakash", "description": "Slim file rack for workstations and reception counters.", "unit": "pcs", "cost_price": Decimal("970.00"), "selling_price": Decimal("1699.00"), "reorder_level": 22, "status": RecordStatusEnum.ACTIVE},
            {"key": "stool", "name": "Acacia Accent Stool", "sku": "NST-DCR-109", "barcode": "8906007201009", "category_key": "decor", "brand_key": "sutradhar", "vendor_key": "kaveri", "description": "Compact accent stool with natural wood grain.", "unit": "pcs", "cost_price": Decimal("1850.00"), "selling_price": Decimal("3499.00"), "reorder_level": 12, "status": RecordStatusEnum.ACTIVE},
            {"key": "tray", "name": "Marble Serve Tray", "sku": "NST-GFT-110", "barcode": "8906007201010", "category_key": "serveware", "brand_key": "veda", "vendor_key": "saffron", "description": "Rounded marble tray for hospitality and gifting collections.", "unit": "pcs", "cost_price": Decimal("1280.00"), "selling_price": Decimal("2299.00"), "reorder_level": 16, "status": RecordStatusEnum.ACTIVE},
            {"key": "sconce", "name": "Rattan Wall Sconce", "sku": "NST-LGT-111", "barcode": "8906007201011", "category_key": "lighting", "brand_key": "aarambh", "vendor_key": "cane", "description": "Soft woven wall light for lounge and studio corners.", "unit": "pcs", "cost_price": Decimal("1140.00"), "selling_price": Decimal("2099.00"), "reorder_level": 18, "status": RecordStatusEnum.ACTIVE},
            {"key": "bin", "name": "Bamboo Utility Bin", "sku": "NST-STO-112", "barcode": "8906007201012", "category_key": "storage", "brand_key": "nila", "vendor_key": "deccan", "description": "Lightweight utility bin with bamboo body and liner.", "unit": "pcs", "cost_price": Decimal("560.00"), "selling_price": Decimal("999.00"), "reorder_level": 26, "status": RecordStatusEnum.ACTIVE},
            {"key": "bench", "name": "Cane Entryway Bench", "sku": "NST-FUR-113", "barcode": "8906007201013", "category_key": "furniture", "brand_key": "veda", "vendor_key": "cane", "description": "Woven cane bench for lounges and reception zones.", "unit": "pcs", "cost_price": Decimal("4480.00"), "selling_price": Decimal("7199.00"), "reorder_level": 10, "status": RecordStatusEnum.ACTIVE},
            {"key": "cushion", "name": "Indigo Cushion Cover Set", "sku": "NST-TXT-114", "barcode": "8906007201014", "category_key": "textiles", "brand_key": "nila", "vendor_key": "gulmohar", "description": "Set of two textured cushion covers in indigo weave.", "unit": "set", "cost_price": Decimal("690.00"), "selling_price": Decimal("1299.00"), "reorder_level": 24, "status": RecordStatusEnum.ACTIVE},
        ],
    )

    stock_payloads = []
    warehouse_cycle = ["blr", "del", "pun", "hyd"]
    for index, product_key in enumerate(products.keys()):
        primary_quantity = 18 + (index * 5)
        reorder_level = products[product_key].reorder_level or 10
        reserved_quantity = 2 if index % 3 == 0 else 0
        stock_payloads.append(
            {
                "warehouse_key": warehouse_cycle[index % len(warehouse_cycle)],
                "product_key": product_key,
                "quantity": primary_quantity,
                "reserved_quantity": reserved_quantity,
                "reorder_level": reorder_level,
            }
        )
        stock_payloads.append(
            {
                "warehouse_key": warehouse_cycle[(index + 1) % len(warehouse_cycle)],
                "product_key": product_key,
                "quantity": max(6, primary_quantity // 2),
                "reserved_quantity": 0,
                "reorder_level": reorder_level,
            }
        )
    stock_payloads.extend(
        [
            {"warehouse_key": "blr", "product_key": "copper", "quantity": 10, "reserved_quantity": 0, "reorder_level": 18},
            {"warehouse_key": "hyd", "product_key": "bench", "quantity": 7, "reserved_quantity": 1, "reorder_level": 10},
            {"warehouse_key": "del", "product_key": "lamp", "quantity": 14, "reserved_quantity": 2, "reorder_level": 20},
        ]
    )
    _add_stock_rows(db, tenant.id, warehouses, products, stock_payloads)

    purchase_orders = _create_purchase_orders(
        db,
        tenant.id,
        vendors,
        warehouses,
        products,
        [
            {
                "key": "po204",
                "vendor_key": "kaveri",
                "po_number": "PO-204",
                "order_date": date(2026, 5, 18),
                "expected_delivery_date": date(2026, 5, 25),
                "status": PurchaseOrderStatusEnum.ISSUED,
                "subtotal": Decimal("105920.00"),
                "tax_amount": Decimal("12710.40"),
                "total_amount": Decimal("118630.40"),
                "notes": "Check finish consistency before warehouse acceptance.",
                "created_by": users["purchase"].id,
                "items": [{"product_key": "table", "warehouse_key": "blr", "quantity_ordered": 8, "quantity_received": 0, "unit_price": Decimal("13240.00"), "tax_rate": Decimal("12.00"), "total_price": Decimal("118630.40")}],
            },
            {
                "key": "po203",
                "vendor_key": "nexa",
                "po_number": "PO-203",
                "order_date": date(2026, 5, 16),
                "expected_delivery_date": date(2026, 5, 24),
                "status": PurchaseOrderStatusEnum.PARTIALLY_RECEIVED,
                "subtotal": Decimal("36960.00"),
                "tax_amount": Decimal("4435.20"),
                "total_amount": Decimal("41395.20"),
                "notes": "Balance shipment due by weekend.",
                "created_by": users["purchase"].id,
                "items": [{"product_key": "lamp", "warehouse_key": "blr", "quantity_ordered": 24, "quantity_received": 10, "unit_price": Decimal("1540.00"), "tax_rate": Decimal("12.00"), "total_price": Decimal("41395.20")}],
            },
            {
                "key": "po202",
                "vendor_key": "gulmohar",
                "po_number": "PO-202",
                "order_date": date(2026, 5, 14),
                "expected_delivery_date": date(2026, 5, 20),
                "status": PurchaseOrderStatusEnum.RECEIVED,
                "subtotal": Decimal("16560.00"),
                "tax_amount": Decimal("1987.20"),
                "total_amount": Decimal("18547.20"),
                "notes": "Textile line replenishment received in full.",
                "created_by": users["purchase"].id,
                "items": [{"product_key": "runner", "warehouse_key": "hyd", "quantity_ordered": 30, "quantity_received": 30, "unit_price": Decimal("480.00"), "tax_rate": Decimal("12.00"), "total_price": Decimal("16128.00")}],
            },
            {
                "key": "po201",
                "vendor_key": "brass",
                "po_number": "PO-201",
                "order_date": date(2026, 5, 12),
                "expected_delivery_date": date(2026, 5, 22),
                "status": PurchaseOrderStatusEnum.DRAFT,
                "subtotal": Decimal("15360.00"),
                "tax_amount": Decimal("1843.20"),
                "total_amount": Decimal("17203.20"),
                "notes": "Awaiting vendor cost approval.",
                "created_by": users["purchase"].id,
                "items": [{"product_key": "tray", "warehouse_key": "del", "quantity_ordered": 12, "quantity_received": 0, "unit_price": Decimal("1280.00"), "tax_rate": Decimal("12.00"), "total_price": Decimal("17203.20")}],
            },
            {
                "key": "po200",
                "vendor_key": "deccan",
                "po_number": "PO-200",
                "order_date": date(2026, 5, 10),
                "expected_delivery_date": date(2026, 5, 18),
                "status": PurchaseOrderStatusEnum.CANCELLED,
                "subtotal": Decimal("11200.00"),
                "tax_amount": Decimal("1344.00"),
                "total_amount": Decimal("12544.00"),
                "notes": "Cancelled after duplicate replenishment request.",
                "created_by": users["purchase"].id,
                "items": [{"product_key": "bin", "warehouse_key": "pun", "quantity_ordered": 20, "quantity_received": 0, "unit_price": Decimal("560.00"), "tax_rate": Decimal("12.00"), "total_price": Decimal("12544.00")}],
            },
        ],
    )
    sales_orders = _create_sales_orders(
        db,
        tenant.id,
        customers,
        warehouses,
        products,
        [
            {
                "key": "so210",
                "customer_key": "aarohi",
                "so_number": "SO-210",
                "order_date": date(2026, 5, 18),
                "status": SalesOrderStatusEnum.CONFIRMED,
                "subtotal": Decimal("35794.00"),
                "tax_amount": Decimal("4295.28"),
                "discount_amount": Decimal("1000.00"),
                "total_amount": Decimal("39089.28"),
                "notes": "Dispatch only after final packing photos.",
                "created_by": users["sales"].id,
                "items": [
                    {"product_key": "chair", "warehouse_key": "blr", "quantity": 4, "unit_price": Decimal("7499.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("1000.00"), "total_price": Decimal("32595.52")},
                    {"product_key": "lamp", "warehouse_key": "blr", "quantity": 2, "unit_price": Decimal("2899.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("6493.76")},
                ],
            },
            {
                "key": "so209",
                "customer_key": "blue",
                "so_number": "SO-209",
                "order_date": date(2026, 5, 17),
                "status": SalesOrderStatusEnum.SHIPPED,
                "subtotal": Decimal("18999.00"),
                "tax_amount": Decimal("2279.88"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("21278.88"),
                "notes": "Corporate order with partial shipment approved.",
                "created_by": users["sales"].id,
                "items": [{"product_key": "table", "warehouse_key": "blr", "quantity": 1, "unit_price": Decimal("18999.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("21278.88")}],
            },
            {
                "key": "so208",
                "customer_key": "urban",
                "so_number": "SO-208",
                "order_date": date(2026, 5, 16),
                "status": SalesOrderStatusEnum.DELIVERED,
                "subtotal": Decimal("9196.00"),
                "tax_amount": Decimal("1103.52"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("10299.52"),
                "notes": "Decor refresh pack delivered.",
                "created_by": users["sales"].id,
                "items": [{"product_key": "planter", "warehouse_key": "hyd", "quantity": 4, "unit_price": Decimal("1199.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("5371.52")}, {"product_key": "tray", "warehouse_key": "del", "quantity": 2, "unit_price": Decimal("2299.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("5148.00")}],
            },
            {
                "key": "so207",
                "customer_key": "story",
                "so_number": "SO-207",
                "order_date": date(2026, 5, 15),
                "status": SalesOrderStatusEnum.DRAFT,
                "subtotal": Decimal("14398.00"),
                "tax_amount": Decimal("1727.76"),
                "discount_amount": Decimal("500.00"),
                "total_amount": Decimal("15625.76"),
                "notes": "Awaiting customer approval.",
                "created_by": users["sales"].id,
                "items": [{"product_key": "bench", "warehouse_key": "hyd", "quantity": 2, "unit_price": Decimal("7199.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("500.00"), "total_price": Decimal("15625.76")}],
            },
            {
                "key": "so206",
                "customer_key": "loom",
                "so_number": "SO-206",
                "order_date": date(2026, 5, 14),
                "status": SalesOrderStatusEnum.PACKED,
                "subtotal": Decimal("7794.00"),
                "tax_amount": Decimal("935.28"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("8729.28"),
                "notes": "Ready for courier handoff.",
                "created_by": users["sales"].id,
                "items": [{"product_key": "cushion", "warehouse_key": "blr", "quantity": 6, "unit_price": Decimal("1299.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("8729.28")}],
            },
            {
                "key": "so205",
                "customer_key": "craft",
                "so_number": "SO-205",
                "order_date": date(2026, 5, 13),
                "status": SalesOrderStatusEnum.CANCELLED,
                "subtotal": Decimal("4198.00"),
                "tax_amount": Decimal("503.76"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("4701.76"),
                "notes": "Cancelled after budget revision.",
                "created_by": users["sales"].id,
                "items": [{"product_key": "sconce", "warehouse_key": "del", "quantity": 2, "unit_price": Decimal("2099.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("4701.76")}],
            },
            {
                "key": "so204",
                "customer_key": "olive",
                "so_number": "SO-204",
                "order_date": date(2026, 5, 12),
                "status": SalesOrderStatusEnum.CONFIRMED,
                "subtotal": Decimal("6597.00"),
                "tax_amount": Decimal("791.64"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("7388.64"),
                "notes": "Reserved for workspace styling launch.",
                "created_by": users["sales"].id,
                "items": [{"product_key": "basket", "warehouse_key": "pun", "quantity": 3, "unit_price": Decimal("2199.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("7388.64")}],
            },
        ],
    )

    transfers = _create_transfers(
        db,
        tenant.id,
        users["inventory"].id,
        warehouses,
        products,
        [
            {"key": "tr1", "source_warehouse_key": "blr", "destination_warehouse_key": "del", "status": StockTransferStatusEnum.IN_TRANSIT, "notes": "Delhi project replenishment before client installation.", "items": [{"product_key": "lamp", "quantity": 6}, {"product_key": "planter", "quantity": 4}]},
            {"key": "tr2", "source_warehouse_key": "hyd", "destination_warehouse_key": "pun", "status": StockTransferStatusEnum.COMPLETED, "notes": "Redistribution after textile campaign close.", "items": [{"product_key": "runner", "quantity": 10}]},
            {"key": "tr3", "source_warehouse_key": "blr", "destination_warehouse_key": "hyd", "status": StockTransferStatusEnum.DRAFT, "notes": "Reserved for South hub seasonal launch.", "items": [{"product_key": "cushion", "quantity": 8}]},
        ],
    )
    _seed_extended_business_tables(
        db,
        tenant.id,
        users["sales"].id,
        users["purchase"].id,
        warehouses,
        products,
        sales_orders,
        purchase_orders,
    )

    for index, (product_key, product) in enumerate(products.items()):
        db.add(
            InventoryTransaction(
                tenant_id=tenant.id,
                product_id=product.id,
                warehouse_id=warehouses["blr"].id if index % 2 == 0 else warehouses["hyd"].id,
                transaction_type=InventoryTransactionTypeEnum.STOCK_IN,
                quantity=12 + index,
                reference_type="OPENING_BALANCE",
                reference_id=None,
                note=f"Seeded opening stock for {product.name}",
                created_by=users["inventory"].id,
            )
        )
        if index < 4:
            db.add(
                InventoryTransaction(
                    tenant_id=tenant.id,
                    product_id=product.id,
                    warehouse_id=warehouses["blr"].id,
                    transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_RESERVE,
                    quantity=-2,
                    reference_type="sales_order",
                    reference_id=sales_orders["so210"].id,
                    note="Reserved for active sales workflow",
                    created_by=users["sales"].id,
                )
            )
    db.add_all(
        [
            InventoryTransaction(
                tenant_id=tenant.id,
                product_id=products["lamp"].id,
                warehouse_id=warehouses["blr"].id,
                destination_warehouse_id=warehouses["del"].id,
                transaction_type=InventoryTransactionTypeEnum.TRANSFER_OUT,
                quantity=-6,
                reference_type="stock_transfer",
                reference_id=transfers["tr1"].id,
                note="Transfer to North Hub",
                created_by=users["inventory"].id,
            ),
            InventoryTransaction(
                tenant_id=tenant.id,
                product_id=products["runner"].id,
                warehouse_id=warehouses["hyd"].id,
                destination_warehouse_id=warehouses["pun"].id,
                transaction_type=InventoryTransactionTypeEnum.TRANSFER_OUT,
                quantity=-10,
                reference_type="stock_transfer",
                reference_id=transfers["tr2"].id,
                note="Completed transfer to Pune Overflow",
                created_by=users["inventory"].id,
            ),
        ]
    )
    db.add_all(
        [
            Notification(tenant_id=tenant.id, user_id=users["admin"].id, title="Low stock watchlist updated", message="Copper Bottle Gift Set, Acacia Accent Stool, and Counter Display SKUs need replenishment.", type=NotificationTypeEnum.LOW_STOCK, is_read=False),
            Notification(tenant_id=tenant.id, user_id=users["purchase"].id, title="Vendor receipts still pending", message="PO-204 and PO-201 need action before the next planning cycle.", type=NotificationTypeEnum.PURCHASE_RECEIVE, is_read=False),
            Notification(tenant_id=tenant.id, user_id=users["sales"].id, title="Orders ready for action", message="SO-210 is confirmed and SO-206 is packed for dispatch.", type=NotificationTypeEnum.ORDER_STATUS, is_read=False),
            Notification(tenant_id=tenant.id, user_id=users["inventory"].id, title="Transfer already in motion", message="TR1 is on the way to Delhi and TR3 is staged in draft.", type=NotificationTypeEnum.STOCK_TRANSFER, is_read=False),
            Notification(tenant_id=tenant.id, user_id=users["viewer"].id, title="Workspace analytics refreshed", message="New dashboard metrics are available across products, orders, and stock.", type=NotificationTypeEnum.SYSTEM, is_read=False),
        ]
    )
    db.add_all(
        [
            AuditLog(tenant_id=tenant.id, user_id=users["inventory"].id, action="inventory.transfer.created", entity_type="stock_transfer", entity_id=transfers["tr1"].id, new_value_json={"status": transfers["tr1"].status.value}),
            AuditLog(tenant_id=tenant.id, user_id=users["sales"].id, action="sales_order.confirmed", entity_type="sales_order", entity_id=sales_orders["so210"].id, new_value_json={"status": sales_orders["so210"].status.value}),
            AuditLog(tenant_id=tenant.id, user_id=users["purchase"].id, action="purchase_order.issued", entity_type="purchase_order", entity_id=purchase_orders["po204"].id, new_value_json={"status": purchase_orders["po204"].status.value}),
            AuditLog(tenant_id=tenant.id, user_id=users["sales"].id, action="sales_order.shipped", entity_type="sales_order", entity_id=sales_orders["so209"].id, new_value_json={"status": sales_orders["so209"].status.value}),
            AuditLog(tenant_id=tenant.id, user_id=users["inventory"].id, action="inventory.low_stock.flagged", entity_type="product", entity_id=products["copper"].id, new_value_json={"reorder_level": products["copper"].reorder_level}),
        ]
    )
    db.commit()


def _top_up_large_workspace(db: Session, tenant: Tenant) -> None:
    existing_products = db.scalars(select(Product).where(Product.tenant_id == tenant.id)).all()
    needs_catalog_topup = len(existing_products) < 12
    user_rows = db.scalars(select(User).where(User.tenant_id == tenant.id)).all()
    users_by_role = {user.role: user for user in user_rows}
    if not all(role in users_by_role for role in [RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER, RoleEnum.SALES_STAFF, RoleEnum.PURCHASE_STAFF]):
        return

    if not needs_catalog_topup:
        warehouses = {
            "blr": db.scalar(select(Warehouse).where(Warehouse.tenant_id == tenant.id, Warehouse.code == "BLR-CEN")),
            "del": db.scalar(select(Warehouse).where(Warehouse.tenant_id == tenant.id, Warehouse.code == "DEL-NTH")),
            "pun": db.scalar(select(Warehouse).where(Warehouse.tenant_id == tenant.id, Warehouse.code == "PUN-OVR")),
            "hyd": db.scalar(select(Warehouse).where(Warehouse.tenant_id == tenant.id, Warehouse.code == "HYD-SOU")),
        }
        products = {product.sku: product for product in existing_products}
        normalized_products = {
            "runner": products.get("NST-TXT-107"),
            "lamp": products.get("NST-LGT-103"),
            "table": products.get("NST-OFC-101"),
            "vase": products.get("CLV-101"),
        }
        normalized_products.update({product.sku: product for product in existing_products})
        _seed_extended_business_tables(
            db,
            tenant.id,
            users_by_role[RoleEnum.SALES_STAFF].id,
            users_by_role[RoleEnum.PURCHASE_STAFF].id,
            warehouses,
            normalized_products,
            {},
            {},
        )
        db.commit()
        return

    categories = _ensure_lookup_records(
        db,
        Category,
        tenant.id,
        [
            {"key": "decor", "name": "Decor", "description": "Accent pieces and planters", "status": RecordStatusEnum.ACTIVE},
            {"key": "serveware", "name": "Serveware", "description": "Gifting and hospitality sets", "status": RecordStatusEnum.ACTIVE},
            {"key": "textiles", "name": "Soft Furnishings", "description": "Cushions, throws, and runners", "status": RecordStatusEnum.ACTIVE},
        ],
        "name",
    )
    categories.update(
        {
            "furniture": db.scalar(select(Category).where(Category.tenant_id == tenant.id, Category.name == "Office Furniture")),
            "lighting": db.scalar(select(Category).where(Category.tenant_id == tenant.id, Category.name == "Lighting")),
            "storage": db.scalar(select(Category).where(Category.tenant_id == tenant.id, Category.name == "Storage")),
        }
    )
    brands = _ensure_lookup_records(
        db,
        Brand,
        tenant.id,
        [
            {"key": "veda", "name": "Veda Home", "description": "Contemporary home accents", "status": RecordStatusEnum.ACTIVE},
            {"key": "nila", "name": "Nila Living", "description": "Soft furnishings and hosting accessories", "status": RecordStatusEnum.ACTIVE},
        ],
        "name",
    )
    brands.update(
        {
            "northstar": db.scalar(select(Brand).where(Brand.tenant_id == tenant.id, Brand.name == "Northstar")),
            "sutradhar": db.scalar(select(Brand).where(Brand.tenant_id == tenant.id, Brand.name == "Sutradhar")),
            "aarambh": db.scalar(select(Brand).where(Brand.tenant_id == tenant.id, Brand.name == "Aarambh")),
        }
    )
    warehouses = _ensure_lookup_records(
        db,
        Warehouse,
        tenant.id,
        [
            {
                "key": "blr",
                "name": "Central Warehouse",
                "code": "BLR-CEN",
                "address": "Mahadevapura Industrial Area, Bengaluru",
                "city": "Bengaluru",
                "state": "Karnataka",
                "country": "India",
                "manager_name": "Akash Sharma",
                "phone": "+91 9845012300",
                "is_default": True,
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "del",
                "name": "North Hub",
                "code": "DEL-NTH",
                "address": "Okhla Phase II, New Delhi",
                "city": "New Delhi",
                "state": "Delhi",
                "country": "India",
                "manager_name": "Pooja Nair",
                "phone": "+91 9810012300",
                "is_default": False,
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "pun",
                "name": "Pune Overflow",
                "code": "PUN-OVR",
                "address": "Bhosari MIDC, Pune",
                "city": "Pune",
                "state": "Maharashtra",
                "country": "India",
                "manager_name": "Nikhil Rao",
                "phone": "+91 9822012300",
                "is_default": False,
                "status": RecordStatusEnum.ACTIVE,
            },
            {
                "key": "hyd",
                "name": "South Distribution Hub",
                "code": "HYD-SOU",
                "address": "Kompally Logistics Park, Hyderabad",
                "city": "Hyderabad",
                "state": "Telangana",
                "country": "India",
                "manager_name": "Rohit Verma",
                "phone": "+91 9849012300",
                "is_default": False,
                "status": RecordStatusEnum.ACTIVE,
            },
        ],
        "code",
    )
    warehouses.update(
        {
            "blr": db.scalar(select(Warehouse).where(Warehouse.tenant_id == tenant.id, Warehouse.code == "BLR-CEN")),
            "del": db.scalar(select(Warehouse).where(Warehouse.tenant_id == tenant.id, Warehouse.code == "DEL-NTH")),
            "pun": db.scalar(select(Warehouse).where(Warehouse.tenant_id == tenant.id, Warehouse.code == "PUN-OVR")),
        }
    )
    vendors = _ensure_lookup_records(
        db,
        Vendor,
        tenant.id,
        [
            {"key": "gulmohar", "name": "Gulmohar Textiles", "email": "trade@gulmohartextiles.in", "phone": "+91 9988721004", "gst_number": "27AACCG2381J1Z4", "address": "Bhiwandi, Mumbai", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "brass", "name": "Jaipur Brass Craft", "email": "hello@jaipurbrass.in", "phone": "+91 9988721005", "gst_number": "08AACFJ0902Q1ZM", "address": "Sanganer, Jaipur", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "cane", "name": "Cane & Co", "email": "ops@caneandco.in", "phone": "+91 9988721006", "gst_number": "32AACCC9182D1ZT", "address": "Alappuzha, Kerala", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "saffron", "name": "Saffron Ceramics", "email": "sales@saffronceramics.in", "phone": "+91 9988721007", "gst_number": "07AAGCS1182F1Z5", "address": "Sikandrabad, Uttar Pradesh", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "deccan", "name": "Deccan Utility House", "email": "support@deccanutility.in", "phone": "+91 9988721008", "gst_number": "36AACCD7211N1Z9", "address": "Jeedimetla, Hyderabad", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
        ],
        "name",
    )
    vendors.update(
        {
            "kaveri": db.scalar(select(Vendor).where(Vendor.tenant_id == tenant.id, Vendor.name == "Kaveri Woods")),
            "prakash": db.scalar(select(Vendor).where(Vendor.tenant_id == tenant.id, Vendor.name == "Prakash Metal Works")),
            "nexa": db.scalar(select(Vendor).where(Vendor.tenant_id == tenant.id, Vendor.name == "Nexa Lamps")),
        }
    )
    customers = _ensure_lookup_records(
        db,
        Customer,
        tenant.id,
        [
            {"key": "story", "name": "Storyline Hospitality", "email": "procurement@storyline.in", "phone": "+91 9988731004", "gst_number": "07AACCS1181L1ZM", "billing_address": "Aerocity, New Delhi", "shipping_address": "Aerocity, New Delhi", "status": RecordStatusEnum.ACTIVE},
            {"key": "loom", "name": "Loom & Leaf Homes", "email": "trade@loomandleaf.in", "phone": "+91 9988731005", "gst_number": "29AACCL5521E1ZA", "billing_address": "Whitefield, Bengaluru", "shipping_address": "Sarjapur, Bengaluru", "status": RecordStatusEnum.ACTIVE},
            {"key": "craft", "name": "Craftway Studios", "email": "orders@craftway.in", "phone": "+91 9988731006", "gst_number": "33AACCC5511P1Z1", "billing_address": "T Nagar, Chennai", "shipping_address": "Velachery, Chennai", "status": RecordStatusEnum.ACTIVE},
            {"key": "olive", "name": "Olive Workspaces", "email": "ops@oliveworkspaces.in", "phone": "+91 9988731007", "gst_number": "19AABCO7311H1ZX", "billing_address": "Salt Lake, Kolkata", "shipping_address": "New Town, Kolkata", "status": RecordStatusEnum.ACTIVE},
            {"key": "saffron", "name": "Saffron Habitat", "email": "sourcing@saffronhabitat.in", "phone": "+91 9988731008", "gst_number": "08AACCS3090N1Z4", "billing_address": "Malviya Nagar, Jaipur", "shipping_address": "Vaishali Nagar, Jaipur", "status": RecordStatusEnum.ACTIVE},
        ],
        "name",
    )
    customers.update(
        {
            "aarohi": db.scalar(select(Customer).where(Customer.tenant_id == tenant.id, Customer.name == "Aarohi Interiors")),
            "blue": db.scalar(select(Customer).where(Customer.tenant_id == tenant.id, Customer.name == "Blue Banyan Offices")),
            "urban": db.scalar(select(Customer).where(Customer.tenant_id == tenant.id, Customer.name == "Urban Nest Retail")),
        }
    )
    products = _ensure_products(
        db,
        tenant.id,
        categories,
        brands,
        vendors,
        [
            {"key": "planter", "name": "Terrazzo Table Planter", "sku": "NST-DCR-106", "barcode": "8906007201006", "category_key": "decor", "brand_key": "veda", "vendor_key": "saffron", "description": "Minimal terrazzo planter for desk and shelf styling.", "unit": "pcs", "cost_price": Decimal("640.00"), "selling_price": Decimal("1199.00"), "reorder_level": 28, "status": RecordStatusEnum.ACTIVE},
            {"key": "runner", "name": "Block Print Table Runner", "sku": "NST-TXT-107", "barcode": "8906007201007", "category_key": "textiles", "brand_key": "nila", "vendor_key": "gulmohar", "description": "Hand block printed cotton table runner.", "unit": "pcs", "cost_price": Decimal("480.00"), "selling_price": Decimal("899.00"), "reorder_level": 30, "status": RecordStatusEnum.ACTIVE},
            {"key": "rack", "name": "Powder-Coated File Rack", "sku": "NST-STO-108", "barcode": "8906007201008", "category_key": "storage", "brand_key": "veda", "vendor_key": "deccan", "description": "Slim file rack for workstations and reception counters.", "unit": "pcs", "cost_price": Decimal("970.00"), "selling_price": Decimal("1699.00"), "reorder_level": 22, "status": RecordStatusEnum.ACTIVE},
            {"key": "stool", "name": "Acacia Accent Stool", "sku": "NST-DCR-109", "barcode": "8906007201009", "category_key": "decor", "brand_key": "sutradhar", "vendor_key": "cane", "description": "Compact accent stool with natural wood grain.", "unit": "pcs", "cost_price": Decimal("1850.00"), "selling_price": Decimal("3499.00"), "reorder_level": 12, "status": RecordStatusEnum.ACTIVE},
            {"key": "tray", "name": "Marble Serve Tray", "sku": "NST-GFT-110", "barcode": "8906007201010", "category_key": "serveware", "brand_key": "veda", "vendor_key": "brass", "description": "Rounded marble tray for hospitality and gifting collections.", "unit": "pcs", "cost_price": Decimal("1280.00"), "selling_price": Decimal("2299.00"), "reorder_level": 16, "status": RecordStatusEnum.ACTIVE},
            {"key": "sconce", "name": "Rattan Wall Sconce", "sku": "NST-LGT-111", "barcode": "8906007201011", "category_key": "lighting", "brand_key": "aarambh", "vendor_key": "cane", "description": "Soft woven wall light for lounge and studio corners.", "unit": "pcs", "cost_price": Decimal("1140.00"), "selling_price": Decimal("2099.00"), "reorder_level": 18, "status": RecordStatusEnum.ACTIVE},
            {"key": "bin", "name": "Bamboo Utility Bin", "sku": "NST-STO-112", "barcode": "8906007201012", "category_key": "storage", "brand_key": "nila", "vendor_key": "deccan", "description": "Lightweight utility bin with bamboo body and liner.", "unit": "pcs", "cost_price": Decimal("560.00"), "selling_price": Decimal("999.00"), "reorder_level": 26, "status": RecordStatusEnum.ACTIVE},
            {"key": "bench", "name": "Cane Entryway Bench", "sku": "NST-FUR-113", "barcode": "8906007201013", "category_key": "furniture", "brand_key": "veda", "vendor_key": "cane", "description": "Woven cane bench for lounges and reception zones.", "unit": "pcs", "cost_price": Decimal("4480.00"), "selling_price": Decimal("7199.00"), "reorder_level": 10, "status": RecordStatusEnum.ACTIVE},
            {"key": "cushion", "name": "Indigo Cushion Cover Set", "sku": "NST-TXT-114", "barcode": "8906007201014", "category_key": "textiles", "brand_key": "nila", "vendor_key": "gulmohar", "description": "Set of two textured cushion covers in indigo weave.", "unit": "set", "cost_price": Decimal("690.00"), "selling_price": Decimal("1299.00"), "reorder_level": 24, "status": RecordStatusEnum.ACTIVE},
        ],
    )
    stock_payloads = []
    for index, product_key in enumerate(products.keys()):
        stock_payloads.append({"warehouse_key": ["blr", "del", "pun", "hyd"][index % 4], "product_key": product_key, "quantity": 12 + (index * 3), "reserved_quantity": 1 if index % 2 == 0 else 0, "reorder_level": products[product_key].reorder_level})
    _add_stock_rows(db, tenant.id, warehouses, products, stock_payloads)
    _create_purchase_orders(
        db,
        tenant.id,
        vendors,
        warehouses,
        products,
        [
            {
                "key": "po205",
                "vendor_key": "gulmohar",
                "po_number": "PO-205",
                "order_date": date(2026, 5, 19),
                "expected_delivery_date": date(2026, 5, 25),
                "status": PurchaseOrderStatusEnum.RECEIVED,
                "subtotal": Decimal("14400.00"),
                "tax_amount": Decimal("1728.00"),
                "total_amount": Decimal("16128.00"),
                "notes": "Textile line replenishment received in full.",
                "created_by": users_by_role[RoleEnum.PURCHASE_STAFF].id,
                "items": [{"product_key": "runner", "warehouse_key": "hyd", "quantity_ordered": 30, "quantity_received": 30, "unit_price": Decimal("480.00"), "tax_rate": Decimal("12.00"), "total_price": Decimal("16128.00")}],
            },
            {
                "key": "po206",
                "vendor_key": "brass",
                "po_number": "PO-206",
                "order_date": date(2026, 5, 20),
                "expected_delivery_date": date(2026, 5, 28),
                "status": PurchaseOrderStatusEnum.DRAFT,
                "subtotal": Decimal("15360.00"),
                "tax_amount": Decimal("1843.20"),
                "total_amount": Decimal("17203.20"),
                "notes": "Awaiting vendor cost approval.",
                "created_by": users_by_role[RoleEnum.PURCHASE_STAFF].id,
                "items": [{"product_key": "tray", "warehouse_key": "del", "quantity_ordered": 12, "quantity_received": 0, "unit_price": Decimal("1280.00"), "tax_rate": Decimal("12.00"), "total_price": Decimal("17203.20")}],
            },
        ],
    )
    sales_orders = _create_sales_orders(
        db,
        tenant.id,
        customers,
        warehouses,
        products,
        [
            {
                "key": "so211",
                "customer_key": "story",
                "so_number": "SO-211",
                "order_date": date(2026, 5, 19),
                "status": SalesOrderStatusEnum.DELIVERED,
                "subtotal": Decimal("9196.00"),
                "tax_amount": Decimal("1103.52"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("10299.52"),
                "notes": "Decor refresh pack delivered.",
                "created_by": users_by_role[RoleEnum.SALES_STAFF].id,
                "items": [{"product_key": "planter", "warehouse_key": "hyd", "quantity": 4, "unit_price": Decimal("1199.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("5371.52")}, {"product_key": "tray", "warehouse_key": "del", "quantity": 2, "unit_price": Decimal("2299.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("5148.00")}],
            },
            {
                "key": "so212",
                "customer_key": "loom",
                "so_number": "SO-212",
                "order_date": date(2026, 5, 18),
                "status": SalesOrderStatusEnum.PACKED,
                "subtotal": Decimal("7794.00"),
                "tax_amount": Decimal("935.28"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("8729.28"),
                "notes": "Ready for courier handoff.",
                "created_by": users_by_role[RoleEnum.SALES_STAFF].id,
                "items": [{"product_key": "cushion", "warehouse_key": "blr", "quantity": 6, "unit_price": Decimal("1299.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("8729.28")}],
            },
            {
                "key": "so213",
                "customer_key": "craft",
                "so_number": "SO-213",
                "order_date": date(2026, 5, 17),
                "status": SalesOrderStatusEnum.CONFIRMED,
                "subtotal": Decimal("6597.00"),
                "tax_amount": Decimal("791.64"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("7388.64"),
                "notes": "Reserved for workspace styling launch.",
                "created_by": users_by_role[RoleEnum.SALES_STAFF].id,
                "items": [{"product_key": "stool", "warehouse_key": "pun", "quantity": 3, "unit_price": Decimal("2199.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("7388.64")}],
            },
        ],
    )
    transfers = _create_transfers(
        db,
        tenant.id,
        users_by_role[RoleEnum.INVENTORY_MANAGER].id,
        warehouses,
        products,
        [
            {"key": "tr-topup-1", "source_warehouse_key": "blr", "destination_warehouse_key": "hyd", "status": StockTransferStatusEnum.IN_TRANSIT, "notes": "Top-up seed rebalancing for South hub.", "items": [{"product_key": "planter", "quantity": 4}, {"product_key": "cushion", "quantity": 6}]}
        ],
    )
    _seed_extended_business_tables(
        db,
        tenant.id,
        users_by_role[RoleEnum.SALES_STAFF].id,
        users_by_role[RoleEnum.PURCHASE_STAFF].id,
        warehouses,
        products,
        sales_orders,
        {},
    )
    db.add_all(
        [
            Notification(tenant_id=tenant.id, user_id=users_by_role[RoleEnum.TENANT_ADMIN].id, title="Workspace expanded", message="Northstar Retail India has been topped up with extended demo inventory and workflow data.", type=NotificationTypeEnum.SYSTEM, is_read=False),
            Notification(tenant_id=tenant.id, user_id=users_by_role[RoleEnum.SALES_STAFF].id, title="New selling lines available", message="Decor, serveware, and textile SKUs are now live in the seeded catalog.", type=NotificationTypeEnum.ORDER_STATUS, is_read=False),
            Notification(tenant_id=tenant.id, user_id=users_by_role[RoleEnum.INVENTORY_MANAGER].id, title="Transfer queued for South hub", message="Additional stock is moving toward Hyderabad as part of the demo dataset expansion.", type=NotificationTypeEnum.STOCK_ALERT, is_read=False),
            AuditLog(tenant_id=tenant.id, user_id=users_by_role[RoleEnum.TENANT_ADMIN].id, action="seed.large.topped_up", entity_type="tenant", entity_id=tenant.id, new_value_json={"products_after": len(existing_products) + len(products)}),
            AuditLog(tenant_id=tenant.id, user_id=users_by_role[RoleEnum.SALES_STAFF].id, action="sales_order.created", entity_type="sales_order", entity_id=sales_orders["so211"].id, new_value_json={"status": sales_orders["so211"].status.value}),
            AuditLog(tenant_id=tenant.id, user_id=users_by_role[RoleEnum.INVENTORY_MANAGER].id, action="inventory.transfer.created", entity_type="stock_transfer", entity_id=transfers["tr-topup-1"].id, new_value_json={"status": transfers["tr-topup-1"].status.value}),
        ]
    )
    db.commit()


def _seed_small_workspace(db: Session) -> None:
    existing_tenant = db.scalar(select(Tenant).where(Tenant.company_name == SMALL_TENANT_NAME))
    if existing_tenant:
        return

    tenant = Tenant(
        company_name=SMALL_TENANT_NAME,
        contact_email="hello@cloverliving.in",
        phone="+91 9899013001",
        address="JP Nagar, Bengaluru",
        gst_number="29AABCC4412L1ZV",
        business_type="Boutique Home Styling Studio",
        status=TenantStatusEnum.ACTIVE,
        subscription_plan_id=1,
    )
    db.add(tenant)
    db.flush()

    users = _create_users(
        db,
        tenant.id,
        [
            {"key": "admin", "name": "Neha Kapoor", "email": "neha@cloverliving.in", "role": RoleEnum.TENANT_ADMIN},
            {"key": "sales", "name": "Arjun Pillai", "email": "arjun@cloverliving.in", "role": RoleEnum.SALES_STAFF},
            {"key": "inventory", "name": "Sana Khan", "email": "sana@cloverliving.in", "role": RoleEnum.INVENTORY_MANAGER},
        ],
    )
    categories = _create_lookup_records(
        db,
        Category,
        tenant.id,
        [
            {"key": "decor", "name": "Decor", "description": "Home styling accents", "status": RecordStatusEnum.ACTIVE},
            {"key": "linen", "name": "Linen", "description": "Table and soft furnishing basics", "status": RecordStatusEnum.ACTIVE},
        ],
    )
    brands = _create_lookup_records(
        db,
        Brand,
        tenant.id,
        [
            {"key": "clover", "name": "Clover Living", "description": "Signature styling line", "status": RecordStatusEnum.ACTIVE},
            {"key": "loom", "name": "Loomcraft", "description": "Curated textile label", "status": RecordStatusEnum.ACTIVE},
        ],
    )
    warehouses = _create_lookup_records(
        db,
        Warehouse,
        tenant.id,
        [
            {
                "key": "blr",
                "name": "Studio Stockroom",
                "code": "CLV-BLR",
                "address": "JP Nagar 2nd Phase, Bengaluru",
                "city": "Bengaluru",
                "state": "Karnataka",
                "country": "India",
                "manager_name": "Sana Khan",
                "phone": "+91 9899013002",
                "is_default": True,
                "status": RecordStatusEnum.ACTIVE,
            }
        ],
    )
    vendors = _create_lookup_records(
        db,
        Vendor,
        tenant.id,
        [
            {"key": "textile", "name": "Mango Leaf Textiles", "email": "sales@mangoleaf.in", "phone": "+91 9899013003", "gst_number": "29AACCM1122K1ZT", "address": "Karur, Tamil Nadu", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
            {"key": "ceramics", "name": "Clayroute Studios", "email": "trade@clayroute.in", "phone": "+91 9899013004", "gst_number": "33AACCC6122N1Z9", "address": "Auroville, Tamil Nadu", "opening_balance": Decimal("0.00"), "status": RecordStatusEnum.ACTIVE},
        ],
    )
    customers = _create_lookup_records(
        db,
        Customer,
        tenant.id,
        [
            {"key": "olive", "name": "Olive Door Homes", "email": "procurement@olivedoor.in", "phone": "+91 9899013005", "gst_number": "29AACCO3311E1ZL", "billing_address": "Sadashivanagar, Bengaluru", "shipping_address": "Sadashivanagar, Bengaluru", "status": RecordStatusEnum.ACTIVE},
            {"key": "atelier", "name": "Atelier Courtyard", "email": "hello@ateliercourtyard.in", "phone": "+91 9899013006", "gst_number": "29AACCA7012P1ZP", "billing_address": "Indiranagar, Bengaluru", "shipping_address": "Indiranagar, Bengaluru", "status": RecordStatusEnum.ACTIVE},
        ],
    )
    products = _create_products(
        db,
        tenant.id,
        categories,
        brands,
        vendors,
        [
            {"key": "vase", "name": "Terracotta Bud Vase", "sku": "CLV-101", "barcode": "8906007203101", "category_key": "decor", "brand_key": "clover", "vendor_key": "ceramics", "description": "Small matte terracotta vase for shelf styling.", "unit": "pcs", "cost_price": Decimal("260.00"), "selling_price": Decimal("599.00"), "reorder_level": 12, "status": RecordStatusEnum.ACTIVE},
            {"key": "throw", "name": "Handloom Throw", "sku": "CLV-102", "barcode": "8906007203102", "category_key": "linen", "brand_key": "loom", "vendor_key": "textile", "description": "Cotton handloom throw for soft styling layers.", "unit": "pcs", "cost_price": Decimal("580.00"), "selling_price": Decimal("1199.00"), "reorder_level": 10, "status": RecordStatusEnum.ACTIVE},
            {"key": "tray", "name": "Wooden Trinket Tray", "sku": "CLV-103", "barcode": "8906007203103", "category_key": "decor", "brand_key": "clover", "vendor_key": "ceramics", "description": "Catch-all tray for bedside and console styling.", "unit": "pcs", "cost_price": Decimal("330.00"), "selling_price": Decimal("699.00"), "reorder_level": 16, "status": RecordStatusEnum.ACTIVE},
            {"key": "runner", "name": "Woven Table Runner", "sku": "CLV-104", "barcode": "8906007203104", "category_key": "linen", "brand_key": "loom", "vendor_key": "textile", "description": "Neutral woven runner for compact dining setups.", "unit": "pcs", "cost_price": Decimal("440.00"), "selling_price": Decimal("899.00"), "reorder_level": 10, "status": RecordStatusEnum.ACTIVE},
        ],
    )
    _add_stock_rows(
        db,
        tenant.id,
        warehouses,
        products,
        [
            {"warehouse_key": "blr", "product_key": "vase", "quantity": 18, "reserved_quantity": 1, "reorder_level": 12},
            {"warehouse_key": "blr", "product_key": "throw", "quantity": 14, "reserved_quantity": 0, "reorder_level": 10},
            {"warehouse_key": "blr", "product_key": "tray", "quantity": 10, "reserved_quantity": 0, "reorder_level": 16},
            {"warehouse_key": "blr", "product_key": "runner", "quantity": 12, "reserved_quantity": 2, "reorder_level": 10},
        ],
    )

    purchase_orders = _create_purchase_orders(
        db,
        tenant.id,
        vendors,
        warehouses,
        products,
        [
            {
                "key": "po1",
                "vendor_key": "textile",
                "po_number": "PO-CLV-001",
                "order_date": date(2026, 5, 17),
                "expected_delivery_date": date(2026, 5, 22),
                "status": PurchaseOrderStatusEnum.ISSUED,
                "subtotal": Decimal("4400.00"),
                "tax_amount": Decimal("528.00"),
                "total_amount": Decimal("4928.00"),
                "notes": "Starter textile top-up for studio launch orders.",
                "created_by": users["admin"].id,
                "items": [{"product_key": "runner", "warehouse_key": "blr", "quantity_ordered": 10, "quantity_received": 0, "unit_price": Decimal("440.00"), "tax_rate": Decimal("12.00"), "total_price": Decimal("4928.00")}],
            }
        ],
    )
    sales_orders = _create_sales_orders(
        db,
        tenant.id,
        customers,
        warehouses,
        products,
        [
            {
                "key": "so1",
                "customer_key": "olive",
                "so_number": "SO-CLV-001",
                "order_date": date(2026, 5, 18),
                "status": SalesOrderStatusEnum.DRAFT,
                "subtotal": Decimal("2398.00"),
                "tax_amount": Decimal("287.76"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("2685.76"),
                "notes": "Awaiting customer confirmation.",
                "created_by": users["sales"].id,
                "items": [{"product_key": "throw", "warehouse_key": "blr", "quantity": 2, "unit_price": Decimal("1199.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("2685.76")}],
            },
            {
                "key": "so2",
                "customer_key": "atelier",
                "so_number": "SO-CLV-002",
                "order_date": date(2026, 5, 16),
                "status": SalesOrderStatusEnum.DELIVERED,
                "subtotal": Decimal("1298.00"),
                "tax_amount": Decimal("155.76"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("1453.76"),
                "notes": "Delivered styling sample order.",
                "created_by": users["sales"].id,
                "items": [{"product_key": "vase", "warehouse_key": "blr", "quantity": 1, "unit_price": Decimal("599.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("670.88")}, {"product_key": "tray", "warehouse_key": "blr", "quantity": 1, "unit_price": Decimal("699.00"), "tax_rate": Decimal("12.00"), "discount": Decimal("0.00"), "total_price": Decimal("782.88")}],
            },
        ],
    )

    db.add_all(
        [
            InventoryTransaction(
                tenant_id=tenant.id,
                product_id=products["vase"].id,
                warehouse_id=warehouses["blr"].id,
                transaction_type=InventoryTransactionTypeEnum.STOCK_IN,
                quantity=18,
                reference_type="OPENING_BALANCE",
                reference_id=None,
                note="Seeded opening stock",
                created_by=users["inventory"].id,
            ),
            InventoryTransaction(
                tenant_id=tenant.id,
                product_id=products["vase"].id,
                warehouse_id=warehouses["blr"].id,
                transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_DEDUCT,
                quantity=-1,
                reference_type="sales_order",
                reference_id=sales_orders["so2"].id,
                note="Delivered sample order",
                created_by=users["sales"].id,
            ),
        ]
    )
    db.add_all(
        [
            Notification(tenant_id=tenant.id, user_id=users["admin"].id, title="Studio workspace ready", message="Clover Living Studio has a light but usable seed dataset.", type=NotificationTypeEnum.SYSTEM, is_read=False),
            Notification(tenant_id=tenant.id, user_id=users["inventory"].id, title="Tray stock is slim", message="Wooden Trinket Tray is nearing its reorder threshold.", type=NotificationTypeEnum.LOW_STOCK, is_read=False),
        ]
    )
    db.add_all(
        [
            AuditLog(tenant_id=tenant.id, user_id=users["admin"].id, action="seed.small.created", entity_type="tenant", entity_id=tenant.id, new_value_json={"workspace": SMALL_TENANT_NAME}),
            AuditLog(tenant_id=tenant.id, user_id=users["sales"].id, action="sales_order.delivered", entity_type="sales_order", entity_id=sales_orders["so2"].id, new_value_json={"status": sales_orders["so2"].status.value}),
            AuditLog(tenant_id=tenant.id, user_id=users["purchase"].id if "purchase" in users else users["admin"].id, action="purchase_order.issued", entity_type="purchase_order", entity_id=purchase_orders["po1"].id, new_value_json={"status": purchase_orders["po1"].status.value}),
        ]
    )
    db.commit()


def _create_users(db: Session, tenant_id: int, payloads: list[dict]) -> dict[str, User]:
    now = datetime.now(UTC)
    users: dict[str, User] = {}
    for payload in payloads:
        data = payload.copy()
        key = data.pop("key")
        users[key] = User(
            tenant_id=tenant_id,
            password_hash=hash_password(DEFAULT_PASSWORD),
            status=UserStatusEnum.ACTIVE,
            last_login_at=now,
            **data,
        )
    db.add_all(users.values())
    db.flush()
    return users


def _create_lookup_records(db: Session, model, tenant_id: int, payloads: list[dict]):
    records = {}
    for payload in payloads:
        data = payload.copy()
        key = data.pop("key")
        records[key] = model(tenant_id=tenant_id, **data)
    db.add_all(records.values())
    db.flush()
    return records


def _ensure_lookup_records(db: Session, model, tenant_id: int, payloads: list[dict], unique_field: str):
    records = {}
    for payload in payloads:
        data = payload.copy()
        key = data.pop("key")
        existing = db.scalar(
            select(model).where(
                model.tenant_id == tenant_id,
                getattr(model, unique_field) == data[unique_field],
            )
        )
        if existing:
            records[key] = existing
            continue
        record = model(tenant_id=tenant_id, **data)
        db.add(record)
        db.flush()
        records[key] = record
    return records


def _create_products(
    db: Session,
    tenant_id: int,
    categories: dict[str, Category],
    brands: dict[str, Brand],
    vendors: dict[str, Vendor],
    payloads: list[dict],
) -> dict[str, Product]:
    records: dict[str, Product] = {}
    for payload in payloads:
        data = payload.copy()
        key = data.pop("key")
        category_key = data.pop("category_key")
        brand_key = data.pop("brand_key")
        vendor_key = data.pop("vendor_key")
        records[key] = Product(
            tenant_id=tenant_id,
            category_id=categories[category_key].id,
            brand_id=brands[brand_key].id,
            vendor_id=vendors[vendor_key].id,
            **data,
        )
    db.add_all(records.values())
    db.flush()
    return records


def _ensure_products(
    db: Session,
    tenant_id: int,
    categories: dict[str, Category],
    brands: dict[str, Brand],
    vendors: dict[str, Vendor],
    payloads: list[dict],
) -> dict[str, Product]:
    records: dict[str, Product] = {}
    for payload in payloads:
        data = payload.copy()
        key = data.pop("key")
        existing = db.scalar(select(Product).where(Product.tenant_id == tenant_id, Product.sku == data["sku"]))
        if existing:
            records[key] = existing
            continue
        category_key = data.pop("category_key")
        brand_key = data.pop("brand_key")
        vendor_key = data.pop("vendor_key")
        record = Product(
            tenant_id=tenant_id,
            category_id=categories[category_key].id,
            brand_id=brands[brand_key].id,
            vendor_id=vendors[vendor_key].id,
            **data,
        )
        db.add(record)
        db.flush()
        records[key] = record
    return records


def _add_stock_rows(
    db: Session,
    tenant_id: int,
    warehouses: dict[str, Warehouse],
    products: dict[str, Product],
    payloads: list[dict],
) -> None:
    rows = []
    for payload in payloads:
        quantity = int(payload["quantity"])
        reserved_quantity = int(payload.get("reserved_quantity", 0))
        rows.append(
            WarehouseStock(
                tenant_id=tenant_id,
                warehouse_id=warehouses[payload["warehouse_key"]].id,
                product_id=products[payload["product_key"]].id,
                quantity=quantity,
                reserved_quantity=reserved_quantity,
                available_quantity=max(quantity - reserved_quantity, 0),
                reorder_level=int(payload["reorder_level"]),
            )
        )
    db.add_all(rows)
    db.flush()


def _create_purchase_orders(
    db: Session,
    tenant_id: int,
    vendors: dict[str, Vendor],
    warehouses: dict[str, Warehouse],
    products: dict[str, Product],
    payloads: list[dict],
) -> dict[str, PurchaseOrder]:
    records: dict[str, PurchaseOrder] = {}
    items: list[PurchaseOrderItem] = []
    for payload in payloads:
        data = payload.copy()
        key = data.pop("key")
        item_payloads = data.pop("items")
        vendor_key = data.pop("vendor_key")
        record = PurchaseOrder(tenant_id=tenant_id, vendor_id=vendors[vendor_key].id, **data)
        records[key] = record
        db.add(record)
        db.flush()
        for item_payload in item_payloads:
            items.append(
                PurchaseOrderItem(
                    purchase_order_id=record.id,
                    product_id=products[item_payload["product_key"]].id,
                    warehouse_id=warehouses[item_payload["warehouse_key"]].id,
                    quantity_ordered=item_payload["quantity_ordered"],
                    quantity_received=item_payload["quantity_received"],
                    unit_price=item_payload["unit_price"],
                    tax_rate=item_payload["tax_rate"],
                    total_price=item_payload["total_price"],
                )
            )
    db.add_all(items)
    db.flush()
    return records


def _create_sales_orders(
    db: Session,
    tenant_id: int,
    customers: dict[str, Customer],
    warehouses: dict[str, Warehouse],
    products: dict[str, Product],
    payloads: list[dict],
) -> dict[str, SalesOrder]:
    records: dict[str, SalesOrder] = {}
    items: list[SalesOrderItem] = []
    for payload in payloads:
        data = payload.copy()
        key = data.pop("key")
        item_payloads = data.pop("items")
        customer_key = data.pop("customer_key")
        record = SalesOrder(tenant_id=tenant_id, customer_id=customers[customer_key].id, **data)
        records[key] = record
        db.add(record)
        db.flush()
        for item_payload in item_payloads:
            items.append(
                SalesOrderItem(
                    sales_order_id=record.id,
                    product_id=products[item_payload["product_key"]].id,
                    warehouse_id=warehouses[item_payload["warehouse_key"]].id,
                    quantity=item_payload["quantity"],
                    unit_price=item_payload["unit_price"],
                    tax_rate=item_payload["tax_rate"],
                    discount=item_payload["discount"],
                    total_price=item_payload["total_price"],
                )
            )
    db.add_all(items)
    db.flush()
    return records


def _create_transfers(
    db: Session,
    tenant_id: int,
    created_by: int,
    warehouses: dict[str, Warehouse],
    products: dict[str, Product],
    payloads: list[dict],
) -> dict[str, StockTransfer]:
    records: dict[str, StockTransfer] = {}
    items: list[StockTransferItem] = []
    for payload in payloads:
        data = payload.copy()
        key = data.pop("key")
        item_payloads = data.pop("items")
        source_warehouse_key = data.pop("source_warehouse_key")
        destination_warehouse_key = data.pop("destination_warehouse_key")
        record = StockTransfer(
            tenant_id=tenant_id,
            source_warehouse_id=warehouses[source_warehouse_key].id,
            destination_warehouse_id=warehouses[destination_warehouse_key].id,
            created_by=created_by,
            **data,
        )
        records[key] = record
        db.add(record)
        db.flush()
        for item_payload in item_payloads:
            items.append(
                StockTransferItem(
                    stock_transfer_id=record.id,
                    product_id=products[item_payload["product_key"]].id,
                    quantity=item_payload["quantity"],
                )
            )
    db.add_all(items)
    db.flush()
    return records


def _seed_extended_business_tables(
    db: Session,
    tenant_id: int,
    sales_user_id: int,
    purchase_user_id: int,
    warehouses: dict[str, Warehouse],
    products: dict[str, Product],
    sales_orders: dict[str, SalesOrder],
    purchase_orders: dict[str, PurchaseOrder],
) -> None:
    if not sales_orders:
        sales_order_rows = db.scalars(select(SalesOrder).where(SalesOrder.tenant_id == tenant_id).order_by(SalesOrder.id.asc())).all()
        sales_orders = {order.so_number: order for order in sales_order_rows}
    if not purchase_orders:
        purchase_order_rows = db.scalars(select(PurchaseOrder).where(PurchaseOrder.tenant_id == tenant_id).order_by(PurchaseOrder.id.asc())).all()
        purchase_orders = {order.po_number: order for order in purchase_order_rows}

    primary_sales_order = next(iter(sales_orders.values()), None)
    primary_purchase_order = next(iter(purchase_orders.values()), None)
    if not primary_sales_order or not primary_purchase_order:
        return

    sales_items = db.scalars(select(SalesOrderItem).where(SalesOrderItem.sales_order_id == primary_sales_order.id)).all()
    purchase_items = db.scalars(select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == primary_purchase_order.id)).all()
    if not sales_items or not purchase_items:
        return

    if not db.scalar(select(Package).where(Package.tenant_id == tenant_id, Package.package_number == f"PKG-{primary_sales_order.so_number}")):
        package = Package(
            tenant_id=tenant_id,
            sales_order_id=primary_sales_order.id,
            package_number=f"PKG-{primary_sales_order.so_number}",
            status=PackageStatusEnum.PACKED,
            notes="Seeded package for workflow coverage.",
            created_by=sales_user_id,
        )
        db.add(package)
        db.flush()
        db.add_all(
            [
                PackageItem(
                    package_id=package.id,
                    sales_order_item_id=item.id,
                    product_id=item.product_id,
                    warehouse_id=item.warehouse_id,
                    quantity=max(1, min(item.quantity, 2)),
                )
                for item in sales_items[:2]
            ]
        )

    if not db.scalar(select(Invoice).where(Invoice.tenant_id == tenant_id, Invoice.invoice_number == f"INV-{primary_sales_order.so_number}")):
        invoice = Invoice(
            tenant_id=tenant_id,
            sales_order_id=primary_sales_order.id,
            customer_id=primary_sales_order.customer_id,
            invoice_number=f"INV-{primary_sales_order.so_number}",
            invoice_date=primary_sales_order.order_date,
            due_date=primary_sales_order.order_date,
            status=InvoiceStatusEnum.SENT,
            subtotal=primary_sales_order.subtotal,
            tax_amount=primary_sales_order.tax_amount,
            discount_amount=primary_sales_order.discount_amount,
            total_amount=primary_sales_order.total_amount,
            notes="Seeded invoice coverage record.",
            created_by=sales_user_id,
        )
        db.add(invoice)

    if not db.scalar(select(SalesReturn).where(SalesReturn.tenant_id == tenant_id, SalesReturn.return_number == f"SR-{primary_sales_order.so_number}")):
        sales_return = SalesReturn(
            tenant_id=tenant_id,
            sales_order_id=primary_sales_order.id,
            customer_id=primary_sales_order.customer_id,
            return_number=f"SR-{primary_sales_order.so_number}",
            return_date=primary_sales_order.order_date,
            status=SalesReturnStatusEnum.RECEIVED,
            notes="Seeded sales return coverage record.",
            created_by=sales_user_id,
        )
        db.add(sales_return)
        db.flush()
        first_sales_item = sales_items[0]
        db.add(
            SalesReturnItem(
                sales_return_id=sales_return.id,
                sales_order_item_id=first_sales_item.id,
                product_id=first_sales_item.product_id,
                warehouse_id=first_sales_item.warehouse_id,
                quantity=1,
                reason="Sample damage",
                notes="Seeded return line.",
            )
        )

    if not db.scalar(select(PurchaseReceive).where(PurchaseReceive.tenant_id == tenant_id, PurchaseReceive.receive_number == f"GRN-{primary_purchase_order.po_number}")):
        purchase_receive = PurchaseReceive(
            tenant_id=tenant_id,
            purchase_order_id=primary_purchase_order.id,
            vendor_id=primary_purchase_order.vendor_id,
            receive_number=f"GRN-{primary_purchase_order.po_number}",
            received_at=primary_purchase_order.order_date,
            status=PurchaseReceiveStatusEnum.POSTED,
            notes="Seeded purchase receive coverage record.",
            created_by=purchase_user_id,
        )
        db.add(purchase_receive)
        db.flush()
        first_purchase_item = purchase_items[0]
        db.add(
            PurchaseReceiveItem(
                purchase_receive_id=purchase_receive.id,
                purchase_order_item_id=first_purchase_item.id,
                product_id=first_purchase_item.product_id,
                warehouse_id=first_purchase_item.warehouse_id,
                quantity_received=max(1, min(first_purchase_item.quantity_ordered, 2)),
            )
        )

    if not db.scalar(select(Bill).where(Bill.tenant_id == tenant_id, Bill.bill_number == f"BILL-{primary_purchase_order.po_number}")):
        bill = Bill(
            tenant_id=tenant_id,
            purchase_order_id=primary_purchase_order.id,
            vendor_id=primary_purchase_order.vendor_id,
            bill_number=f"BILL-{primary_purchase_order.po_number}",
            bill_date=primary_purchase_order.order_date,
            due_date=primary_purchase_order.expected_delivery_date,
            status=BillStatusEnum.POSTED,
            subtotal=primary_purchase_order.subtotal,
            tax_amount=primary_purchase_order.tax_amount,
            total_amount=primary_purchase_order.total_amount,
            notes="Seeded payable coverage record.",
            created_by=purchase_user_id,
        )
        db.add(bill)

    batch_product = products.get("runner") or products.get("lamp") or next(iter(products.values()))
    batch_warehouse = warehouses.get("hyd") or warehouses.get("blr") or next(iter(warehouses.values()))
    batch = db.scalar(
        select(InventoryBatch).where(
            InventoryBatch.tenant_id == tenant_id,
            InventoryBatch.product_id == batch_product.id,
            InventoryBatch.batch_number == f"BATCH-{batch_product.sku}",
        )
    )
    if not batch:
        batch = InventoryBatch(
            tenant_id=tenant_id,
            product_id=batch_product.id,
            warehouse_id=batch_warehouse.id,
            batch_number=f"BATCH-{batch_product.sku}",
            expiry_date=date(2027, 12, 31),
            warranty_until=date(2027, 12, 31),
            quantity=12,
            available_quantity=10,
        )
        db.add(batch)
        db.flush()

    serial_product = products.get("table") or products.get("vase") or next(iter(products.values()))
    serial_warehouse = warehouses.get("blr") or next(iter(warehouses.values()))
    for offset in range(1, 4):
        serial_number = f"{serial_product.sku}-SN-{offset:03d}"
        if db.scalar(select(InventorySerial).where(InventorySerial.tenant_id == tenant_id, InventorySerial.serial_number == serial_number)):
            continue
        db.add(
            InventorySerial(
                tenant_id=tenant_id,
                product_id=serial_product.id,
                warehouse_id=serial_warehouse.id,
                batch_id=batch.id if batch.product_id == serial_product.id else None,
                serial_number=serial_number,
                expires_on=date(2027, 12, 31),
                warranty_until=date(2028, 12, 31),
                status=InventorySerialStatusEnum.IN_STOCK,
            )
        )

    db.flush()
