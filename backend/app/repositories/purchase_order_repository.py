from __future__ import annotations

from datetime import date

from sqlalchemy import Select, String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import PurchaseOrderStatusEnum
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem


class PurchaseOrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        self.db.add(purchase_order)
        self.db.flush()
        self.db.refresh(purchase_order)
        return purchase_order

    def get_by_id(self, purchase_order_id: int) -> PurchaseOrder | None:
        return self.db.get(PurchaseOrder, purchase_order_id)

    def find_by_number(self, *, tenant_id: int, po_number: str, exclude_id: int | None = None) -> PurchaseOrder | None:
        statement = select(PurchaseOrder).where(
            PurchaseOrder.tenant_id == tenant_id,
            PurchaseOrder.po_number == po_number,
        )
        if exclude_id is not None:
            statement = statement.where(PurchaseOrder.id != exclude_id)
        return self.db.scalar(statement)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        tenant_id: int | None,
        status_filter: PurchaseOrderStatusEnum | None = None,
        vendor_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,
    ) -> tuple[list[PurchaseOrder], int]:
        query: Select[tuple[PurchaseOrder]] = select(PurchaseOrder)
        count_query = select(func.count(PurchaseOrder.id))

        if tenant_id is not None:
            query = query.where(PurchaseOrder.tenant_id == tenant_id)
            count_query = count_query.where(PurchaseOrder.tenant_id == tenant_id)
        if status_filter is not None:
            query = query.where(PurchaseOrder.status == status_filter)
            count_query = count_query.where(PurchaseOrder.status == status_filter)
        if vendor_id is not None:
            query = query.where(PurchaseOrder.vendor_id == vendor_id)
            count_query = count_query.where(PurchaseOrder.vendor_id == vendor_id)
        if date_from is not None:
            query = query.where(PurchaseOrder.order_date >= date_from)
            count_query = count_query.where(PurchaseOrder.order_date >= date_from)
        if date_to is not None:
            query = query.where(PurchaseOrder.order_date <= date_to)
            count_query = count_query.where(PurchaseOrder.order_date <= date_to)
        if search:
            search_filter = or_(
                PurchaseOrder.po_number.ilike(f"%{search}%"),
                PurchaseOrder.notes.ilike(f"%{search}%"),
                cast(PurchaseOrder.id, String).ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        query = query.order_by(PurchaseOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def update(self, purchase_order: PurchaseOrder, updates: dict) -> PurchaseOrder:
        for field, value in updates.items():
            setattr(purchase_order, field, value)
        self.db.add(purchase_order)
        self.db.flush()
        self.db.refresh(purchase_order)
        return purchase_order


class PurchaseOrderItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_many(self, items: list[PurchaseOrderItem]) -> list[PurchaseOrderItem]:
        self.db.add_all(items)
        self.db.flush()
        return items

    def list_by_purchase_order(self, purchase_order_id: int) -> list[PurchaseOrderItem]:
        statement = (
            select(PurchaseOrderItem)
            .where(PurchaseOrderItem.purchase_order_id == purchase_order_id)
            .order_by(PurchaseOrderItem.id.asc())
        )
        return list(self.db.scalars(statement).all())

    def delete_for_purchase_order(self, purchase_order_id: int) -> None:
        for item in self.list_by_purchase_order(purchase_order_id):
            self.db.delete(item)
        self.db.flush()
