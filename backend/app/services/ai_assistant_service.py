from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.enums import InventoryTransactionTypeEnum
from app.models.enums import PurchaseOrderStatusEnum
from app.models.enums import RoleEnum
from app.models.enums import SalesOrderStatusEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.notification import Notification
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.schemas.ai import AIAssistantFact
from app.schemas.ai import IntegrationCatalogItem
from app.schemas.ai import ReorderSuggestionResponse


class AIAssistantService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ask(self, *, current_user: User, question: str, tenant_id: int | None = None) -> tuple[str, list[AIAssistantFact]]:
        scoped_tenant_id = self._resolve_tenant_id(current_user=current_user, tenant_id=tenant_id)
        snapshot = self._snapshot(scoped_tenant_id)
        suggestions = self.get_reorder_suggestions(current_user=current_user, tenant_id=scoped_tenant_id, limit=5)
        lowered = question.lower()

        facts = [
            AIAssistantFact(label="Active items", value=snapshot["total_products"]),
            AIAssistantFact(label="Warehouses", value=snapshot["total_warehouses"]),
            AIAssistantFact(label="Low-stock records", value=snapshot["low_stock_count"]),
            AIAssistantFact(label="Open sales orders", value=snapshot["open_sales_orders"]),
            AIAssistantFact(label="Open purchase orders", value=snapshot["open_purchase_orders"]),
            AIAssistantFact(label="Unread notifications", value=snapshot["unread_notifications"]),
        ]

        if snapshot["total_products"] == 0:
            return "No product data is available for this tenant yet, so I cannot generate operational insights right now.", facts

        if "reorder" in lowered or "low stock" in lowered:
            if not suggestions:
                return "There are no current reorder suggestions because no low-stock items were found from live tenant data.", facts
            top = suggestions[0]
            return (
                f"{len(suggestions)} reorder suggestion(s) are currently open. The highest-priority item is {top.product_name} in {top.warehouse_name}, "
                f"with {top.available_quantity} on hand against a reorder level of {top.reorder_level}. Recommended reorder quantity: {top.recommended_quantity}.",
                facts,
            )

        if "sales" in lowered:
            return (
                f"There are {snapshot['open_sales_orders']} open sales orders in progress. {snapshot['packed_sales_orders']} are packed or shipped, "
                f"and the last 30 days recorded {snapshot['last_30d_sales_deduct_qty']} unit(s) deducted through delivered sales orders.",
                facts,
            )

        if "purchase" in lowered or "vendor" in lowered:
            return (
                f"There are {snapshot['open_purchase_orders']} open purchase orders awaiting receipt, including {snapshot['partially_received_purchase_orders']} partially received order(s). "
                f"Current low-stock pressure exists on {snapshot['low_stock_count']} warehouse item positions.",
                facts,
            )

        return (
            f"Current tenant snapshot: {snapshot['total_products']} active item(s) across {snapshot['total_warehouses']} warehouse(s), "
            f"{snapshot['open_sales_orders']} open sales order(s), {snapshot['open_purchase_orders']} open purchase order(s), and "
            f"{snapshot['low_stock_count']} low-stock warehouse record(s). "
            + (
                f"The top reorder candidate is {suggestions[0].product_name} with a recommended buy quantity of {suggestions[0].recommended_quantity}."
                if suggestions
                else "There are no immediate reorder candidates right now."
            ),
            facts,
        )

    def get_reorder_suggestions(
        self,
        *,
        current_user: User,
        tenant_id: int | None = None,
        limit: int = 20,
    ) -> list[ReorderSuggestionResponse]:
        scoped_tenant_id = self._resolve_tenant_id(current_user=current_user, tenant_id=tenant_id)
        demand_since = datetime.now(timezone.utc) - timedelta(days=30)

        low_stock_rows = self.db.execute(
            select(
                WarehouseStock.product_id,
                Product.name,
                Product.sku,
                WarehouseStock.warehouse_id,
                Warehouse.name,
                WarehouseStock.available_quantity,
                WarehouseStock.reorder_level,
            )
            .join(Product, Product.id == WarehouseStock.product_id)
            .join(Warehouse, Warehouse.id == WarehouseStock.warehouse_id)
            .where(
                WarehouseStock.tenant_id == scoped_tenant_id,
                WarehouseStock.available_quantity <= WarehouseStock.reorder_level,
            )
            .order_by(WarehouseStock.available_quantity.asc(), Product.name.asc())
        ).all()

        if not low_stock_rows:
            return []

        demand_rows = self.db.execute(
            select(
                InventoryTransaction.product_id,
                InventoryTransaction.warehouse_id,
                func.coalesce(func.sum(InventoryTransaction.quantity), 0),
            )
            .where(
                InventoryTransaction.tenant_id == scoped_tenant_id,
                InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.SALES_ORDER_DEDUCT,
                InventoryTransaction.created_at >= demand_since,
            )
            .group_by(InventoryTransaction.product_id, InventoryTransaction.warehouse_id)
        ).all()
        demand_map = {(product_id, warehouse_id): int(quantity or 0) for product_id, warehouse_id, quantity in demand_rows}

        suggestions: list[ReorderSuggestionResponse] = []
        for row in low_stock_rows[:limit]:
            reorder_level = int(row[6] or 0)
            available_quantity = int(row[5] or 0)
            demand_30d = demand_map.get((row[0], row[3]), 0)
            recommended_quantity = max((reorder_level * 2) - available_quantity, demand_30d - available_quantity, reorder_level - available_quantity, 0)
            if recommended_quantity <= 0:
                recommended_quantity = max(reorder_level - available_quantity, 1)
            suggestions.append(
                ReorderSuggestionResponse(
                    product_id=row[0],
                    product_name=row[1],
                    sku=row[2],
                    warehouse_id=row[3],
                    warehouse_name=row[4],
                    available_quantity=available_quantity,
                    reorder_level=reorder_level,
                    last_30d_demand=demand_30d,
                    recommended_quantity=recommended_quantity,
                    reason=(
                        f"Available quantity is {available_quantity} against reorder level {reorder_level}, "
                        f"with {demand_30d} unit(s) deducted in the last 30 days."
                    ),
                )
            )
        return suggestions

    def summarize_report(self, *, current_user: User, report_key: str, tenant_id: int | None = None) -> str:
        scoped_tenant_id = self._resolve_tenant_id(current_user=current_user, tenant_id=tenant_id)
        report_key = report_key.strip().lower()
        if report_key == "low-stock":
            count = self.db.scalar(
                select(func.count(WarehouseStock.id)).where(
                    WarehouseStock.tenant_id == scoped_tenant_id,
                    WarehouseStock.available_quantity <= WarehouseStock.reorder_level,
                )
            ) or 0
            return f"Low-stock report placeholder: the current tenant has {count} low-stock warehouse record(s)."
        if report_key == "inventory-summary":
            count = self.db.scalar(select(func.count(Product.id)).where(Product.tenant_id == scoped_tenant_id)) or 0
            return f"Inventory summary placeholder: the current tenant has {count} product record(s) in scope."
        if report_key == "sales-orders":
            count = self.db.scalar(select(func.count(SalesOrder.id)).where(SalesOrder.tenant_id == scoped_tenant_id)) or 0
            return f"Sales-order report placeholder: the current tenant has {count} sales order record(s) available for summarization."
        return "This report summary placeholder is available, but there is no specialized summary template for the requested report key yet."

    def integration_catalog(self, *, current_user: User, tenant_id: int | None = None) -> list[IntegrationCatalogItem]:
        self._resolve_tenant_id(current_user=current_user, tenant_id=tenant_id)
        return [
            IntegrationCatalogItem(
                key="shipping",
                name="Shipping Partners",
                category="Logistics",
                status="PLANNED",
                configured=False,
                description="Courier and shipment label integrations are planned but not connected yet.",
            ),
            IntegrationCatalogItem(
                key="payments",
                name="Payment Collection",
                category="Finance",
                status="PLANNED",
                configured=False,
                description="Online payment collection and settlement integrations are reserved for a later rollout.",
            ),
            IntegrationCatalogItem(
                key="marketplaces",
                name="Marketplace Sync",
                category="Commerce",
                status="PLANNED",
                configured=False,
                description="Marketplace catalog and order sync placeholders are ready for future channel integrations.",
            ),
        ]

    def _snapshot(self, tenant_id: int) -> dict[str, int]:
        demand_since = datetime.now(timezone.utc) - timedelta(days=30)
        return {
            "total_products": self.db.scalar(select(func.count(Product.id)).where(Product.tenant_id == tenant_id)) or 0,
            "total_warehouses": self.db.scalar(select(func.count(Warehouse.id)).where(Warehouse.tenant_id == tenant_id)) or 0,
            "low_stock_count": self.db.scalar(
                select(func.count(WarehouseStock.id)).where(
                    WarehouseStock.tenant_id == tenant_id,
                    WarehouseStock.available_quantity <= WarehouseStock.reorder_level,
                )
            ) or 0,
            "open_sales_orders": self.db.scalar(
                select(func.count(SalesOrder.id)).where(
                    SalesOrder.tenant_id == tenant_id,
                    SalesOrder.status.in_([SalesOrderStatusEnum.CONFIRMED, SalesOrderStatusEnum.PACKED, SalesOrderStatusEnum.SHIPPED]),
                )
            ) or 0,
            "packed_sales_orders": self.db.scalar(
                select(func.count(SalesOrder.id)).where(
                    SalesOrder.tenant_id == tenant_id,
                    SalesOrder.status.in_([SalesOrderStatusEnum.PACKED, SalesOrderStatusEnum.SHIPPED]),
                )
            ) or 0,
            "open_purchase_orders": self.db.scalar(
                select(func.count(PurchaseOrder.id)).where(
                    PurchaseOrder.tenant_id == tenant_id,
                    PurchaseOrder.status.in_([PurchaseOrderStatusEnum.ISSUED, PurchaseOrderStatusEnum.PARTIALLY_RECEIVED]),
                )
            ) or 0,
            "partially_received_purchase_orders": self.db.scalar(
                select(func.count(PurchaseOrder.id)).where(
                    PurchaseOrder.tenant_id == tenant_id,
                    PurchaseOrder.status == PurchaseOrderStatusEnum.PARTIALLY_RECEIVED,
                )
            ) or 0,
            "unread_notifications": self.db.scalar(
                select(func.count(Notification.id)).where(Notification.tenant_id == tenant_id, Notification.is_read.is_(False))
            ) or 0,
            "last_30d_sales_deduct_qty": self.db.scalar(
                select(func.coalesce(func.sum(InventoryTransaction.quantity), 0)).where(
                    InventoryTransaction.tenant_id == tenant_id,
                    InventoryTransaction.transaction_type == InventoryTransactionTypeEnum.SALES_ORDER_DEDUCT,
                    InventoryTransaction.created_at >= demand_since,
                )
            ) or 0,
        }

    @staticmethod
    def _resolve_tenant_id(*, current_user: User, tenant_id: int | None = None) -> int:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=current_user.role == RoleEnum.SUPER_ADMIN)
        if scoped_tenant_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A tenant context is required for the AI workspace.")
        return scoped_tenant_id
