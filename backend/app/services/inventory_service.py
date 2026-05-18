from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.audit_log import AuditLog
from app.models.enums import InventoryTransactionTypeEnum, RecordStatusEnum, RoleEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.inventory_repository import InventoryTransactionRepository, WarehouseStockRepository
from app.repositories.product_repository import ProductRepository


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_repository = ProductRepository(db)
        self.stock_repository = WarehouseStockRepository(db)
        self.transaction_repository = InventoryTransactionRepository(db)
        self.audit_repository = AuditLogRepository(db)

    def stock_in(self, *, current_user: User, payload, request_meta: dict[str, str | None]) -> InventoryTransaction:
        return self._apply_stock_change(
            current_user=current_user,
            product_id=payload.product_id,
            warehouse_id=payload.warehouse_id,
            quantity_delta=payload.quantity,
            transaction_type=InventoryTransactionTypeEnum.STOCK_IN,
            note=payload.note,
            reference_type=payload.reference_type,
            reference_id=payload.reference_id,
            request_meta=request_meta,
        )

    def stock_out(self, *, current_user: User, payload, request_meta: dict[str, str | None]) -> InventoryTransaction:
        return self._apply_stock_change(
            current_user=current_user,
            product_id=payload.product_id,
            warehouse_id=payload.warehouse_id,
            quantity_delta=-payload.quantity,
            transaction_type=InventoryTransactionTypeEnum.STOCK_OUT,
            note=payload.note,
            reference_type=payload.reference_type,
            reference_id=payload.reference_id,
            request_meta=request_meta,
        )

    def adjust_stock(self, *, current_user: User, payload, request_meta: dict[str, str | None]) -> InventoryTransaction:
        if payload.quantity_delta == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quantity_delta cannot be zero.")
        return self._apply_stock_change(
            current_user=current_user,
            product_id=payload.product_id,
            warehouse_id=payload.warehouse_id,
            quantity_delta=payload.quantity_delta,
            transaction_type=InventoryTransactionTypeEnum.ADJUSTMENT,
            note=payload.note,
            reference_type=payload.reference_type,
            reference_id=payload.reference_id,
            request_meta=request_meta,
        )

    def list_transactions(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        product_id: int | None = None,
        warehouse_id: int | None = None,
        transaction_type: InventoryTransactionTypeEnum | None = None,
        created_by: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[InventoryTransaction], int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.transaction_repository.list(
            page=page,
            page_size=page_size,
            tenant_id=scoped_tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type=transaction_type,
            created_by=created_by,
            date_from=date_from,
            date_to=date_to,
        )

    def list_product_transactions(self, *, current_user: User, product_id: int, page: int, page_size: int) -> tuple[list[InventoryTransaction], int]:
        product = self._get_product_for_inventory(current_user=current_user, product_id=product_id)
        return self.transaction_repository.list_by_product(
            page=page,
            page_size=page_size,
            tenant_id=product.tenant_id,
            product_id=product.id,
        )

    def get_product_stock_breakdown(self, *, current_user: User, product_id: int) -> tuple[Product, dict[str, int], list[WarehouseStock]]:
        product = self._get_product_for_inventory(current_user=current_user, product_id=product_id)
        summary = self.product_repository.get_stock_summary(product_id=product.id, tenant_id=product.tenant_id)
        warehouses = self.stock_repository.list_by_product(tenant_id=product.tenant_id, product_id=product.id)
        return product, summary, warehouses

    def low_stock(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
    ):
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.stock_repository.list_low_stock(
            tenant_id=scoped_tenant_id,
            page=page,
            page_size=page_size,
            warehouse_id=warehouse_id,
            product_id=product_id,
        )

    def _apply_stock_change(
        self,
        *,
        current_user: User,
        product_id: int,
        warehouse_id: int,
        quantity_delta: int,
        transaction_type: InventoryTransactionTypeEnum,
        note: str | None,
        reference_type: str | None,
        reference_id: int | None,
        request_meta: dict[str, str | None],
    ) -> InventoryTransaction:
        if transaction_type == InventoryTransactionTypeEnum.ADJUSTMENT and not note:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Adjustment reason is required.")

        product = self._get_product_for_inventory(current_user=current_user, product_id=product_id)
        warehouse = self._get_warehouse_for_inventory(current_user=current_user, warehouse_id=warehouse_id, tenant_id=product.tenant_id)

        stock = self.stock_repository.get_for_update(
            tenant_id=product.tenant_id,
            product_id=product.id,
            warehouse_id=warehouse.id,
        )
        if stock is None:
            stock = self.stock_repository.create(
                WarehouseStock(
                    tenant_id=product.tenant_id,
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    quantity=0,
                    reserved_quantity=0,
                    available_quantity=0,
                    reorder_level=product.reorder_level,
                )
            )

        old_snapshot = {
            "quantity": stock.quantity,
            "reserved_quantity": stock.reserved_quantity,
            "available_quantity": stock.available_quantity,
        }
        new_quantity = stock.quantity + quantity_delta
        if new_quantity < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock. Negative stock is not allowed.")
        if new_quantity - stock.reserved_quantity < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reserved stock prevents this operation.")

        updates = {
            "quantity": new_quantity,
            "available_quantity": new_quantity - stock.reserved_quantity,
        }
        self.stock_repository.update(stock, updates)

        transaction = self.transaction_repository.create(
            InventoryTransaction(
                tenant_id=product.tenant_id,
                product_id=product.id,
                warehouse_id=warehouse.id,
                source_warehouse_id=None,
                destination_warehouse_id=None,
                transaction_type=transaction_type,
                quantity=abs(quantity_delta),
                reference_type=reference_type,
                reference_id=reference_id,
                note=note,
                created_by=current_user.id,
            )
        )
        transaction_quantity = quantity_delta if transaction_type == InventoryTransactionTypeEnum.ADJUSTMENT else abs(quantity_delta)
        self.audit_repository.create(
            AuditLog(
                tenant_id=product.tenant_id,
                user_id=current_user.id,
                action=f"inventory.{transaction_type.value.lower()}",
                entity_type="warehouse_stock",
                entity_id=stock.id,
                old_value_json=old_snapshot,
                new_value_json={
                    "quantity": stock.quantity,
                    "reserved_quantity": stock.reserved_quantity,
                    "available_quantity": stock.available_quantity,
                    "product_id": product.id,
                    "warehouse_id": warehouse.id,
                },
                ip_address=request_meta.get("ip_address"),
                user_agent=request_meta.get("user_agent"),
            )
        )
        transaction.quantity = transaction_quantity
        self.db.add(transaction)
        self.db.commit()
        return transaction

    def _get_product_for_inventory(self, *, current_user: User, product_id: int) -> Product:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        if current_user.role != RoleEnum.SUPER_ADMIN and product.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-tenant access is not allowed.")
        if product.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived products cannot be used in stock operations.")
        return product

    def _get_warehouse_for_inventory(self, *, current_user: User, warehouse_id: int, tenant_id: int) -> Warehouse:
        from app.repositories.master_data_repository import MasterDataRepository

        warehouse = MasterDataRepository(self.db, Warehouse).get_by_id(warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found for this tenant.")
        if warehouse.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived warehouses cannot be used in stock operations.")
        return warehouse
