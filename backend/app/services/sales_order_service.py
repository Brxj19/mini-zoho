from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.models.enums import InventoryTransactionTypeEnum, RecordStatusEnum, RoleEnum, SalesOrderStatusEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.inventory_repository import InventoryTransactionRepository, WarehouseStockRepository
from app.repositories.master_data_repository import MasterDataRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sales_order_repository import SalesOrderItemRepository, SalesOrderRepository
from app.repositories.tenant_repository import TenantRepository


class SalesOrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sales_order_repository = SalesOrderRepository(db)
        self.item_repository = SalesOrderItemRepository(db)
        self.product_repository = ProductRepository(db)
        self.stock_repository = WarehouseStockRepository(db)
        self.transaction_repository = InventoryTransactionRepository(db)
        self.audit_repository = AuditLogRepository(db)
        self.tenant_repository = TenantRepository(db)
        self.customer_repository = MasterDataRepository(db, Customer)
        self.warehouse_repository = MasterDataRepository(db, Warehouse)

    def list_sales_orders(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        status_filter: SalesOrderStatusEnum | None = None,
        customer_id: int | None = None,
        date_from=None,
        date_to=None,
        search: str | None = None,
    ) -> tuple[list[SalesOrder], int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.sales_order_repository.list(
            page=page,
            page_size=page_size,
            tenant_id=scoped_tenant_id,
            status_filter=status_filter,
            customer_id=customer_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )

    def get_sales_order_for_user(self, *, current_user: User, sales_order_id: int) -> tuple[SalesOrder, list[SalesOrderItem]]:
        sales_order = self.sales_order_repository.get_by_id(sales_order_id)
        if not sales_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found.")
        if current_user.role != RoleEnum.SUPER_ADMIN and sales_order.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-tenant access is not allowed.")
        items = self.item_repository.list_by_sales_order(sales_order.id)
        return sales_order, items

    def create_sales_order(self, *, current_user: User, payload, tenant_id: int | None = None) -> tuple[SalesOrder, list[SalesOrderItem]]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        self._validate_tenant_exists(scoped_tenant_id)
        self._ensure_unique_so_number(tenant_id=scoped_tenant_id, so_number=payload.so_number)
        self._validate_customer(tenant_id=scoped_tenant_id, customer_id=payload.customer_id)
        items_data = self._validate_items(tenant_id=scoped_tenant_id, items=payload.items)
        totals = self._build_order_totals(items_data)

        sales_order = self.sales_order_repository.create(
            SalesOrder(
                tenant_id=scoped_tenant_id,
                customer_id=payload.customer_id,
                so_number=payload.so_number,
                order_date=payload.order_date,
                status=SalesOrderStatusEnum.DRAFT,
                subtotal=totals["subtotal"],
                tax_amount=totals["tax_amount"],
                discount_amount=totals["discount_amount"],
                total_amount=totals["total_amount"],
                notes=payload.notes,
                created_by=current_user.id,
            )
        )
        items = self.item_repository.create_many(
            [
                SalesOrderItem(
                    sales_order_id=sales_order.id,
                    product_id=item["product_id"],
                    warehouse_id=item["warehouse_id"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    tax_rate=item["tax_rate"],
                    discount=item["discount"],
                    total_price=item["total_price"],
                )
                for item in items_data
            ]
        )
        self._log_sales_order_action(
            actor=current_user,
            sales_order=sales_order,
            action="sales_order.created",
            old_value=None,
            new_value=self._sales_order_snapshot(sales_order, items),
        )
        self.db.commit()
        return sales_order, items

    def update_sales_order(self, *, current_user: User, sales_order_id: int, payload) -> tuple[SalesOrder, list[SalesOrderItem]]:
        sales_order, current_items = self.get_sales_order_for_user(current_user=current_user, sales_order_id=sales_order_id)
        if sales_order.status != SalesOrderStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft sales orders can be updated.")

        updates = payload.model_dump(exclude_unset=True)
        old_snapshot = self._sales_order_snapshot(sales_order, current_items)
        customer_id = updates.get("customer_id", sales_order.customer_id)
        so_number = updates.get("so_number", sales_order.so_number)

        self._validate_customer(tenant_id=sales_order.tenant_id, customer_id=customer_id)
        self._ensure_unique_so_number(tenant_id=sales_order.tenant_id, so_number=so_number, exclude_id=sales_order.id)

        if "items" in updates and updates["items"] is not None:
            items_data = self._validate_items(tenant_id=sales_order.tenant_id, items=updates["items"])
            totals = self._build_order_totals(items_data)
            self.item_repository.delete_for_sales_order(sales_order.id)
            current_items = self.item_repository.create_many(
                [
                    SalesOrderItem(
                        sales_order_id=sales_order.id,
                        product_id=item["product_id"],
                        warehouse_id=item["warehouse_id"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                        tax_rate=item["tax_rate"],
                        discount=item["discount"],
                        total_price=item["total_price"],
                    )
                    for item in items_data
                ]
            )
        else:
            totals = {
                "subtotal": sales_order.subtotal,
                "tax_amount": sales_order.tax_amount,
                "discount_amount": sales_order.discount_amount,
                "total_amount": sales_order.total_amount,
            }

        sales_order = self.sales_order_repository.update(
            sales_order,
            {
                "customer_id": customer_id,
                "so_number": so_number,
                "order_date": updates.get("order_date", sales_order.order_date),
                "notes": updates.get("notes", sales_order.notes),
                "subtotal": totals["subtotal"],
                "tax_amount": totals["tax_amount"],
                "discount_amount": totals["discount_amount"],
                "total_amount": totals["total_amount"],
            },
        )
        self._log_sales_order_action(
            actor=current_user,
            sales_order=sales_order,
            action="sales_order.updated",
            old_value=old_snapshot,
            new_value=self._sales_order_snapshot(sales_order, current_items),
        )
        self.db.commit()
        return sales_order, current_items

    def confirm_sales_order(
        self,
        *,
        current_user: User,
        sales_order_id: int,
        notes: str | None,
        request_meta: dict[str, str | None],
    ) -> tuple[SalesOrder, list[SalesOrderItem]]:
        sales_order, items = self.get_sales_order_for_user(current_user=current_user, sales_order_id=sales_order_id)
        if sales_order.status != SalesOrderStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft sales orders can be confirmed.")

        old_snapshot = self._sales_order_snapshot(sales_order, items)
        self._reserve_stock(tenant_id=sales_order.tenant_id, sales_order_id=sales_order.id, items=items, current_user=current_user, note=notes or sales_order.notes, request_meta=request_meta)
        sales_order = self.sales_order_repository.update(
            sales_order,
            {
                "status": SalesOrderStatusEnum.CONFIRMED,
                "notes": notes if notes is not None else sales_order.notes,
            },
        )
        self._log_sales_order_action(
            actor=current_user,
            sales_order=sales_order,
            action="sales_order.confirmed",
            old_value=old_snapshot,
            new_value=self._sales_order_snapshot(sales_order, items),
            request_meta=request_meta,
        )
        self.db.commit()
        return sales_order, items

    def mark_packed(self, *, current_user: User, sales_order_id: int, notes: str | None = None) -> tuple[SalesOrder, list[SalesOrderItem]]:
        return self._advance_status(
            current_user=current_user,
            sales_order_id=sales_order_id,
            expected_status=SalesOrderStatusEnum.CONFIRMED,
            next_status=SalesOrderStatusEnum.PACKED,
            action="sales_order.packed",
            notes=notes,
        )

    def mark_shipped(self, *, current_user: User, sales_order_id: int, notes: str | None = None) -> tuple[SalesOrder, list[SalesOrderItem]]:
        return self._advance_status(
            current_user=current_user,
            sales_order_id=sales_order_id,
            expected_status=SalesOrderStatusEnum.PACKED,
            next_status=SalesOrderStatusEnum.SHIPPED,
            action="sales_order.shipped",
            notes=notes,
        )

    def mark_delivered(
        self,
        *,
        current_user: User,
        sales_order_id: int,
        notes: str | None,
        request_meta: dict[str, str | None],
    ) -> tuple[SalesOrder, list[SalesOrderItem]]:
        sales_order, items = self.get_sales_order_for_user(current_user=current_user, sales_order_id=sales_order_id)
        if sales_order.status != SalesOrderStatusEnum.SHIPPED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only shipped sales orders can be marked as delivered.")

        old_snapshot = self._sales_order_snapshot(sales_order, items)
        self._deduct_reserved_stock(
            tenant_id=sales_order.tenant_id,
            sales_order_id=sales_order.id,
            items=items,
            current_user=current_user,
            note=notes or sales_order.notes,
            request_meta=request_meta,
        )
        sales_order = self.sales_order_repository.update(
            sales_order,
            {
                "status": SalesOrderStatusEnum.DELIVERED,
                "notes": notes if notes is not None else sales_order.notes,
            },
        )
        self._log_sales_order_action(
            actor=current_user,
            sales_order=sales_order,
            action="sales_order.delivered",
            old_value=old_snapshot,
            new_value=self._sales_order_snapshot(sales_order, items),
            request_meta=request_meta,
        )
        self.db.commit()
        return sales_order, items

    def cancel_sales_order(
        self,
        *,
        current_user: User,
        sales_order_id: int,
        notes: str | None,
        request_meta: dict[str, str | None],
    ) -> tuple[SalesOrder, list[SalesOrderItem]]:
        sales_order, items = self.get_sales_order_for_user(current_user=current_user, sales_order_id=sales_order_id)
        if sales_order.status == SalesOrderStatusEnum.DELIVERED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Delivered sales orders cannot be cancelled.")
        if sales_order.status == SalesOrderStatusEnum.CANCELLED:
            return sales_order, items

        old_snapshot = self._sales_order_snapshot(sales_order, items)
        if sales_order.status in {SalesOrderStatusEnum.CONFIRMED, SalesOrderStatusEnum.PACKED, SalesOrderStatusEnum.SHIPPED}:
            self._release_reserved_stock(
                tenant_id=sales_order.tenant_id,
                sales_order_id=sales_order.id,
                items=items,
                current_user=current_user,
                note=notes or sales_order.notes,
                request_meta=request_meta,
            )

        sales_order = self.sales_order_repository.update(
            sales_order,
            {
                "status": SalesOrderStatusEnum.CANCELLED,
                "notes": notes if notes is not None else sales_order.notes,
            },
        )
        self._log_sales_order_action(
            actor=current_user,
            sales_order=sales_order,
            action="sales_order.cancelled",
            old_value=old_snapshot,
            new_value=self._sales_order_snapshot(sales_order, items),
            request_meta=request_meta,
        )
        self.db.commit()
        return sales_order, items

    def _advance_status(
        self,
        *,
        current_user: User,
        sales_order_id: int,
        expected_status: SalesOrderStatusEnum,
        next_status: SalesOrderStatusEnum,
        action: str,
        notes: str | None,
    ) -> tuple[SalesOrder, list[SalesOrderItem]]:
        sales_order, items = self.get_sales_order_for_user(current_user=current_user, sales_order_id=sales_order_id)
        if sales_order.status != expected_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Sales order must be {expected_status.value} before moving to {next_status.value}.")

        old_snapshot = self._sales_order_snapshot(sales_order, items)
        sales_order = self.sales_order_repository.update(
            sales_order,
            {
                "status": next_status,
                "notes": notes if notes is not None else sales_order.notes,
            },
        )
        self._log_sales_order_action(
            actor=current_user,
            sales_order=sales_order,
            action=action,
            old_value=old_snapshot,
            new_value=self._sales_order_snapshot(sales_order, items),
        )
        self.db.commit()
        return sales_order, items

    def _validate_tenant_exists(self, tenant_id: int) -> None:
        if self.tenant_repository.get_by_id(tenant_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    def _ensure_unique_so_number(self, *, tenant_id: int, so_number: str, exclude_id: int | None = None) -> None:
        if self.sales_order_repository.find_by_number(tenant_id=tenant_id, so_number=so_number, exclude_id=exclude_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="so_number must be unique within the tenant.")

    def _validate_customer(self, *, tenant_id: int, customer_id: int) -> Customer:
        customer = self.customer_repository.get_by_id(customer_id)
        if not customer or customer.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found for this tenant.")
        if customer.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived customers cannot be used in sales orders.")
        return customer

    def _validate_items(self, *, tenant_id: int, items: list[Any]) -> list[dict[str, Any]]:
        validated_items: list[dict[str, Any]] = []
        seen_pairs: set[tuple[int, int]] = set()
        for item in items:
            product = self._get_active_product(tenant_id=tenant_id, product_id=item.product_id)
            warehouse = self._get_active_warehouse(tenant_id=tenant_id, warehouse_id=item.warehouse_id)
            pair = (product.id, warehouse.id)
            if pair in seen_pairs:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Each product and warehouse combination may appear only once per sales order.",
                )
            seen_pairs.add(pair)

            quantity = int(item.quantity)
            unit_price = self._quantize(item.unit_price)
            tax_rate = self._quantize(item.tax_rate)
            discount = self._quantize(item.discount)
            line_subtotal = self._quantize(unit_price * quantity)
            line_tax = self._quantize(line_subtotal * (tax_rate / Decimal("100")))
            total_price = self._quantize(line_subtotal + line_tax - discount)
            if total_price < Decimal("0.00"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Line total cannot be negative after discount.")

            validated_items.append(
                {
                    "product_id": product.id,
                    "warehouse_id": warehouse.id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "tax_rate": tax_rate,
                    "discount": discount,
                    "total_price": total_price,
                }
            )
        return validated_items

    def _build_order_totals(self, items: list[dict[str, Any]]) -> dict[str, Decimal]:
        subtotal = Decimal("0.00")
        tax_amount = Decimal("0.00")
        discount_amount = Decimal("0.00")
        for item in items:
            line_subtotal = self._quantize(item["unit_price"] * item["quantity"])
            line_tax = self._quantize(line_subtotal * (item["tax_rate"] / Decimal("100")))
            subtotal += line_subtotal
            tax_amount += line_tax
            discount_amount += item["discount"]
        subtotal = self._quantize(subtotal)
        tax_amount = self._quantize(tax_amount)
        discount_amount = self._quantize(discount_amount)
        total_amount = self._quantize(subtotal + tax_amount - discount_amount)
        if total_amount < Decimal("0.00"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sales order total cannot be negative.")
        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "discount_amount": discount_amount,
            "total_amount": total_amount,
        }

    def _reserve_stock(
        self,
        *,
        tenant_id: int,
        sales_order_id: int,
        items: list[SalesOrderItem],
        current_user: User,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> None:
        for item in items:
            product = self._get_active_product(tenant_id=tenant_id, product_id=item.product_id)
            warehouse = self._get_active_warehouse(tenant_id=tenant_id, warehouse_id=item.warehouse_id)
            stock = self.stock_repository.get_for_update(tenant_id=tenant_id, product_id=product.id, warehouse_id=warehouse.id)
            if stock is None or stock.available_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient available stock for product {product.sku} in warehouse {warehouse.code}.",
                )
            stock_old = self._stock_snapshot(stock)
            self.stock_repository.update(
                stock,
                {
                    "reserved_quantity": stock.reserved_quantity + item.quantity,
                    "available_quantity": stock.available_quantity - item.quantity,
                },
            )
            self.transaction_repository.create(
                InventoryTransaction(
                    tenant_id=tenant_id,
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    source_warehouse_id=None,
                    destination_warehouse_id=None,
                    transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_RESERVE,
                    quantity=item.quantity,
                    reference_type="sales_order",
                    reference_id=sales_order_id,
                    note=note,
                    created_by=current_user.id,
                )
            )
            self.audit_repository.create(
                AuditLog(
                    tenant_id=tenant_id,
                    user_id=current_user.id,
                    action="inventory.sales_order_reserve",
                    entity_type="warehouse_stock",
                    entity_id=stock.id,
                    old_value_json=stock_old,
                    new_value_json={
                        "quantity": stock.quantity,
                        "reserved_quantity": stock.reserved_quantity,
                        "available_quantity": stock.available_quantity,
                        "product_id": product.id,
                        "warehouse_id": warehouse.id,
                        "sales_order_id": sales_order_id,
                    },
                    ip_address=request_meta.get("ip_address"),
                    user_agent=request_meta.get("user_agent"),
                )
            )

    def _release_reserved_stock(
        self,
        *,
        tenant_id: int,
        sales_order_id: int,
        items: list[SalesOrderItem],
        current_user: User,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> None:
        for item in items:
            product = self._get_active_product(tenant_id=tenant_id, product_id=item.product_id)
            warehouse = self._get_active_warehouse(tenant_id=tenant_id, warehouse_id=item.warehouse_id)
            stock = self.stock_repository.get_for_update(tenant_id=tenant_id, product_id=product.id, warehouse_id=warehouse.id)
            if stock is None or stock.reserved_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Reserved stock mismatch for product {product.sku} in warehouse {warehouse.code}.",
                )
            stock_old = self._stock_snapshot(stock)
            self.stock_repository.update(
                stock,
                {
                    "reserved_quantity": stock.reserved_quantity - item.quantity,
                    "available_quantity": stock.available_quantity + item.quantity,
                },
            )
            self.transaction_repository.create(
                InventoryTransaction(
                    tenant_id=tenant_id,
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    source_warehouse_id=None,
                    destination_warehouse_id=None,
                    transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_CANCEL_RELEASE,
                    quantity=item.quantity,
                    reference_type="sales_order",
                    reference_id=sales_order_id,
                    note=note,
                    created_by=current_user.id,
                )
            )
            self.audit_repository.create(
                AuditLog(
                    tenant_id=tenant_id,
                    user_id=current_user.id,
                    action="inventory.sales_order_cancel_release",
                    entity_type="warehouse_stock",
                    entity_id=stock.id,
                    old_value_json=stock_old,
                    new_value_json={
                        "quantity": stock.quantity,
                        "reserved_quantity": stock.reserved_quantity,
                        "available_quantity": stock.available_quantity,
                        "product_id": product.id,
                        "warehouse_id": warehouse.id,
                        "sales_order_id": sales_order_id,
                    },
                    ip_address=request_meta.get("ip_address"),
                    user_agent=request_meta.get("user_agent"),
                )
            )

    def _deduct_reserved_stock(
        self,
        *,
        tenant_id: int,
        sales_order_id: int,
        items: list[SalesOrderItem],
        current_user: User,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> None:
        for item in items:
            product = self._get_active_product(tenant_id=tenant_id, product_id=item.product_id)
            warehouse = self._get_active_warehouse(tenant_id=tenant_id, warehouse_id=item.warehouse_id)
            stock = self.stock_repository.get_for_update(tenant_id=tenant_id, product_id=product.id, warehouse_id=warehouse.id)
            if stock is None or stock.reserved_quantity < item.quantity or stock.quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Reserved stock is not available for product {product.sku} in warehouse {warehouse.code}.",
                )
            stock_old = self._stock_snapshot(stock)
            self.stock_repository.update(
                stock,
                {
                    "quantity": stock.quantity - item.quantity,
                    "reserved_quantity": stock.reserved_quantity - item.quantity,
                },
            )
            self.transaction_repository.create(
                InventoryTransaction(
                    tenant_id=tenant_id,
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    source_warehouse_id=None,
                    destination_warehouse_id=None,
                    transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_DEDUCT,
                    quantity=item.quantity,
                    reference_type="sales_order",
                    reference_id=sales_order_id,
                    note=note,
                    created_by=current_user.id,
                )
            )
            self.audit_repository.create(
                AuditLog(
                    tenant_id=tenant_id,
                    user_id=current_user.id,
                    action="inventory.sales_order_deduct",
                    entity_type="warehouse_stock",
                    entity_id=stock.id,
                    old_value_json=stock_old,
                    new_value_json={
                        "quantity": stock.quantity,
                        "reserved_quantity": stock.reserved_quantity,
                        "available_quantity": stock.available_quantity,
                        "product_id": product.id,
                        "warehouse_id": warehouse.id,
                        "sales_order_id": sales_order_id,
                    },
                    ip_address=request_meta.get("ip_address"),
                    user_agent=request_meta.get("user_agent"),
                )
            )

    def _sales_order_snapshot(self, sales_order: SalesOrder, items: list[SalesOrderItem]) -> dict[str, Any]:
        return {
            "id": sales_order.id,
            "tenant_id": sales_order.tenant_id,
            "customer_id": sales_order.customer_id,
            "so_number": sales_order.so_number,
            "order_date": sales_order.order_date.isoformat(),
            "status": sales_order.status.value,
            "subtotal": str(sales_order.subtotal),
            "tax_amount": str(sales_order.tax_amount),
            "discount_amount": str(sales_order.discount_amount),
            "total_amount": str(sales_order.total_amount),
            "notes": sales_order.notes,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "warehouse_id": item.warehouse_id,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "tax_rate": str(item.tax_rate),
                    "discount": str(item.discount),
                    "total_price": str(item.total_price),
                }
                for item in items
            ],
        }

    def _log_sales_order_action(
        self,
        *,
        actor: User,
        sales_order: SalesOrder,
        action: str,
        old_value: dict[str, Any] | None,
        new_value: dict[str, Any] | None,
        request_meta: dict[str, str | None] | None = None,
    ) -> None:
        self.audit_repository.create(
            AuditLog(
                tenant_id=sales_order.tenant_id,
                user_id=actor.id,
                action=action,
                entity_type="sales_order",
                entity_id=sales_order.id,
                old_value_json=old_value,
                new_value_json=new_value,
                ip_address=(request_meta or {}).get("ip_address"),
                user_agent=(request_meta or {}).get("user_agent"),
            )
        )

    def _get_active_product(self, *, tenant_id: int, product_id: int) -> Product:
        product = self.product_repository.get_by_id(product_id)
        if not product or product.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found for this tenant.")
        if product.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived products cannot be used in sales orders.")
        return product

    def _get_active_warehouse(self, *, tenant_id: int, warehouse_id: int) -> Warehouse:
        warehouse = self.warehouse_repository.get_by_id(warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found for this tenant.")
        if warehouse.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived warehouses cannot be used in sales orders.")
        return warehouse

    def _stock_snapshot(self, stock: WarehouseStock) -> dict[str, int | None]:
        return {
            "quantity": stock.quantity,
            "reserved_quantity": stock.reserved_quantity,
            "available_quantity": stock.available_quantity,
            "reorder_level": stock.reorder_level,
        }

    def _quantize(self, value: Decimal | int | float) -> Decimal:
        return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
