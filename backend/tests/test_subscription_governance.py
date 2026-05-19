from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models.subscription_plan import SubscriptionPlan
from app.schemas.sales_order import SalesOrderCreate
from app.schemas.sales_order import SalesOrderItemInput
from app.schemas.user import UserCreate
from app.services.sales_order_service import SalesOrderService
from app.services.user_service import UserService


def test_user_creation_respects_plan_limits(db, tenant_context):
    limited_plan = SubscriptionPlan(
        code="LIMIT-1",
        name="Limit One User",
        monthly_price=Decimal("0.00"),
        annual_price=Decimal("0.00"),
        max_users=1,
        max_products=10,
        max_warehouses=2,
        max_monthly_sales_orders=10,
        max_monthly_purchase_orders=10,
        max_monthly_stock_transfers=10,
        barcode_enabled=True,
        advanced_inventory_enabled=False,
        integrations_enabled=False,
        ai_assistant_enabled=False,
    )
    db.add(limited_plan)
    db.flush()
    tenant_context.tenant.subscription_plan_id = limited_plan.id
    db.add(tenant_context.tenant)
    db.commit()

    payload = UserCreate(
        name="Priya Menon",
        email="priya.menon@northstarretail.in",
        password="ChangeMe123!",
        role="VIEWER",
        tenant_id=tenant_context.tenant.id,
    )

    with pytest.raises(HTTPException) as exc:
        UserService(db).create_user(tenant_context.user, payload)

    assert exc.value.status_code == 409
    assert "users limit" in exc.value.detail


def test_monthly_sales_order_limit_blocks_new_orders(db, tenant_context):
    limited_plan = SubscriptionPlan(
        code="LIMIT-SO",
        name="One Sales Order",
        monthly_price=Decimal("0.00"),
        annual_price=Decimal("0.00"),
        max_users=5,
        max_products=20,
        max_warehouses=5,
        max_monthly_sales_orders=1,
        max_monthly_purchase_orders=10,
        max_monthly_stock_transfers=10,
        barcode_enabled=True,
        advanced_inventory_enabled=False,
        integrations_enabled=False,
        ai_assistant_enabled=False,
    )
    db.add(limited_plan)
    db.flush()
    tenant_context.tenant.subscription_plan_id = limited_plan.id
    db.add(tenant_context.tenant)
    db.commit()

    service = SalesOrderService(db)
    payload = SalesOrderCreate(
        customer_id=tenant_context.customer.id,
        so_number="SO-LIMIT-001",
        order_date=tenant_context.order_date,
        notes="First order",
        items=[
            SalesOrderItemInput(
                product_id=tenant_context.product.id,
                warehouse_id=tenant_context.warehouse_primary.id,
                quantity=1,
                unit_price=Decimal("119.00"),
                tax_rate=Decimal("0.00"),
                discount=Decimal("0.00"),
            )
        ],
    )
    service.create_sales_order(current_user=tenant_context.user, payload=payload)

    second_payload = SalesOrderCreate(
        customer_id=tenant_context.customer.id,
        so_number="SO-LIMIT-002",
        order_date=tenant_context.order_date,
        notes="Second order should fail",
        items=[
            SalesOrderItemInput(
                product_id=tenant_context.product.id,
                warehouse_id=tenant_context.warehouse_primary.id,
                quantity=1,
                unit_price=Decimal("119.00"),
                tax_rate=Decimal("0.00"),
                discount=Decimal("0.00"),
            )
        ],
    )

    with pytest.raises(HTTPException) as exc:
        service.create_sales_order(current_user=tenant_context.user, payload=second_payload)

    assert exc.value.status_code == 409
    assert "monthly sales orders limit" in exc.value.detail
