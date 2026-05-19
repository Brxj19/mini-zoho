from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from app.models.enums import InventorySerialStatusEnum
from app.models.enums import InventoryTransactionTypeEnum
from app.models.inventory_batch import InventoryBatch
from app.models.inventory_serial import InventorySerial
from app.models.inventory_transaction import InventoryTransaction
from app.models.subscription_plan import SubscriptionPlan
from app.schemas.inventory import BatchTrackingInput
from app.schemas.inventory import StockInRequest
from app.schemas.inventory import StockOutRequest
from app.services.inventory_service import InventoryService


def test_batch_and_serial_tracking_follow_stock_in_and_out(db, tenant_context):
    advanced_plan = SubscriptionPlan(
        code="ADV-TRACK",
        name="Advanced Tracking",
        monthly_price=Decimal("0.00"),
        annual_price=Decimal("0.00"),
        max_users=5,
        max_products=25,
        max_warehouses=5,
        max_monthly_sales_orders=25,
        max_monthly_purchase_orders=25,
        max_monthly_stock_transfers=25,
        barcode_enabled=True,
        advanced_inventory_enabled=True,
        integrations_enabled=False,
        ai_assistant_enabled=False,
    )
    db.add(advanced_plan)
    db.flush()
    tenant_context.tenant.subscription_plan_id = advanced_plan.id
    tenant_context.product.batch_tracking_enabled = True
    tenant_context.product.serial_tracking_enabled = True
    tenant_context.product.expiry_tracking_enabled = True
    tenant_context.product.warranty_tracking_enabled = True
    db.add(tenant_context.tenant)
    db.add(tenant_context.product)
    db.commit()

    service = InventoryService(db)
    stock_in = StockInRequest(
        product_id=tenant_context.product.id,
        warehouse_id=tenant_context.warehouse_primary.id,
        quantity=2,
        note="Tracked stock received",
        batch=BatchTrackingInput(
            batch_number="BATCH-2026-05",
            expiry_date=date(2027, 5, 31),
            warranty_until=date(2027, 11, 30),
        ),
        serial_numbers=["SR-001", "SR-002"],
    )
    service.stock_in(current_user=tenant_context.user, payload=stock_in, request_meta=tenant_context.request_meta)

    batch = db.scalar(select(InventoryBatch).where(InventoryBatch.batch_number == "BATCH-2026-05"))
    serials = list(db.scalars(select(InventorySerial).where(InventorySerial.batch_id == batch.id)).all())
    assert batch.quantity == 2
    assert batch.available_quantity == 2
    assert {serial.serial_number for serial in serials} == {"SR-001", "SR-002"}
    assert all(serial.status == InventorySerialStatusEnum.IN_STOCK for serial in serials)

    stock_out = StockOutRequest(
        product_id=tenant_context.product.id,
        warehouse_id=tenant_context.warehouse_primary.id,
        quantity=1,
        note="Issued tracked stock",
        batch_number="BATCH-2026-05",
        serial_numbers=["SR-001"],
    )
    service.stock_out(current_user=tenant_context.user, payload=stock_out, request_meta=tenant_context.request_meta)

    batch = db.scalar(select(InventoryBatch).where(InventoryBatch.batch_number == "BATCH-2026-05"))
    sold_serial = db.scalar(select(InventorySerial).where(InventorySerial.serial_number == "SR-001"))
    in_stock_serial = db.scalar(select(InventorySerial).where(InventorySerial.serial_number == "SR-002"))
    stock_out_count = db.scalar(
        select(func.count(InventoryTransaction.id)).where(
            InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.STOCK_OUT,
            InventoryTransaction.product_id == tenant_context.product.id,
        )
    )

    assert batch.quantity == 1
    assert batch.available_quantity == 1
    assert sold_serial.status == InventorySerialStatusEnum.SOLD
    assert in_stock_serial.status == InventorySerialStatusEnum.IN_STOCK
    assert stock_out_count >= 1
