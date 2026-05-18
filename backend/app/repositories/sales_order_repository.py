from __future__ import annotations

from datetime import date

from sqlalchemy import Select, String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import SalesOrderStatusEnum
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem


class SalesOrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, sales_order: SalesOrder) -> SalesOrder:
        self.db.add(sales_order)
        self.db.flush()
        self.db.refresh(sales_order)
        return sales_order

    def get_by_id(self, sales_order_id: int) -> SalesOrder | None:
        return self.db.get(SalesOrder, sales_order_id)

    def find_by_number(self, *, tenant_id: int, so_number: str, exclude_id: int | None = None) -> SalesOrder | None:
        statement = select(SalesOrder).where(
            SalesOrder.tenant_id == tenant_id,
            SalesOrder.so_number == so_number,
        )
        if exclude_id is not None:
            statement = statement.where(SalesOrder.id != exclude_id)
        return self.db.scalar(statement)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        tenant_id: int | None,
        status_filter: SalesOrderStatusEnum | None = None,
        customer_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,
    ) -> tuple[list[SalesOrder], int]:
        query: Select[tuple[SalesOrder]] = select(SalesOrder)
        count_query = select(func.count(SalesOrder.id))

        if tenant_id is not None:
            query = query.where(SalesOrder.tenant_id == tenant_id)
            count_query = count_query.where(SalesOrder.tenant_id == tenant_id)
        if status_filter is not None:
            query = query.where(SalesOrder.status == status_filter)
            count_query = count_query.where(SalesOrder.status == status_filter)
        if customer_id is not None:
            query = query.where(SalesOrder.customer_id == customer_id)
            count_query = count_query.where(SalesOrder.customer_id == customer_id)
        if date_from is not None:
            query = query.where(SalesOrder.order_date >= date_from)
            count_query = count_query.where(SalesOrder.order_date >= date_from)
        if date_to is not None:
            query = query.where(SalesOrder.order_date <= date_to)
            count_query = count_query.where(SalesOrder.order_date <= date_to)
        if search:
            search_filter = or_(
                SalesOrder.so_number.ilike(f"%{search}%"),
                SalesOrder.notes.ilike(f"%{search}%"),
                cast(SalesOrder.id, String).ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        query = query.order_by(SalesOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def update(self, sales_order: SalesOrder, updates: dict) -> SalesOrder:
        for field, value in updates.items():
            setattr(sales_order, field, value)
        self.db.add(sales_order)
        self.db.flush()
        self.db.refresh(sales_order)
        return sales_order


class SalesOrderItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_many(self, items: list[SalesOrderItem]) -> list[SalesOrderItem]:
        self.db.add_all(items)
        self.db.flush()
        return items

    def list_by_sales_order(self, sales_order_id: int) -> list[SalesOrderItem]:
        statement = (
            select(SalesOrderItem)
            .where(SalesOrderItem.sales_order_id == sales_order_id)
            .order_by(SalesOrderItem.id.asc())
        )
        return list(self.db.scalars(statement).all())

    def delete_for_sales_order(self, sales_order_id: int) -> None:
        for item in self.list_by_sales_order(sales_order_id):
            self.db.delete(item)
        self.db.flush()
