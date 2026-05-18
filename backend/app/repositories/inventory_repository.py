from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import InventoryTransactionTypeEnum, RecordStatusEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock


class WarehouseStockRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_for_update(self, *, tenant_id: int, product_id: int, warehouse_id: int) -> WarehouseStock | None:
        statement = (
            select(WarehouseStock)
            .where(
                WarehouseStock.tenant_id == tenant_id,
                WarehouseStock.product_id == product_id,
                WarehouseStock.warehouse_id == warehouse_id,
            )
            .with_for_update()
        )
        return self.db.scalar(statement)

    def create(self, stock: WarehouseStock) -> WarehouseStock:
        self.db.add(stock)
        self.db.flush()
        self.db.refresh(stock)
        return stock

    def update(self, stock: WarehouseStock, updates: dict) -> WarehouseStock:
        for field, value in updates.items():
            setattr(stock, field, value)
        self.db.add(stock)
        self.db.flush()
        self.db.refresh(stock)
        return stock

    def list_by_product(self, *, tenant_id: int, product_id: int) -> list[WarehouseStock]:
        statement = (
            select(WarehouseStock)
            .where(WarehouseStock.tenant_id == tenant_id, WarehouseStock.product_id == product_id)
            .order_by(WarehouseStock.warehouse_id.asc())
        )
        return list(self.db.scalars(statement).all())

    def list_low_stock(
        self,
        *,
        tenant_id: int | None,
        page: int,
        page_size: int,
        warehouse_id: int | None = None,
        product_id: int | None = None,
    ) -> tuple[list[tuple[WarehouseStock, Product, Warehouse]], int]:
        query = (
            select(WarehouseStock, Product, Warehouse)
            .join(Product, Product.id == WarehouseStock.product_id)
            .join(Warehouse, Warehouse.id == WarehouseStock.warehouse_id)
            .where(Product.status == RecordStatusEnum.ACTIVE, Warehouse.status == RecordStatusEnum.ACTIVE)
            .where(WarehouseStock.available_quantity <= func.coalesce(WarehouseStock.reorder_level, Product.reorder_level))
        )
        count_query = (
            select(func.count())
            .select_from(WarehouseStock)
            .join(Product, Product.id == WarehouseStock.product_id)
            .join(Warehouse, Warehouse.id == WarehouseStock.warehouse_id)
            .where(Product.status == RecordStatusEnum.ACTIVE, Warehouse.status == RecordStatusEnum.ACTIVE)
            .where(WarehouseStock.available_quantity <= func.coalesce(WarehouseStock.reorder_level, Product.reorder_level))
        )

        if tenant_id is not None:
            query = query.where(WarehouseStock.tenant_id == tenant_id)
            count_query = count_query.where(WarehouseStock.tenant_id == tenant_id)
        if warehouse_id is not None:
            query = query.where(WarehouseStock.warehouse_id == warehouse_id)
            count_query = count_query.where(WarehouseStock.warehouse_id == warehouse_id)
        if product_id is not None:
            query = query.where(WarehouseStock.product_id == product_id)
            count_query = count_query.where(WarehouseStock.product_id == product_id)

        query = query.order_by(WarehouseStock.available_quantity.asc(), Product.name.asc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.execute(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total


class InventoryTransactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, transaction: InventoryTransaction) -> InventoryTransaction:
        self.db.add(transaction)
        self.db.flush()
        self.db.refresh(transaction)
        return transaction

    def list(
        self,
        *,
        page: int,
        page_size: int,
        tenant_id: int | None,
        product_id: int | None = None,
        warehouse_id: int | None = None,
        transaction_type: InventoryTransactionTypeEnum | None = None,
        created_by: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[InventoryTransaction], int]:
        query: Select[tuple[InventoryTransaction]] = select(InventoryTransaction)
        count_query = select(func.count(InventoryTransaction.id))

        if tenant_id is not None:
            query = query.where(InventoryTransaction.tenant_id == tenant_id)
            count_query = count_query.where(InventoryTransaction.tenant_id == tenant_id)
        if product_id is not None:
            query = query.where(InventoryTransaction.product_id == product_id)
            count_query = count_query.where(InventoryTransaction.product_id == product_id)
        if warehouse_id is not None:
            query = query.where(
                or_(
                    InventoryTransaction.warehouse_id == warehouse_id,
                    InventoryTransaction.source_warehouse_id == warehouse_id,
                    InventoryTransaction.destination_warehouse_id == warehouse_id,
                )
            )
            count_query = count_query.where(
                or_(
                    InventoryTransaction.warehouse_id == warehouse_id,
                    InventoryTransaction.source_warehouse_id == warehouse_id,
                    InventoryTransaction.destination_warehouse_id == warehouse_id,
                )
            )
        if transaction_type is not None:
            query = query.where(InventoryTransaction.transaction_type == transaction_type)
            count_query = count_query.where(InventoryTransaction.transaction_type == transaction_type)
        if created_by is not None:
            query = query.where(InventoryTransaction.created_by == created_by)
            count_query = count_query.where(InventoryTransaction.created_by == created_by)
        if date_from is not None:
            query = query.where(InventoryTransaction.created_at >= date_from)
            count_query = count_query.where(InventoryTransaction.created_at >= date_from)
        if date_to is not None:
            query = query.where(InventoryTransaction.created_at <= date_to)
            count_query = count_query.where(InventoryTransaction.created_at <= date_to)

        query = query.order_by(InventoryTransaction.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def list_by_product(self, *, page: int, page_size: int, tenant_id: int, product_id: int) -> tuple[list[InventoryTransaction], int]:
        return self.list(page=page, page_size=page_size, tenant_id=tenant_id, product_id=product_id)
