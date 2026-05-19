from __future__ import annotations

from app.models.enums import PurchaseOrderStatusEnum
from app.models.enums import SalesOrderStatusEnum
from app.models.enums import SalesReturnStatusEnum
from app.schemas.business_workflow import PurchaseReceiveCreate
from app.schemas.business_workflow import PurchaseReceiveItemInput
from app.schemas.business_workflow import SalesReturnCreate
from app.schemas.business_workflow import SalesReturnItemInput
from app.schemas.purchase_order import PurchaseOrderCreate
from app.schemas.purchase_order import PurchaseOrderItemInput
from app.schemas.sales_order import SalesOrderCreate
from app.schemas.sales_order import SalesOrderItemInput
from app.services.business_workflow_service import BusinessWorkflowService
from app.services.purchase_order_service import PurchaseOrderService
from app.services.sales_order_service import SalesOrderService


def test_purchase_receive_creates_first_class_receipt_and_updates_stock(db, tenant_context):
    po_service = PurchaseOrderService(db)
    purchase_order, items = po_service.create_purchase_order(
        current_user=tenant_context.user,
        payload=PurchaseOrderCreate(
            vendor_id=tenant_context.vendor.id,
            po_number="PO-WF-001",
            order_date=tenant_context.order_date,
            expected_delivery_date=tenant_context.order_date,
            notes="Inbound load",
            items=[
                PurchaseOrderItemInput(
                    product_id=tenant_context.product.id,
                    warehouse_id=tenant_context.warehouse_primary.id,
                    quantity_ordered=5,
                    unit_price="70.00",
                    tax_rate="0.00",
                )
            ],
        ),
    )
    po_service.issue_purchase_order(current_user=tenant_context.user, purchase_order_id=purchase_order.id, notes="Issued")

    receipt, receipt_items = BusinessWorkflowService(db).create_purchase_receive(
        current_user=tenant_context.user,
        payload=PurchaseReceiveCreate(
            purchase_order_id=purchase_order.id,
            receive_number="PR-001",
            received_at=tenant_context.order_date,
            notes="Received all",
            items=[PurchaseReceiveItemInput(purchase_order_item_id=items[0].id, quantity_received=5)],
        ),
        request_meta=tenant_context.request_meta,
    )

    refreshed_po, refreshed_items = po_service.get_purchase_order_for_user(current_user=tenant_context.user, purchase_order_id=purchase_order.id)
    db.refresh(tenant_context.stock)

    assert receipt.receive_number == "PR-001"
    assert len(receipt_items) == 1
    assert tenant_context.stock.quantity == 45
    assert refreshed_po.status == PurchaseOrderStatusEnum.RECEIVED
    assert refreshed_items[0].quantity_received == 5


def test_sales_return_receive_restocks_inventory(db, tenant_context):
    sales_service = SalesOrderService(db)
    sales_order, sales_items = sales_service.create_sales_order(
        current_user=tenant_context.user,
        payload=SalesOrderCreate(
            customer_id=tenant_context.customer.id,
            so_number="SO-WF-001",
            order_date=tenant_context.order_date,
            notes="Delivered order",
            items=[
                SalesOrderItemInput(
                    product_id=tenant_context.product.id,
                    warehouse_id=tenant_context.warehouse_primary.id,
                    quantity=2,
                    unit_price="119.00",
                    tax_rate="0.00",
                    discount="0.00",
                )
            ],
        ),
    )
    sales_service.confirm_sales_order(
        current_user=tenant_context.user,
        sales_order_id=sales_order.id,
        notes="Confirmed",
        request_meta=tenant_context.request_meta,
    )
    sales_service.mark_packed(current_user=tenant_context.user, sales_order_id=sales_order.id, notes="Packed")
    sales_service.mark_shipped(current_user=tenant_context.user, sales_order_id=sales_order.id, notes="Shipped")
    sales_service.mark_delivered(
        current_user=tenant_context.user,
        sales_order_id=sales_order.id,
        notes="Delivered",
        request_meta=tenant_context.request_meta,
    )

    sales_return, _ = BusinessWorkflowService(db).create_sales_return(
        current_user=tenant_context.user,
        payload=SalesReturnCreate(
            sales_order_id=sales_order.id,
            return_number="SR-001",
            return_date=tenant_context.order_date,
            notes="Customer return",
            items=[
                SalesReturnItemInput(
                    sales_order_item_id=sales_items[0].id,
                    warehouse_id=tenant_context.warehouse_primary.id,
                    quantity=1,
                    reason="Damaged in transit",
                    notes="Outer box dented",
                )
            ],
        ),
    )

    received_return, _ = BusinessWorkflowService(db).receive_sales_return(
        current_user=tenant_context.user,
        sales_return_id=sales_return.id,
        notes="Received back",
        request_meta=tenant_context.request_meta,
    )
    refreshed_order, _ = sales_service.get_sales_order_for_user(current_user=tenant_context.user, sales_order_id=sales_order.id)
    db.refresh(tenant_context.stock)

    assert refreshed_order.status == SalesOrderStatusEnum.DELIVERED
    assert received_return.status == SalesReturnStatusEnum.RECEIVED
    assert tenant_context.stock.quantity == 39
