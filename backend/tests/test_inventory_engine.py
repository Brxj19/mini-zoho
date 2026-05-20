from __future__ import annotations

from sqlalchemy import func
from sqlalchemy import select

import pytest
from fastapi import HTTPException

from app.models.enums import InventoryTransactionTypeEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.warehouse_stock import WarehouseStock
from app.services.inventory_engine import InventoryEngine


def _get_stock(db, tenant_context) -> WarehouseStock:
    return db.scalar(
        select(WarehouseStock).where(
            WarehouseStock.tenant_id == tenant_context.tenant.id,
            WarehouseStock.product_id == tenant_context.product.id,
            WarehouseStock.warehouse_id == tenant_context.warehouse_primary.id,
        )
    )


def test_stock_in_increases_quantity(db, tenant_context):
    engine = InventoryEngine(db)

    transaction = engine.stock_in(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=5,
        note="Restocked",
        reference_type="manual",
        reference_id=101,
        request_meta=tenant_context.request_meta,
    )

    stock = _get_stock(db, tenant_context)
    assert transaction.transaction_type == InventoryTransactionTypeEnum.STOCK_IN
    assert stock.quantity == 45
    assert stock.reserved_quantity == 0
    assert stock.available_quantity == 45


def test_stock_out_decreases_quantity(db, tenant_context):
    engine = InventoryEngine(db)

    engine.stock_out(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=7,
        note="Manual issue",
        reference_type="manual",
        reference_id=102,
        request_meta=tenant_context.request_meta,
    )

    stock = _get_stock(db, tenant_context)
    assert stock.quantity == 33
    assert stock.available_quantity == 33


def test_reserve_changes_only_reserved_quantity(db, tenant_context):
    engine = InventoryEngine(db)

    engine.reserve_for_sales_order(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=6,
        sales_order_id=201,
        note="Reserve",
        request_meta=tenant_context.request_meta,
    )

    stock = _get_stock(db, tenant_context)
    assert stock.quantity == 40
    assert stock.reserved_quantity == 6
    assert stock.available_quantity == 34


def test_delivery_decreases_quantity_and_reserved_when_reserved(db, tenant_context):
    engine = InventoryEngine(db)
    engine.reserve_for_sales_order(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=4,
        sales_order_id=202,
        note="Reserve",
        request_meta=tenant_context.request_meta,
    )

    engine.deduct_for_sales_order_delivery(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=4,
        sales_order_id=202,
        note="Deliver",
        request_meta=tenant_context.request_meta,
    )

    stock = _get_stock(db, tenant_context)
    assert stock.quantity == 36
    assert stock.reserved_quantity == 0
    assert stock.available_quantity == 36


def test_cancel_releases_reserved_quantity(db, tenant_context):
    engine = InventoryEngine(db)
    engine.reserve_for_sales_order(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=5,
        sales_order_id=203,
        note="Reserve",
        request_meta=tenant_context.request_meta,
    )

    engine.release_sales_order_reservation(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=5,
        sales_order_id=203,
        note="Cancel",
        request_meta=tenant_context.request_meta,
    )

    stock = _get_stock(db, tenant_context)
    assert stock.quantity == 40
    assert stock.reserved_quantity == 0
    assert stock.available_quantity == 40


def test_transfer_creates_matching_out_and_in_movements(db, tenant_context):
    engine = InventoryEngine(db)

    out_tx, in_tx = engine.transfer_stock(
        current_user=tenant_context.user,
        product=tenant_context.product,
        source_warehouse=tenant_context.warehouse_primary,
        destination_warehouse=tenant_context.warehouse_secondary,
        quantity=8,
        stock_transfer_id=301,
        note="Move stock",
        request_meta=tenant_context.request_meta,
    )

    source_stock = _get_stock(db, tenant_context)
    destination_stock = db.scalar(
        select(WarehouseStock).where(
            WarehouseStock.tenant_id == tenant_context.tenant.id,
            WarehouseStock.product_id == tenant_context.product.id,
            WarehouseStock.warehouse_id == tenant_context.warehouse_secondary.id,
        )
    )

    assert out_tx.transaction_type == InventoryTransactionTypeEnum.TRANSFER_OUT
    assert in_tx.transaction_type == InventoryTransactionTypeEnum.TRANSFER_IN
    assert source_stock.quantity == 32
    assert source_stock.available_quantity == 32
    assert destination_stock.quantity == 8
    assert destination_stock.available_quantity == 8


def test_negative_stock_is_blocked(db, tenant_context):
    engine = InventoryEngine(db)

    with pytest.raises(HTTPException) as exc:
        engine.stock_out(
            current_user=tenant_context.user,
            product=tenant_context.product,
            warehouse=tenant_context.warehouse_primary,
            quantity=99,
            note="Too much",
            reference_type="manual",
            reference_id=401,
            request_meta=tenant_context.request_meta,
        )

    assert exc.value.status_code == 400
    assert "Negative stock" in exc.value.detail


def test_reserved_greater_than_quantity_is_blocked(db, tenant_context):
    engine = InventoryEngine(db)
    engine.reserve_for_sales_order(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=10,
        sales_order_id=501,
        note="Reserve",
        request_meta=tenant_context.request_meta,
    )

    with pytest.raises(HTTPException) as exc:
        engine.stock_out(
            current_user=tenant_context.user,
            product=tenant_context.product,
            warehouse=tenant_context.warehouse_primary,
            quantity=35,
            note="Would break reservation",
            reference_type="manual",
            reference_id=502,
            request_meta=tenant_context.request_meta,
        )

    assert exc.value.status_code == 400
    assert "Reserved quantity cannot exceed stock quantity" in exc.value.detail


def test_available_quantity_is_always_recomputed(db, tenant_context):
    engine = InventoryEngine(db)

    engine.reserve_for_sales_order(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=3,
        sales_order_id=601,
        note="Reserve",
        request_meta=tenant_context.request_meta,
    )
    stock = _get_stock(db, tenant_context)
    assert stock.available_quantity == stock.quantity - stock.reserved_quantity

    engine.adjust(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        signed_qty=2,
        note="Count correction",
        reference_type="adjustment",
        reference_id=602,
        request_meta=tenant_context.request_meta,
    )
    stock = _get_stock(db, tenant_context)
    assert stock.available_quantity == stock.quantity - stock.reserved_quantity


def test_duplicate_reference_is_idempotent(db, tenant_context):
    engine = InventoryEngine(db)

    first = engine.stock_in(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=4,
        note="Retry-safe stock in",
        reference_type="manual",
        reference_id=701,
        request_meta=tenant_context.request_meta,
    )
    second = engine.stock_in(
        current_user=tenant_context.user,
        product=tenant_context.product,
        warehouse=tenant_context.warehouse_primary,
        quantity=4,
        note="Retry-safe stock in",
        reference_type="manual",
        reference_id=701,
        request_meta=tenant_context.request_meta,
    )

    stock = _get_stock(db, tenant_context)
    tx_count = db.scalar(
        select(func.count(InventoryTransaction.id)).where(
            InventoryTransaction.tenant_id == tenant_context.tenant.id,
            InventoryTransaction.product_id == tenant_context.product.id,
            InventoryTransaction.warehouse_id == tenant_context.warehouse_primary.id,
            InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.STOCK_IN,
            InventoryTransaction.reference_type == "manual",
            InventoryTransaction.reference_id == 701,
        )
    )

    assert first.id == second.id
    assert tx_count == 1
    assert stock.quantity == 44
