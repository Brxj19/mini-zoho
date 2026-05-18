from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import InventoryTransactionTypeEnum, RecordStatusEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.warehouse_stock import WarehouseStock


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        tenant_id: int | None,
        search: str | None = None,
        status_filter: RecordStatusEnum | None = None,
        category_id: int | None = None,
        brand_id: int | None = None,
        vendor_id: int | None = None,
    ) -> tuple[list[Product], int]:
        query: Select[tuple[Product]] = select(Product)
        count_query = select(func.count(Product.id))

        if tenant_id is not None:
            query = query.where(Product.tenant_id == tenant_id)
            count_query = count_query.where(Product.tenant_id == tenant_id)

        if search:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
                Product.barcode.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if status_filter is not None:
            query = query.where(Product.status == status_filter)
            count_query = count_query.where(Product.status == status_filter)
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
            count_query = count_query.where(Product.category_id == category_id)
        if brand_id is not None:
            query = query.where(Product.brand_id == brand_id)
            count_query = count_query.where(Product.brand_id == brand_id)
        if vendor_id is not None:
            query = query.where(Product.vendor_id == vendor_id)
            count_query = count_query.where(Product.vendor_id == vendor_id)

        query = query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def update(self, product: Product, updates: dict) -> Product:
        for field, value in updates.items():
            setattr(product, field, value)
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        return product

    def find_by_sku(self, *, tenant_id: int, sku: str, exclude_id: int | None = None) -> Product | None:
        statement = select(Product).where(Product.tenant_id == tenant_id, Product.sku == sku)
        if exclude_id is not None:
            statement = statement.where(Product.id != exclude_id)
        return self.db.scalar(statement)

    def find_by_barcode(self, *, tenant_id: int, barcode: str, exclude_id: int | None = None) -> Product | None:
        statement = select(Product).where(Product.tenant_id == tenant_id, Product.barcode == barcode)
        if exclude_id is not None:
            statement = statement.where(Product.id != exclude_id)
        return self.db.scalar(statement)

    def get_stock_summary(self, *, product_id: int, tenant_id: int) -> dict[str, Decimal | int]:
        statement = select(
            func.coalesce(func.sum(WarehouseStock.quantity), 0),
            func.coalesce(func.sum(WarehouseStock.reserved_quantity), 0),
            func.coalesce(func.sum(WarehouseStock.available_quantity), 0),
        ).where(
            WarehouseStock.tenant_id == tenant_id,
            WarehouseStock.product_id == product_id,
        )
        quantity, reserved, available = self.db.execute(statement).one()
        return {
            "total_quantity": int(quantity or 0),
            "reserved_quantity": int(reserved or 0),
            "available_quantity": int(available or 0),
        }

    def has_inventory_transactions(self, *, product_id: int, tenant_id: int) -> bool:
        statement = select(InventoryTransaction.id).where(
            InventoryTransaction.tenant_id == tenant_id,
            InventoryTransaction.product_id == product_id,
        ).limit(1)
        return self.db.scalar(statement) is not None
