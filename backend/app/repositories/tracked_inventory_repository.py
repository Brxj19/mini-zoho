from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.enums import InventorySerialStatusEnum
from app.models.inventory_batch import InventoryBatch
from app.models.inventory_serial import InventorySerial


class InventoryBatchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_scope(self, *, tenant_id: int, product_id: int, warehouse_id: int, batch_number: str) -> InventoryBatch | None:
        statement = select(InventoryBatch).where(
            InventoryBatch.tenant_id == tenant_id,
            InventoryBatch.product_id == product_id,
            InventoryBatch.warehouse_id == warehouse_id,
            InventoryBatch.batch_number == batch_number,
        )
        return self.db.scalar(statement)

    def create(self, batch: InventoryBatch) -> InventoryBatch:
        self.db.add(batch)
        self.db.flush()
        self.db.refresh(batch)
        return batch

    def update(self, batch: InventoryBatch, updates: dict[str, object]) -> InventoryBatch:
        for field, value in updates.items():
            setattr(batch, field, value)
        self.db.add(batch)
        self.db.flush()
        self.db.refresh(batch)
        return batch

    def list(
        self,
        *,
        tenant_id: int,
        page: int,
        page_size: int,
        product_id: int | None = None,
        warehouse_id: int | None = None,
    ) -> tuple[list[InventoryBatch], int]:
        query: Select[tuple[InventoryBatch]] = select(InventoryBatch).where(InventoryBatch.tenant_id == tenant_id)
        count_query = select(func.count(InventoryBatch.id)).where(InventoryBatch.tenant_id == tenant_id)
        if product_id is not None:
            query = query.where(InventoryBatch.product_id == product_id)
            count_query = count_query.where(InventoryBatch.product_id == product_id)
        if warehouse_id is not None:
            query = query.where(InventoryBatch.warehouse_id == warehouse_id)
            count_query = count_query.where(InventoryBatch.warehouse_id == warehouse_id)
        query = query.order_by(InventoryBatch.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(query).all()), int(self.db.scalar(count_query) or 0)


class InventorySerialRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_serial(self, *, tenant_id: int, serial_number: str) -> InventorySerial | None:
        statement = select(InventorySerial).where(InventorySerial.tenant_id == tenant_id, InventorySerial.serial_number == serial_number)
        return self.db.scalar(statement)

    def create_many(self, serials: list[InventorySerial]) -> list[InventorySerial]:
        if serials:
            self.db.add_all(serials)
            self.db.flush()
        return serials

    def update(self, serial: InventorySerial, updates: dict[str, object]) -> InventorySerial:
        for field, value in updates.items():
            setattr(serial, field, value)
        self.db.add(serial)
        self.db.flush()
        self.db.refresh(serial)
        return serial

    def list(
        self,
        *,
        tenant_id: int,
        page: int,
        page_size: int,
        product_id: int | None = None,
        warehouse_id: int | None = None,
        status_filter: InventorySerialStatusEnum | None = None,
    ) -> tuple[list[InventorySerial], int]:
        query: Select[tuple[InventorySerial]] = select(InventorySerial).where(InventorySerial.tenant_id == tenant_id)
        count_query = select(func.count(InventorySerial.id)).where(InventorySerial.tenant_id == tenant_id)
        if product_id is not None:
            query = query.where(InventorySerial.product_id == product_id)
            count_query = count_query.where(InventorySerial.product_id == product_id)
        if warehouse_id is not None:
            query = query.where(InventorySerial.warehouse_id == warehouse_id)
            count_query = count_query.where(InventorySerial.warehouse_id == warehouse_id)
        if status_filter is not None:
            query = query.where(InventorySerial.status == status_filter)
            count_query = count_query.where(InventorySerial.status == status_filter)
        query = query.order_by(InventorySerial.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(query).all()), int(self.db.scalar(count_query) or 0)
