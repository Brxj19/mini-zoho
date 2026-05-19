from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import event
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models import Base
from app.models.brand import Brand
from app.models.category import Category
from app.models.customer import Customer
from app.models.enums import RecordStatusEnum
from app.models.enums import RoleEnum
from app.models.enums import TenantStatusEnum
from app.models.enums import UserStatusEnum
from app.models.product import Product
from app.models.tenant import Tenant
from app.models.user import User
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock


@pytest.fixture
def db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_local()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def tenant_context(db: Session) -> SimpleNamespace:
    tenant = Tenant(
        company_name="Northstar Retail Private Limited",
        contact_email="ops@northstarretail.in",
        phone="+91-9876543210",
        status=TenantStatusEnum.ACTIVE,
    )
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        name="Aarav Mehta",
        email="aarav.mehta@northstarretail.in",
        password_hash="test-hash",
        role=RoleEnum.TENANT_ADMIN,
        status=UserStatusEnum.ACTIVE,
    )
    category = Category(
        tenant_id=tenant.id,
        name="Personal Care",
        description="Personal care assortment",
        status=RecordStatusEnum.ACTIVE,
    )
    brand = Brand(
        tenant_id=tenant.id,
        name="Sundrop Essentials",
        description="Indian household FMCG brand",
        status=RecordStatusEnum.ACTIVE,
    )
    vendor = Vendor(
        tenant_id=tenant.id,
        name="Sharma Wholesale Traders",
        email="procurement@sharmawholesale.in",
        phone="+91-9811111111",
        gst_number="27ABCDE1234F1Z5",
        status=RecordStatusEnum.ACTIVE,
    )
    customer = Customer(
        tenant_id=tenant.id,
        name="Kiran Stores",
        email="owner@kiranstores.in",
        phone="+91-9822222222",
        gst_number="27PQRSX4567K2Z8",
        status=RecordStatusEnum.ACTIVE,
    )
    warehouse_primary = Warehouse(
        tenant_id=tenant.id,
        name="Mumbai Central Warehouse",
        code="MUM-01",
        city="Mumbai",
        state="Maharashtra",
        country="India",
        manager_name="Neha Kulkarni",
        is_default=True,
        status=RecordStatusEnum.ACTIVE,
    )
    warehouse_secondary = Warehouse(
        tenant_id=tenant.id,
        name="Pune Overflow Warehouse",
        code="PUN-02",
        city="Pune",
        state="Maharashtra",
        country="India",
        manager_name="Rohit Patil",
        is_default=False,
        status=RecordStatusEnum.ACTIVE,
    )
    db.add_all([user, category, brand, vendor, customer, warehouse_primary, warehouse_secondary])
    db.flush()

    product = Product(
        tenant_id=tenant.id,
        name="Neem Fresh Face Wash",
        sku="NF-FW-100",
        barcode="8901234567890",
        category_id=category.id,
        brand_id=brand.id,
        vendor_id=vendor.id,
        unit="pcs",
        cost_price=Decimal("70.00"),
        selling_price=Decimal("119.00"),
        reorder_level=5,
        status=RecordStatusEnum.ACTIVE,
    )
    db.add(product)
    db.flush()

    stock = WarehouseStock(
        tenant_id=tenant.id,
        warehouse_id=warehouse_primary.id,
        product_id=product.id,
        quantity=40,
        reserved_quantity=0,
        available_quantity=40,
        reorder_level=5,
    )
    db.add(stock)
    db.commit()

    return SimpleNamespace(
        tenant=tenant,
        user=user,
        category=category,
        brand=brand,
        vendor=vendor,
        customer=customer,
        warehouse_primary=warehouse_primary,
        warehouse_secondary=warehouse_secondary,
        product=product,
        stock=stock,
        order_date=date(2026, 5, 19),
        request_meta={"ip_address": "127.0.0.1", "user_agent": "pytest"},
    )
