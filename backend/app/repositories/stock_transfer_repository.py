from __future__ import annotations

from sqlalchemy import Select, String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import StockTransferStatusEnum
from app.models.stock_transfer import StockTransfer
from app.models.stock_transfer_item import StockTransferItem


class StockTransferRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, transfer: StockTransfer) -> StockTransfer:
        self.db.add(transfer)
        self.db.flush()
        self.db.refresh(transfer)
        return transfer

    def get_by_id(self, transfer_id: int) -> StockTransfer | None:
        return self.db.get(StockTransfer, transfer_id)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        tenant_id: int | None,
        status_filter: StockTransferStatusEnum | None = None,
        source_warehouse_id: int | None = None,
        destination_warehouse_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[StockTransfer], int]:
        query: Select[tuple[StockTransfer]] = select(StockTransfer)
        count_query = select(func.count(StockTransfer.id))

        if tenant_id is not None:
            query = query.where(StockTransfer.tenant_id == tenant_id)
            count_query = count_query.where(StockTransfer.tenant_id == tenant_id)
        if status_filter is not None:
            query = query.where(StockTransfer.status == status_filter)
            count_query = count_query.where(StockTransfer.status == status_filter)
        if source_warehouse_id is not None:
            query = query.where(StockTransfer.source_warehouse_id == source_warehouse_id)
            count_query = count_query.where(StockTransfer.source_warehouse_id == source_warehouse_id)
        if destination_warehouse_id is not None:
            query = query.where(StockTransfer.destination_warehouse_id == destination_warehouse_id)
            count_query = count_query.where(StockTransfer.destination_warehouse_id == destination_warehouse_id)
        if search:
            search_filter = or_(
                StockTransfer.notes.ilike(f"%{search}%"),
                cast(StockTransfer.id, String).ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        query = query.order_by(StockTransfer.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def update(self, transfer: StockTransfer, updates: dict) -> StockTransfer:
        for field, value in updates.items():
            setattr(transfer, field, value)
        self.db.add(transfer)
        self.db.flush()
        self.db.refresh(transfer)
        return transfer


class StockTransferItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_many(self, items: list[StockTransferItem]) -> list[StockTransferItem]:
        self.db.add_all(items)
        self.db.flush()
        return items

    def list_by_transfer(self, transfer_id: int) -> list[StockTransferItem]:
        statement = (
            select(StockTransferItem)
            .where(StockTransferItem.stock_transfer_id == transfer_id)
            .order_by(StockTransferItem.id.asc())
        )
        return list(self.db.scalars(statement).all())

    def delete_for_transfer(self, transfer_id: int) -> None:
        for item in self.list_by_transfer(transfer_id):
            self.db.delete(item)
        self.db.flush()
