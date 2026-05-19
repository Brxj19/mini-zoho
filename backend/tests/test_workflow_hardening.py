from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy import select

from app.models.category import Category
from app.models.brand import Brand
from app.models.customer import Customer
from app.models.enums import InventoryTransactionTypeEnum
from app.models.enums import PurchaseOrderStatusEnum
from app.models.enums import SalesOrderStatusEnum
from app.models.enums import StockTransferStatusEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder
from app.models.vendor import Vendor
from app.models.warehouse_stock import WarehouseStock
from app.schemas.purchase_order import PurchaseOrderCreate
from app.schemas.purchase_order import PurchaseOrderItemInput
from app.schemas.purchase_order import PurchaseOrderReceiveItemInput
from app.schemas.purchase_order import PurchaseOrderReceiveRequest
from app.schemas.sales_order import SalesOrderCreate
from app.schemas.sales_order import SalesOrderItemInput
from app.schemas.sales_order import SalesOrderStatusAction
from app.schemas.stock_transfer import StockTransferCreate
from app.schemas.stock_transfer import StockTransferItemInput
from app.services.master_data_service import MasterDataService
from app.services.purchase_order_service import PurchaseOrderService
from app.services.sales_order_service import SalesOrderService
from app.services.stock_transfer_service import StockTransferService


@pytest.mark.parametrize(
    ("entity_name", "model", "entity_attr", "dependencies"),
    [
        ("Category", Category, "category", ((Product, "category_id", "products"),)),
        ("Brand", Brand, "brand", ((Product, "brand_id", "products"),)),
        ("Vendor", Vendor, "vendor", ((Product, "vendor_id", "products"), (PurchaseOrder, "vendor_id", "purchase orders"))),
        ("Customer", Customer, "customer", ((SalesOrder, "customer_id", "sales orders"),)),
    ],
)
def test_archive_restrictions_block_linked_master_data(db, tenant_context, entity_name, model, entity_attr, dependencies):
    if model is PurchaseOrder or entity_attr == "vendor":
        purchase_order = PurchaseOrder(
            tenant_id=tenant_context.tenant.id,
            vendor_id=tenant_context.vendor.id,
            po_number="PO-LINKED-1",
            order_date=tenant_context.order_date,
            status=PurchaseOrderStatusEnum.DRAFT,
            subtotal=Decimal("100.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
            created_by=tenant_context.user.id,
        )
        db.add(purchase_order)
    if entity_attr == "customer":
        sales_order = SalesOrder(
            tenant_id=tenant_context.tenant.id,
            customer_id=tenant_context.customer.id,
            so_number="SO-LINKED-1",
            order_date=tenant_context.order_date,
            status=SalesOrderStatusEnum.DRAFT,
            subtotal=Decimal("100.00"),
            tax_amount=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
            created_by=tenant_context.user.id,
        )
        db.add(sales_order)
    db.commit()

    service = MasterDataService(
        db,
        model=model,
        entity_name=entity_name,
        search_columns=[getattr(model, "name")],
        unique_fields=("name",),
        archive_dependencies=dependencies,
    )

    with pytest.raises(HTTPException) as exc:
        service.archive_entity(current_user=tenant_context.user, entity_id=getattr(tenant_context, entity_attr).id)

    assert exc.value.status_code == 409
    assert "cannot be archived" in exc.value.detail


def test_purchase_order_partial_and_full_receive_updates_stock_and_transactions(db, tenant_context):
    service = PurchaseOrderService(db)
    payload = PurchaseOrderCreate(
        vendor_id=tenant_context.vendor.id,
        po_number="PO-2026-101",
        order_date=tenant_context.order_date,
        notes="Inbound replenishment",
        items=[
            PurchaseOrderItemInput(
                product_id=tenant_context.product.id,
                warehouse_id=tenant_context.warehouse_primary.id,
                quantity_ordered=5,
                unit_price=Decimal("70.00"),
                tax_rate=Decimal("0.00"),
            )
        ],
    )

    purchase_order, items = service.create_purchase_order(current_user=tenant_context.user, payload=payload)
    purchase_order, items = service.issue_purchase_order(current_user=tenant_context.user, purchase_order_id=purchase_order.id)

    partial_receive = PurchaseOrderReceiveRequest(
        notes="First truck arrived",
        items=[PurchaseOrderReceiveItemInput(purchase_order_item_id=items[0].id, quantity_received=2)],
    )
    purchase_order, items = service.receive_purchase_order(
        current_user=tenant_context.user,
        purchase_order_id=purchase_order.id,
        payload=partial_receive,
        request_meta=tenant_context.request_meta,
    )

    stock = db.scalar(
        select(WarehouseStock).where(
            WarehouseStock.tenant_id == tenant_context.tenant.id,
            WarehouseStock.warehouse_id == tenant_context.warehouse_primary.id,
            WarehouseStock.product_id == tenant_context.product.id,
        )
    )
    assert purchase_order.status == PurchaseOrderStatusEnum.PARTIALLY_RECEIVED
    assert items[0].quantity_received == 2
    assert stock.quantity == 42
    assert stock.available_quantity == 42

    final_receive = PurchaseOrderReceiveRequest(
        notes="Balance stock received",
        items=[PurchaseOrderReceiveItemInput(purchase_order_item_id=items[0].id, quantity_received=3)],
    )
    purchase_order, items = service.receive_purchase_order(
        current_user=tenant_context.user,
        purchase_order_id=purchase_order.id,
        payload=final_receive,
        request_meta=tenant_context.request_meta,
    )

    stock = db.scalar(
        select(WarehouseStock).where(
            WarehouseStock.tenant_id == tenant_context.tenant.id,
            WarehouseStock.warehouse_id == tenant_context.warehouse_primary.id,
            WarehouseStock.product_id == tenant_context.product.id,
        )
    )
    receive_count = db.scalar(
        select(func.count(InventoryTransaction.id)).where(
            InventoryTransaction.reference_type == "purchase_order",
            InventoryTransaction.reference_id == purchase_order.id,
            InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.PURCHASE_RECEIVE,
        )
    )

    assert purchase_order.status == PurchaseOrderStatusEnum.RECEIVED
    assert items[0].quantity_received == 5
    assert stock.quantity == 45
    assert stock.available_quantity == 45
    assert receive_count == 2


def test_sales_order_confirm_cancel_and_delivery_adjust_stock_correctly(db, tenant_context):
    service = SalesOrderService(db)
    payload = SalesOrderCreate(
        customer_id=tenant_context.customer.id,
        so_number="SO-2026-451",
        order_date=tenant_context.order_date,
        notes="Retail dispatch order",
        items=[
            SalesOrderItemInput(
                product_id=tenant_context.product.id,
                warehouse_id=tenant_context.warehouse_primary.id,
                quantity=4,
                unit_price=Decimal("119.00"),
                tax_rate=Decimal("0.00"),
                discount=Decimal("0.00"),
            )
        ],
    )

    sales_order, _items = service.create_sales_order(current_user=tenant_context.user, payload=payload)
    sales_order, items = service.confirm_sales_order(
        current_user=tenant_context.user,
        sales_order_id=sales_order.id,
        notes="Reserve stock",
        request_meta=tenant_context.request_meta,
    )

    stock = db.scalar(
        select(WarehouseStock).where(
            WarehouseStock.tenant_id == tenant_context.tenant.id,
            WarehouseStock.warehouse_id == tenant_context.warehouse_primary.id,
            WarehouseStock.product_id == tenant_context.product.id,
        )
    )
    assert sales_order.status == SalesOrderStatusEnum.CONFIRMED
    assert stock.quantity == 40
    assert stock.reserved_quantity == 4
    assert stock.available_quantity == 36

    sales_order, items = service.cancel_sales_order(
        current_user=tenant_context.user,
        sales_order_id=sales_order.id,
        notes="Customer changed mind",
        request_meta=tenant_context.request_meta,
    )
    stock = db.scalar(
        select(WarehouseStock).where(
            WarehouseStock.tenant_id == tenant_context.tenant.id,
            WarehouseStock.warehouse_id == tenant_context.warehouse_primary.id,
            WarehouseStock.product_id == tenant_context.product.id,
        )
    )
    cancel_release_count = db.scalar(
        select(func.count(InventoryTransaction.id)).where(
            InventoryTransaction.reference_type == "sales_order",
            InventoryTransaction.reference_id == sales_order.id,
            InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.SALES_ORDER_CANCEL_RELEASE,
        )
    )

    assert sales_order.status == SalesOrderStatusEnum.CANCELLED
    assert stock.quantity == 40
    assert stock.reserved_quantity == 0
    assert stock.available_quantity == 40
    assert cancel_release_count == 1

    second_payload = SalesOrderCreate(
        customer_id=tenant_context.customer.id,
        so_number="SO-2026-452",
        order_date=tenant_context.order_date,
        notes="Delivery flow validation",
        items=[
            SalesOrderItemInput(
                product_id=tenant_context.product.id,
                warehouse_id=tenant_context.warehouse_primary.id,
                quantity=6,
                unit_price=Decimal("119.00"),
                tax_rate=Decimal("0.00"),
                discount=Decimal("0.00"),
            )
        ],
    )
    deliver_order, _ = service.create_sales_order(current_user=tenant_context.user, payload=second_payload)
    deliver_order, _ = service.confirm_sales_order(
        current_user=tenant_context.user,
        sales_order_id=deliver_order.id,
        notes="Reserve for delivery",
        request_meta=tenant_context.request_meta,
    )
    deliver_order, _ = service.mark_packed(current_user=tenant_context.user, sales_order_id=deliver_order.id)
    deliver_order, _ = service.mark_shipped(current_user=tenant_context.user, sales_order_id=deliver_order.id)
    deliver_order, _ = service.mark_delivered(
        current_user=tenant_context.user,
        sales_order_id=deliver_order.id,
        notes="Delivered to customer",
        request_meta=tenant_context.request_meta,
    )

    stock = db.scalar(
        select(WarehouseStock).where(
            WarehouseStock.tenant_id == tenant_context.tenant.id,
            WarehouseStock.warehouse_id == tenant_context.warehouse_primary.id,
            WarehouseStock.product_id == tenant_context.product.id,
        )
    )
    deduct_count = db.scalar(
        select(func.count(InventoryTransaction.id)).where(
            InventoryTransaction.reference_type == "sales_order",
            InventoryTransaction.reference_id == deliver_order.id,
            InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.SALES_ORDER_DEDUCT,
        )
    )

    assert deliver_order.status == SalesOrderStatusEnum.DELIVERED
    assert stock.quantity == 34
    assert stock.reserved_quantity == 0
    assert stock.available_quantity == 34
    assert deduct_count == 1


def test_stock_transfer_completion_moves_inventory_between_warehouses(db, tenant_context):
    service = StockTransferService(db)
    payload = StockTransferCreate(
        source_warehouse_id=tenant_context.warehouse_primary.id,
        destination_warehouse_id=tenant_context.warehouse_secondary.id,
        notes="Move inventory to overflow site",
        items=[StockTransferItemInput(product_id=tenant_context.product.id, quantity=7)],
    )

    transfer, _ = service.create_transfer(current_user=tenant_context.user, payload=payload)
    transfer, _ = service.mark_in_transit(current_user=tenant_context.user, transfer_id=transfer.id, notes="Truck dispatched")
    transfer, _ = service.complete_transfer(
        current_user=tenant_context.user,
        transfer_id=transfer.id,
        notes="Truck delivered",
        request_meta=tenant_context.request_meta,
    )

    source_stock = db.scalar(
        select(WarehouseStock).where(
            WarehouseStock.tenant_id == tenant_context.tenant.id,
            WarehouseStock.warehouse_id == tenant_context.warehouse_primary.id,
            WarehouseStock.product_id == tenant_context.product.id,
        )
    )
    destination_stock = db.scalar(
        select(WarehouseStock).where(
            WarehouseStock.tenant_id == tenant_context.tenant.id,
            WarehouseStock.warehouse_id == tenant_context.warehouse_secondary.id,
            WarehouseStock.product_id == tenant_context.product.id,
        )
    )
    transfer_out_count = db.scalar(
        select(func.count(InventoryTransaction.id)).where(
            InventoryTransaction.reference_type == "stock_transfer",
            InventoryTransaction.reference_id == transfer.id,
            InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.TRANSFER_OUT,
        )
    )
    transfer_in_count = db.scalar(
        select(func.count(InventoryTransaction.id)).where(
            InventoryTransaction.reference_type == "stock_transfer",
            InventoryTransaction.reference_id == transfer.id,
            InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.TRANSFER_IN,
        )
    )

    assert transfer.status == StockTransferStatusEnum.COMPLETED
    assert source_stock.quantity == 33
    assert source_stock.available_quantity == 33
    assert destination_stock.quantity == 7
    assert destination_stock.available_quantity == 7
    assert transfer_out_count == 1
    assert transfer_in_count == 1
