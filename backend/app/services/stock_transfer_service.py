from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.audit_log import AuditLog
from app.models.enums import InventoryTransactionTypeEnum, RecordStatusEnum, RoleEnum, StockTransferStatusEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.stock_transfer import StockTransfer
from app.models.stock_transfer_item import StockTransferItem
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.inventory_repository import InventoryTransactionRepository, WarehouseStockRepository
from app.repositories.master_data_repository import MasterDataRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.stock_transfer_repository import StockTransferItemRepository, StockTransferRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.governance_service import GovernanceService
from app.services.notification_service import NotificationService


class StockTransferService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.transfer_repository = StockTransferRepository(db)
        self.item_repository = StockTransferItemRepository(db)
        self.product_repository = ProductRepository(db)
        self.stock_repository = WarehouseStockRepository(db)
        self.transaction_repository = InventoryTransactionRepository(db)
        self.audit_repository = AuditLogRepository(db)
        self.tenant_repository = TenantRepository(db)
        self.governance_service = GovernanceService(db)
        self.warehouse_repository = MasterDataRepository(db, Warehouse)
        self.notification_service = NotificationService(db)

    def list_transfers(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        status_filter: StockTransferStatusEnum | None = None,
        source_warehouse_id: int | None = None,
        destination_warehouse_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[StockTransfer], int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.transfer_repository.list(
            page=page,
            page_size=page_size,
            tenant_id=scoped_tenant_id,
            status_filter=status_filter,
            source_warehouse_id=source_warehouse_id,
            destination_warehouse_id=destination_warehouse_id,
            search=search,
        )

    def get_transfer_for_user(self, *, current_user: User, transfer_id: int) -> tuple[StockTransfer, list[StockTransferItem]]:
        transfer = self.transfer_repository.get_by_id(transfer_id)
        if not transfer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock transfer not found.")
        if current_user.role != RoleEnum.SUPER_ADMIN and transfer.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-tenant access is not allowed.")
        items = self.item_repository.list_by_transfer(transfer.id)
        return transfer, items

    def create_transfer(self, *, current_user: User, payload, tenant_id: int | None = None) -> tuple[StockTransfer, list[StockTransferItem]]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        self._validate_tenant_exists(scoped_tenant_id)
        self.governance_service.assert_limit(tenant_id=scoped_tenant_id, metric_key="monthly_stock_transfers")
        self._validate_warehouses(
            tenant_id=scoped_tenant_id,
            source_warehouse_id=payload.source_warehouse_id,
            destination_warehouse_id=payload.destination_warehouse_id,
        )
        items_data = self._validate_items(tenant_id=scoped_tenant_id, items=payload.items)

        transfer = self.transfer_repository.create(
            StockTransfer(
                tenant_id=scoped_tenant_id,
                source_warehouse_id=payload.source_warehouse_id,
                destination_warehouse_id=payload.destination_warehouse_id,
                status=StockTransferStatusEnum.DRAFT,
                notes=payload.notes,
                created_by=current_user.id,
            )
        )
        items = self.item_repository.create_many(
            [
                StockTransferItem(
                    stock_transfer_id=transfer.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                )
                for item in items_data
            ]
        )
        self._log_transfer_action(
            actor=current_user,
            transfer=transfer,
            action="stock_transfer.created",
            old_value=None,
            new_value=self._transfer_snapshot(transfer, items),
        )
        self.db.commit()
        return transfer, items

    def update_transfer(self, *, current_user: User, transfer_id: int, payload) -> tuple[StockTransfer, list[StockTransferItem]]:
        transfer, current_items = self.get_transfer_for_user(current_user=current_user, transfer_id=transfer_id)
        if transfer.status != StockTransferStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft transfers can be updated.")

        updates = payload.model_dump(exclude_unset=True)
        old_snapshot = self._transfer_snapshot(transfer, current_items)
        source_warehouse_id = updates.get("source_warehouse_id", transfer.source_warehouse_id)
        destination_warehouse_id = updates.get("destination_warehouse_id", transfer.destination_warehouse_id)
        self._validate_warehouses(
            tenant_id=transfer.tenant_id,
            source_warehouse_id=source_warehouse_id,
            destination_warehouse_id=destination_warehouse_id,
        )

        if "items" in updates and updates["items"] is not None:
            items_data = self._validate_items(tenant_id=transfer.tenant_id, items=updates["items"])
            self.item_repository.delete_for_transfer(transfer.id)
            current_items = self.item_repository.create_many(
                [
                    StockTransferItem(
                        stock_transfer_id=transfer.id,
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                    )
                    for item in items_data
                ]
            )
        else:
            current_items = self.item_repository.list_by_transfer(transfer.id)

        transfer = self.transfer_repository.update(
            transfer,
            {
                "source_warehouse_id": source_warehouse_id,
                "destination_warehouse_id": destination_warehouse_id,
                "notes": updates.get("notes", transfer.notes),
            },
        )
        self._log_transfer_action(
            actor=current_user,
            transfer=transfer,
            action="stock_transfer.updated",
            old_value=old_snapshot,
            new_value=self._transfer_snapshot(transfer, current_items),
        )
        self.db.commit()
        return transfer, current_items

    def mark_in_transit(self, *, current_user: User, transfer_id: int, notes: str | None = None) -> tuple[StockTransfer, list[StockTransferItem]]:
        transfer, items = self.get_transfer_for_user(current_user=current_user, transfer_id=transfer_id)
        if transfer.status != StockTransferStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft transfers can move to in-transit.")
        self._validate_available_stock(tenant_id=transfer.tenant_id, warehouse_id=transfer.source_warehouse_id, items=items)
        old_snapshot = self._transfer_snapshot(transfer, items)
        transfer = self.transfer_repository.update(
            transfer,
            {
                "status": StockTransferStatusEnum.IN_TRANSIT,
                "notes": notes if notes is not None else transfer.notes,
            },
        )
        self._log_transfer_action(
            actor=current_user,
            transfer=transfer,
            action="stock_transfer.in_transit",
            old_value=old_snapshot,
            new_value=self._transfer_snapshot(transfer, items),
        )
        self.db.commit()
        return transfer, items

    def cancel_transfer(self, *, current_user: User, transfer_id: int, notes: str | None = None) -> tuple[StockTransfer, list[StockTransferItem]]:
        transfer, items = self.get_transfer_for_user(current_user=current_user, transfer_id=transfer_id)
        if transfer.status == StockTransferStatusEnum.COMPLETED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Completed transfers cannot be cancelled.")
        if transfer.status == StockTransferStatusEnum.CANCELLED:
            return transfer, items

        old_snapshot = self._transfer_snapshot(transfer, items)
        transfer = self.transfer_repository.update(
            transfer,
            {
                "status": StockTransferStatusEnum.CANCELLED,
                "notes": notes if notes is not None else transfer.notes,
            },
        )
        self._log_transfer_action(
            actor=current_user,
            transfer=transfer,
            action="stock_transfer.cancelled",
            old_value=old_snapshot,
            new_value=self._transfer_snapshot(transfer, items),
        )
        self.db.commit()
        return transfer, items

    def complete_transfer(self, *, current_user: User, transfer_id: int, notes: str | None = None, request_meta: dict[str, str | None]) -> tuple[StockTransfer, list[StockTransferItem]]:
        transfer, items = self.get_transfer_for_user(current_user=current_user, transfer_id=transfer_id)
        if transfer.status == StockTransferStatusEnum.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancelled transfers cannot be completed.")
        if transfer.status == StockTransferStatusEnum.COMPLETED:
            return transfer, items
        if transfer.status not in {StockTransferStatusEnum.DRAFT, StockTransferStatusEnum.IN_TRANSIT}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer cannot be completed from its current status.")

        old_snapshot = self._transfer_snapshot(transfer, items)
        source_wh = self._get_active_warehouse(tenant_id=transfer.tenant_id, warehouse_id=transfer.source_warehouse_id)
        dest_wh = self._get_active_warehouse(tenant_id=transfer.tenant_id, warehouse_id=transfer.destination_warehouse_id)

        for item in items:
            product = self._get_active_product(tenant_id=transfer.tenant_id, product_id=item.product_id)
            source_stock = self._get_or_create_stock(
                tenant_id=transfer.tenant_id,
                warehouse_id=source_wh.id,
                product=product,
                lock=True,
            )
            if source_stock.available_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient available stock for product {product.sku} in the source warehouse.",
                )
            destination_stock = self._get_or_create_stock(
                tenant_id=transfer.tenant_id,
                warehouse_id=dest_wh.id,
                product=product,
                lock=True,
            )

            source_old = self._stock_snapshot(source_stock)
            destination_old = self._stock_snapshot(destination_stock)

            self.stock_repository.update(
                source_stock,
                {
                    "quantity": source_stock.quantity - item.quantity,
                    "available_quantity": source_stock.available_quantity - item.quantity,
                },
            )
            self.stock_repository.update(
                destination_stock,
                {
                    "quantity": destination_stock.quantity + item.quantity,
                    "available_quantity": destination_stock.available_quantity + item.quantity,
                },
            )

            self.transaction_repository.create(
                InventoryTransaction(
                    tenant_id=transfer.tenant_id,
                    product_id=product.id,
                    warehouse_id=source_wh.id,
                    source_warehouse_id=source_wh.id,
                    destination_warehouse_id=dest_wh.id,
                    transaction_type=InventoryTransactionTypeEnum.TRANSFER_OUT,
                    quantity=item.quantity,
                    reference_type="stock_transfer",
                    reference_id=transfer.id,
                    note=notes if notes is not None else transfer.notes,
                    created_by=current_user.id,
                )
            )
            self.transaction_repository.create(
                InventoryTransaction(
                    tenant_id=transfer.tenant_id,
                    product_id=product.id,
                    warehouse_id=dest_wh.id,
                    source_warehouse_id=source_wh.id,
                    destination_warehouse_id=dest_wh.id,
                    transaction_type=InventoryTransactionTypeEnum.TRANSFER_IN,
                    quantity=item.quantity,
                    reference_type="stock_transfer",
                    reference_id=transfer.id,
                    note=notes if notes is not None else transfer.notes,
                    created_by=current_user.id,
                )
            )
            self.audit_repository.create(
                AuditLog(
                    tenant_id=transfer.tenant_id,
                    user_id=current_user.id,
                    action="inventory.transfer_out",
                    entity_type="warehouse_stock",
                    entity_id=source_stock.id,
                    old_value_json=source_old,
                    new_value_json=self._stock_snapshot(source_stock),
                    ip_address=request_meta.get("ip_address"),
                    user_agent=request_meta.get("user_agent"),
                )
            )
            self.audit_repository.create(
                AuditLog(
                    tenant_id=transfer.tenant_id,
                    user_id=current_user.id,
                    action="inventory.transfer_in",
                    entity_type="warehouse_stock",
                    entity_id=destination_stock.id,
                    old_value_json=destination_old,
                    new_value_json=self._stock_snapshot(destination_stock),
                    ip_address=request_meta.get("ip_address"),
                    user_agent=request_meta.get("user_agent"),
                )
            )
            reorder_level = source_stock.reorder_level if source_stock.reorder_level is not None else product.reorder_level
            if source_stock.available_quantity <= reorder_level:
                self.notification_service.notify_low_stock(
                    tenant_id=transfer.tenant_id,
                    product_name=product.name,
                    sku=product.sku,
                    warehouse_name=source_wh.name,
                    available_quantity=source_stock.available_quantity,
                    reorder_level=reorder_level,
                )

        transfer = self.transfer_repository.update(
            transfer,
            {
                "status": StockTransferStatusEnum.COMPLETED,
                "notes": notes if notes is not None else transfer.notes,
            },
        )
        self._log_transfer_action(
            actor=current_user,
            transfer=transfer,
            action="stock_transfer.completed",
            old_value=old_snapshot,
            new_value=self._transfer_snapshot(transfer, items),
            request_meta=request_meta,
        )
        self.db.commit()
        return transfer, items

    def _validate_tenant_exists(self, tenant_id: int) -> None:
        if not self.tenant_repository.get_by_id(tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    def _validate_warehouses(self, *, tenant_id: int, source_warehouse_id: int, destination_warehouse_id: int) -> None:
        if source_warehouse_id == destination_warehouse_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source and destination warehouses must be different.")
        self._get_active_warehouse(tenant_id=tenant_id, warehouse_id=source_warehouse_id)
        self._get_active_warehouse(tenant_id=tenant_id, warehouse_id=destination_warehouse_id)

    def _validate_items(self, *, tenant_id: int, items: list[Any]) -> list[dict[str, int]]:
        if not items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one transfer item is required.")
        seen_products: set[int] = set()
        normalized: list[dict[str, int]] = []
        for item in items:
            product_id = item.product_id if hasattr(item, "product_id") else item["product_id"]
            quantity = item.quantity if hasattr(item, "quantity") else item["quantity"]
            if product_id in seen_products:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate products are not allowed in a transfer.")
            self._get_active_product(tenant_id=tenant_id, product_id=product_id)
            seen_products.add(product_id)
            normalized.append({"product_id": product_id, "quantity": quantity})
        return normalized

    def _validate_available_stock(self, *, tenant_id: int, warehouse_id: int, items: list[StockTransferItem]) -> None:
        for item in items:
            product = self._get_active_product(tenant_id=tenant_id, product_id=item.product_id)
            stock = self.stock_repository.get_for_update(tenant_id=tenant_id, product_id=product.id, warehouse_id=warehouse_id)
            if stock is None or stock.available_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient available stock for product {product.sku} in the source warehouse.",
                )

    def _get_active_product(self, *, tenant_id: int, product_id: int) -> Product:
        product = self.product_repository.get_by_id(product_id)
        if not product or product.tenant_id != tenant_id or product.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found for this tenant.")
        return product

    def _get_active_warehouse(self, *, tenant_id: int, warehouse_id: int) -> Warehouse:
        warehouse = self.warehouse_repository.get_by_id(warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id or warehouse.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found for this tenant.")
        return warehouse

    def _get_or_create_stock(self, *, tenant_id: int, warehouse_id: int, product: Product, lock: bool) -> WarehouseStock:
        stock = self.stock_repository.get_for_update(tenant_id=tenant_id, product_id=product.id, warehouse_id=warehouse_id) if lock else None
        if stock is None:
            stock = self.stock_repository.create(
                WarehouseStock(
                    tenant_id=tenant_id,
                    warehouse_id=warehouse_id,
                    product_id=product.id,
                    quantity=0,
                    reserved_quantity=0,
                    available_quantity=0,
                    reorder_level=product.reorder_level,
                )
            )
        return stock

    def _stock_snapshot(self, stock: WarehouseStock) -> dict[str, int | None]:
        return {
            "quantity": stock.quantity,
            "reserved_quantity": stock.reserved_quantity,
            "available_quantity": stock.available_quantity,
            "reorder_level": stock.reorder_level,
        }

    def _transfer_snapshot(self, transfer: StockTransfer, items: list[StockTransferItem]) -> dict[str, Any]:
        return {
            "id": transfer.id,
            "source_warehouse_id": transfer.source_warehouse_id,
            "destination_warehouse_id": transfer.destination_warehouse_id,
            "status": transfer.status.value,
            "notes": transfer.notes,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                }
                for item in items
            ],
        }

    def _log_transfer_action(
        self,
        *,
        actor: User,
        transfer: StockTransfer,
        action: str,
        old_value: dict[str, Any] | None,
        new_value: dict[str, Any],
        request_meta: dict[str, str | None] | None = None,
    ) -> None:
        self.audit_repository.create(
            AuditLog(
                tenant_id=transfer.tenant_id,
                user_id=actor.id,
                action=action,
                entity_type="stock_transfer",
                entity_id=transfer.id,
                old_value_json=old_value,
                new_value_json=new_value,
                ip_address=request_meta.get("ip_address") if request_meta else None,
                user_agent=request_meta.get("user_agent") if request_meta else None,
            )
        )
