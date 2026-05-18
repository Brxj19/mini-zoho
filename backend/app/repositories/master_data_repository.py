from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session


class MasterDataRepository:
    def __init__(self, db: Session, model: type) -> None:
        self.db = db
        self.model = model

    def create(self, entity: Any) -> Any:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> Any | None:
        return self.db.get(self.model, entity_id)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        search_columns: Sequence[Any] = (),
        tenant_id: int | None = None,
        status: Any | None = None,
        extra_filters: Sequence[Any] = (),
    ) -> tuple[list[Any], int]:
        query: Select[tuple[Any]] = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if tenant_id is not None:
            query = query.where(self.model.tenant_id == tenant_id)
            count_query = count_query.where(self.model.tenant_id == tenant_id)

        if status is not None:
            query = query.where(self.model.status == status)
            count_query = count_query.where(self.model.status == status)

        if search and search_columns:
            search_filter = or_(*[column.ilike(f"%{search}%") for column in search_columns])
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if extra_filters:
            query = query.where(*extra_filters)
            count_query = count_query.where(*extra_filters)

        query = query.order_by(self.model.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def update(self, entity: Any, updates: dict[str, Any]) -> Any:
        for field, value in updates.items():
            setattr(entity, field, value)
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def find_by_field(
        self,
        field_name: str,
        value: Any,
        *,
        tenant_id: int | None = None,
        exclude_id: int | None = None,
    ) -> Any | None:
        field = getattr(self.model, field_name)
        statement = select(self.model).where(field == value)
        if tenant_id is not None:
            statement = statement.where(self.model.tenant_id == tenant_id)
        if exclude_id is not None:
            statement = statement.where(self.model.id != exclude_id)
        return self.db.scalar(statement)
