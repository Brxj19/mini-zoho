from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.enums import InventoryTransactionTypeEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.inventory_repository import InventoryTransactionRepository, WarehouseStockRepository
from app.services.notification_service import NotificationService


@dataclass(slots=True)
class ReconciliationResult:
    tenant_id: int
    product_id: int
    warehouse_id: int
    expected_quantity: int
    actual_quantity: int
    expected_reserved_quantity: int
    actual_reserved_quantity: int
    expected_available_quantity: int
    actual_available_quantity: int
    fixed: bool = False


class InventoryEngine:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.stock_repository = WarehouseStockRepository(db)
        self.transaction_repository = InventoryTransactionRepository(db)
        self.audit_repository = AuditLogRepository(db)
        self.notification_service = NotificationService(db)

    def get_or_create_stock(
        self,
        *,
        tenant_id: int,
        product_id: int,
        warehouse_id: int,
        reorder_level: int | None = None,
    ) -> WarehouseStock:
        stock = self.stock_repository.get_for_update(
            tenant_id=tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
        )
        if stock is None:
            stock = self.stock_repository.create(
                WarehouseStock(
                    tenant_id=tenant_id,
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    quantity=0,
                    reserved_quantity=0,
                    available_quantity=0,
                    reorder_level=reorder_level,
                )
            )
        return stock

    def stock_in(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        quantity: int,
        note: str | None,
        reference_type: str | None,
        reference_id: int | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        return self._change_physical_stock(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            quantity_delta=quantity,
            transaction_type=InventoryTransactionTypeEnum.STOCK_IN,
            note=note,
            reference_type=reference_type,
            reference_id=reference_id,
            request_meta=request_meta,
        )

    def stock_out(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        quantity: int,
        note: str | None,
        reference_type: str | None,
        reference_id: int | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        return self._change_physical_stock(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            quantity_delta=-quantity,
            transaction_type=InventoryTransactionTypeEnum.STOCK_OUT,
            note=note,
            reference_type=reference_type,
            reference_id=reference_id,
            request_meta=request_meta,
        )

    def adjust(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        signed_qty: int,
        note: str,
        reference_type: str | None,
        reference_id: int | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        if signed_qty == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quantity_delta cannot be zero.")
        return self._change_physical_stock(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            quantity_delta=signed_qty,
            transaction_type=InventoryTransactionTypeEnum.ADJUSTMENT,
            note=note,
            reference_type=reference_type,
            reference_id=reference_id,
            request_meta=request_meta,
        )

    def reserve_for_sales_order(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        quantity: int,
        sales_order_id: int,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        return self._change_reserved_stock(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            reserved_delta=quantity,
            transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_RESERVE,
            note=note,
            reference_type="sales_order",
            reference_id=sales_order_id,
            request_meta=request_meta,
        )

    def release_sales_order_reservation(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        quantity: int,
        sales_order_id: int,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        return self._change_reserved_stock(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            reserved_delta=-quantity,
            transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_CANCEL_RELEASE,
            note=note,
            reference_type="sales_order",
            reference_id=sales_order_id,
            request_meta=request_meta,
        )

    def deduct_for_sales_order_delivery(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        quantity: int,
        sales_order_id: int,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        existing = self._find_existing_transaction(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=warehouse.id,
            transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_DEDUCT,
            reference_type="sales_order",
            reference_id=sales_order_id,
            expected_quantity=quantity,
        )
        if existing:
            return existing

        stock = self.get_or_create_stock(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=warehouse.id,
            reorder_level=product.reorder_level,
        )
        old_snapshot = self._stock_snapshot(stock)

        if stock.quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.sku} in warehouse {warehouse.code}.",
            )

        reserved_to_consume = 0
        if stock.reserved_quantity >= quantity:
            reserved_to_consume = quantity
        elif stock.reserved_quantity not in {0, quantity} and stock.reserved_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reserved stock mismatch for product {product.sku} in warehouse {warehouse.code}.",
            )

        stock.quantity -= quantity
        stock.reserved_quantity -= reserved_to_consume
        self.recompute_available_quantity(stock)
        self.validate_stock_invariants(stock)
        self.db.add(stock)
        self.db.flush()

        transaction = self._create_transaction(
            current_user=current_user,
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=warehouse.id,
            transaction_type=InventoryTransactionTypeEnum.SALES_ORDER_DEDUCT,
            quantity=quantity,
            note=note,
            reference_type="sales_order",
            reference_id=sales_order_id,
        )
        self._create_stock_audit_log(
            current_user=current_user,
            tenant_id=product.tenant_id,
            action="inventory.sales_order_deduct",
            stock=stock,
            old_snapshot=old_snapshot,
            new_snapshot=self._stock_snapshot(stock),
            request_meta=request_meta,
        )
        self._notify_low_stock_if_needed(product=product, warehouse=warehouse, stock=stock)
        return transaction

    def receive_purchase_order(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        quantity: int,
        purchase_order_id: int,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        return self._change_physical_stock(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            quantity_delta=quantity,
            transaction_type=InventoryTransactionTypeEnum.PURCHASE_RECEIVE,
            note=note,
            reference_type="purchase_order",
            reference_id=purchase_order_id,
            request_meta=request_meta,
            idempotency_enabled=False,
        )

    def transfer_stock(
        self,
        *,
        current_user: User,
        product: Product,
        source_warehouse: Warehouse,
        destination_warehouse: Warehouse,
        quantity: int,
        stock_transfer_id: int,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> tuple[InventoryTransaction, InventoryTransaction]:
        existing_out = self._find_existing_transaction(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=source_warehouse.id,
            transaction_type=InventoryTransactionTypeEnum.TRANSFER_OUT,
            reference_type="stock_transfer",
            reference_id=stock_transfer_id,
            expected_quantity=quantity,
        )
        existing_in = self._find_existing_transaction(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=destination_warehouse.id,
            transaction_type=InventoryTransactionTypeEnum.TRANSFER_IN,
            reference_type="stock_transfer",
            reference_id=stock_transfer_id,
            expected_quantity=quantity,
        )
        if bool(existing_out) != bool(existing_in):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Transfer reference is only partially recorded. Reconcile inventory before retrying this transfer.",
            )
        if existing_out and existing_in:
            return existing_out, existing_in

        source_stock = self.get_or_create_stock(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=source_warehouse.id,
            reorder_level=product.reorder_level,
        )
        destination_stock = self.get_or_create_stock(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=destination_warehouse.id,
            reorder_level=product.reorder_level,
        )
        if source_stock.available_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient available stock for product {product.sku} in the source warehouse.",
            )

        source_old = self._stock_snapshot(source_stock)
        destination_old = self._stock_snapshot(destination_stock)

        source_stock.quantity -= quantity
        destination_stock.quantity += quantity
        self.recompute_available_quantity(source_stock)
        self.recompute_available_quantity(destination_stock)
        self.validate_stock_invariants(source_stock)
        self.validate_stock_invariants(destination_stock)
        self.db.add_all([source_stock, destination_stock])
        self.db.flush()

        out_tx = existing_out or self._create_transaction(
            current_user=current_user,
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=source_warehouse.id,
            transaction_type=InventoryTransactionTypeEnum.TRANSFER_OUT,
            quantity=quantity,
            note=note,
            reference_type="stock_transfer",
            reference_id=stock_transfer_id,
            source_warehouse_id=source_warehouse.id,
            destination_warehouse_id=destination_warehouse.id,
        )
        in_tx = existing_in or self._create_transaction(
            current_user=current_user,
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=destination_warehouse.id,
            transaction_type=InventoryTransactionTypeEnum.TRANSFER_IN,
            quantity=quantity,
            note=note,
            reference_type="stock_transfer",
            reference_id=stock_transfer_id,
            source_warehouse_id=source_warehouse.id,
            destination_warehouse_id=destination_warehouse.id,
        )
        self._create_stock_audit_log(
            current_user=current_user,
            tenant_id=product.tenant_id,
            action="inventory.transfer_out",
            stock=source_stock,
            old_snapshot=source_old,
            new_snapshot=self._stock_snapshot(source_stock),
            request_meta=request_meta,
        )
        self._create_stock_audit_log(
            current_user=current_user,
            tenant_id=product.tenant_id,
            action="inventory.transfer_in",
            stock=destination_stock,
            old_snapshot=destination_old,
            new_snapshot=self._stock_snapshot(destination_stock),
            request_meta=request_meta,
        )
        self._notify_low_stock_if_needed(product=product, warehouse=source_warehouse, stock=source_stock)
        return out_tx, in_tx

    def return_stock(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        quantity: int,
        reference_type: str | None,
        reference_id: int | None,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        return self._change_physical_stock(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            quantity_delta=quantity,
            transaction_type=InventoryTransactionTypeEnum.RETURN_IN,
            note=note,
            reference_type=reference_type,
            reference_id=reference_id,
            request_meta=request_meta,
        )

    def damage_out(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        quantity: int,
        reference_type: str | None,
        reference_id: int | None,
        note: str | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        return self._change_physical_stock(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            quantity_delta=-quantity,
            transaction_type=InventoryTransactionTypeEnum.DAMAGE_OUT,
            note=note,
            reference_type=reference_type,
            reference_id=reference_id,
            request_meta=request_meta,
        )

    def recompute_available_quantity(self, stock: WarehouseStock) -> int:
        stock.available_quantity = stock.quantity - stock.reserved_quantity
        return stock.available_quantity

    def validate_stock_invariants(self, stock: WarehouseStock) -> None:
        if stock.quantity < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock. Negative stock is not allowed.")
        if stock.reserved_quantity < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reserved quantity cannot be negative.")
        if stock.reserved_quantity > stock.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reserved quantity cannot exceed stock quantity.")
        if stock.available_quantity != stock.quantity - stock.reserved_quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Available quantity is out of sync with quantity and reserved quantity.")

    def reconcile_product_warehouse(
        self,
        *,
        tenant_id: int,
        product_id: int,
        warehouse_id: int,
        fix: bool = False,
    ) -> ReconciliationResult | None:
        transactions = self.transaction_repository.list_by_scope(
            tenant_id=tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
        )
        existing_stock = self.stock_repository.get_for_update(
            tenant_id=tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
        )
        if not transactions and not existing_stock:
            return None

        expected_quantity = 0
        expected_reserved_quantity = 0
        for transaction in transactions:
            quantity_effect, reserved_effect = self._effects_from_transaction(transaction)
            expected_quantity += quantity_effect
            expected_reserved_quantity += reserved_effect

        stock = existing_stock
        actual_quantity = stock.quantity if stock else 0
        actual_reserved_quantity = stock.reserved_quantity if stock else 0
        actual_available_quantity = stock.available_quantity if stock else 0
        expected_available_quantity = expected_quantity - expected_reserved_quantity
        result = ReconciliationResult(
            tenant_id=tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            expected_quantity=expected_quantity,
            actual_quantity=actual_quantity,
            expected_reserved_quantity=expected_reserved_quantity,
            actual_reserved_quantity=actual_reserved_quantity,
            expected_available_quantity=expected_available_quantity,
            actual_available_quantity=actual_available_quantity,
            fixed=False,
        )

        mismatch = (
            actual_quantity != expected_quantity
            or actual_reserved_quantity != expected_reserved_quantity
            or actual_available_quantity != expected_available_quantity
        )
        if mismatch and fix:
            stock = stock or self.get_or_create_stock(
                tenant_id=tenant_id,
                product_id=product_id,
                warehouse_id=warehouse_id,
            )
            old_snapshot = self._stock_snapshot(stock)
            stock.quantity = expected_quantity
            stock.reserved_quantity = expected_reserved_quantity
            self.recompute_available_quantity(stock)
            self.validate_stock_invariants(stock)
            self.db.add(stock)
            self.db.flush()
            self.audit_repository.create(
                AuditLog(
                    tenant_id=tenant_id,
                    user_id=None,
                    action="inventory.reconciliation_fix",
                    entity_type="warehouse_stock",
                    entity_id=stock.id,
                    old_value_json=old_snapshot,
                    new_value_json=self._stock_snapshot(stock),
                    ip_address=None,
                    user_agent="reconcile_inventory_cli",
                )
            )
            result.actual_quantity = stock.quantity
            result.actual_reserved_quantity = stock.reserved_quantity
            result.actual_available_quantity = stock.available_quantity
            result.fixed = True
        return result

    def reconcile_tenant(self, *, tenant_id: int, fix: bool = False) -> list[ReconciliationResult]:
        stock_pairs = {
            (stock.product_id, stock.warehouse_id)
            for stock in self.stock_repository.list_by_tenant(tenant_id=tenant_id)
        }
        tx_pairs = {
            (transaction.product_id, transaction.warehouse_id)
            for transaction in self.transaction_repository.list_by_scope(tenant_id=tenant_id)
        }
        pairs = sorted(stock_pairs | tx_pairs)
        results: list[ReconciliationResult] = []
        for product_id, warehouse_id in pairs:
            result = self.reconcile_product_warehouse(
                tenant_id=tenant_id,
                product_id=product_id,
                warehouse_id=warehouse_id,
                fix=fix,
            )
            if result is not None:
                results.append(result)
        return results

    def _change_physical_stock(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        quantity_delta: int,
        transaction_type: InventoryTransactionTypeEnum,
        note: str | None,
        reference_type: str | None,
        reference_id: int | None,
        request_meta: dict[str, str | None],
        idempotency_enabled: bool = True,
    ) -> InventoryTransaction:
        if idempotency_enabled:
            existing = self._find_existing_transaction(
                tenant_id=product.tenant_id,
                product_id=product.id,
                warehouse_id=warehouse.id,
                transaction_type=transaction_type,
                reference_type=reference_type,
                reference_id=reference_id,
                expected_quantity=quantity_delta if transaction_type == InventoryTransactionTypeEnum.ADJUSTMENT else abs(quantity_delta),
            )
            if existing:
                return existing

        stock = self.get_or_create_stock(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=warehouse.id,
            reorder_level=product.reorder_level,
        )
        old_snapshot = self._stock_snapshot(stock)
        stock.quantity += quantity_delta
        self.recompute_available_quantity(stock)
        self.validate_stock_invariants(stock)
        self.db.add(stock)
        self.db.flush()

        transaction = self._create_transaction(
            current_user=current_user,
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=warehouse.id,
            transaction_type=transaction_type,
            quantity=quantity_delta if transaction_type == InventoryTransactionTypeEnum.ADJUSTMENT else abs(quantity_delta),
            note=note,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        self._create_stock_audit_log(
            current_user=current_user,
            tenant_id=product.tenant_id,
            action=f"inventory.{transaction_type.value.lower()}",
            stock=stock,
            old_snapshot=old_snapshot,
            new_snapshot=self._stock_snapshot(stock),
            request_meta=request_meta,
        )
        if quantity_delta < 0:
            self._notify_low_stock_if_needed(product=product, warehouse=warehouse, stock=stock)
        if transaction_type == InventoryTransactionTypeEnum.ADJUSTMENT:
            self._notify_adjustment_if_needed(current_user=current_user, product=product, warehouse=warehouse, quantity_delta=quantity_delta)
        return transaction

    def _change_reserved_stock(
        self,
        *,
        current_user: User,
        product: Product,
        warehouse: Warehouse,
        reserved_delta: int,
        transaction_type: InventoryTransactionTypeEnum,
        note: str | None,
        reference_type: str | None,
        reference_id: int | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        existing = self._find_existing_transaction(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=warehouse.id,
            transaction_type=transaction_type,
            reference_type=reference_type,
            reference_id=reference_id,
            expected_quantity=abs(reserved_delta),
        )
        if existing:
            return existing

        stock = self.get_or_create_stock(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=warehouse.id,
            reorder_level=product.reorder_level,
        )
        old_snapshot = self._stock_snapshot(stock)
        if reserved_delta > 0 and stock.available_quantity < reserved_delta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient available stock for product {product.sku} in warehouse {warehouse.code}.",
            )
        if reserved_delta < 0 and stock.reserved_quantity < abs(reserved_delta):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reserved stock mismatch for product {product.sku} in warehouse {warehouse.code}.",
            )

        stock.reserved_quantity += reserved_delta
        self.recompute_available_quantity(stock)
        self.validate_stock_invariants(stock)
        self.db.add(stock)
        self.db.flush()

        transaction = self._create_transaction(
            current_user=current_user,
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=warehouse.id,
            transaction_type=transaction_type,
            quantity=abs(reserved_delta),
            note=note,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        self._create_stock_audit_log(
            current_user=current_user,
            tenant_id=product.tenant_id,
            action=f"inventory.{transaction_type.value.lower()}",
            stock=stock,
            old_snapshot=old_snapshot,
            new_snapshot=self._stock_snapshot(stock),
            request_meta=request_meta,
        )
        self._notify_low_stock_if_needed(product=product, warehouse=warehouse, stock=stock)
        return transaction

    def _create_transaction(
        self,
        *,
        current_user: User,
        tenant_id: int,
        product_id: int,
        warehouse_id: int,
        transaction_type: InventoryTransactionTypeEnum,
        quantity: int,
        note: str | None,
        reference_type: str | None,
        reference_id: int | None,
        source_warehouse_id: int | None = None,
        destination_warehouse_id: int | None = None,
    ) -> InventoryTransaction:
        return self.transaction_repository.create(
            InventoryTransaction(
                tenant_id=tenant_id,
                product_id=product_id,
                warehouse_id=warehouse_id,
                source_warehouse_id=source_warehouse_id,
                destination_warehouse_id=destination_warehouse_id,
                transaction_type=transaction_type,
                quantity=quantity,
                reference_type=reference_type,
                reference_id=reference_id,
                note=note,
                created_by=current_user.id,
            )
        )

    def _create_stock_audit_log(
        self,
        *,
        current_user: User,
        tenant_id: int,
        action: str,
        stock: WarehouseStock,
        old_snapshot: dict[str, Any],
        new_snapshot: dict[str, Any],
        request_meta: dict[str, str | None],
    ) -> None:
        self.audit_repository.create(
            AuditLog(
                tenant_id=tenant_id,
                user_id=current_user.id,
                action=action,
                entity_type="warehouse_stock",
                entity_id=stock.id,
                old_value_json=old_snapshot,
                new_value_json=new_snapshot,
                ip_address=request_meta.get("ip_address"),
                user_agent=request_meta.get("user_agent"),
            )
        )

    def _notify_low_stock_if_needed(self, *, product: Product, warehouse: Warehouse, stock: WarehouseStock) -> None:
        reorder_level = stock.reorder_level if stock.reorder_level is not None else product.reorder_level
        if reorder_level is not None and stock.available_quantity <= reorder_level:
            self.notification_service.notify_low_stock(
                tenant_id=product.tenant_id,
                product_name=product.name,
                sku=product.sku,
                warehouse_name=warehouse.name,
                available_quantity=stock.available_quantity,
                reorder_level=reorder_level,
            )

    def _notify_adjustment_if_needed(self, *, current_user: User, product: Product, warehouse: Warehouse, quantity_delta: int) -> None:
        threshold = max(10, product.reorder_level or 0, 1)
        if abs(quantity_delta) >= threshold:
            self.notification_service.notify_suspicious_adjustment(
                tenant_id=product.tenant_id,
                product_name=product.name,
                warehouse_name=warehouse.name,
                quantity_delta=quantity_delta,
                actor_name=current_user.name,
            )

    def _find_existing_transaction(
        self,
        *,
        tenant_id: int,
        product_id: int,
        warehouse_id: int,
        transaction_type: InventoryTransactionTypeEnum,
        reference_type: str | None,
        reference_id: int | None,
        expected_quantity: int,
    ) -> InventoryTransaction | None:
        existing = self.transaction_repository.find_by_reference(
            tenant_id=tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type=transaction_type,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        if existing and existing.quantity != expected_quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A stock operation for this reference already exists with a different quantity.",
            )
        return existing

    def _effects_from_transaction(self, transaction: InventoryTransaction) -> tuple[int, int]:
        if transaction.transaction_type == InventoryTransactionTypeEnum.STOCK_IN:
            return transaction.quantity, 0
        if transaction.transaction_type == InventoryTransactionTypeEnum.STOCK_OUT:
            return -transaction.quantity, 0
        if transaction.transaction_type == InventoryTransactionTypeEnum.ADJUSTMENT:
            return transaction.quantity, 0
        if transaction.transaction_type == InventoryTransactionTypeEnum.PURCHASE_RECEIVE:
            return transaction.quantity, 0
        if transaction.transaction_type == InventoryTransactionTypeEnum.SALES_ORDER_RESERVE:
            return 0, transaction.quantity
        if transaction.transaction_type == InventoryTransactionTypeEnum.SALES_ORDER_CANCEL_RELEASE:
            return 0, -transaction.quantity
        if transaction.transaction_type == InventoryTransactionTypeEnum.SALES_ORDER_DEDUCT:
            return -transaction.quantity, -transaction.quantity
        if transaction.transaction_type == InventoryTransactionTypeEnum.TRANSFER_OUT:
            return -transaction.quantity, 0
        if transaction.transaction_type == InventoryTransactionTypeEnum.TRANSFER_IN:
            return transaction.quantity, 0
        if transaction.transaction_type == InventoryTransactionTypeEnum.RETURN_IN:
            return transaction.quantity, 0
        if transaction.transaction_type == InventoryTransactionTypeEnum.DAMAGE_OUT:
            return -transaction.quantity, 0
        return 0, 0

    def _stock_snapshot(self, stock: WarehouseStock) -> dict[str, int | None]:
        return {
            "quantity": stock.quantity,
            "reserved_quantity": stock.reserved_quantity,
            "available_quantity": stock.available_quantity,
            "reorder_level": stock.reorder_level,
            "warehouse_id": stock.warehouse_id,
            "product_id": stock.product_id,
        }
