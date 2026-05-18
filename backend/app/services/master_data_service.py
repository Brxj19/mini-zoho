from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import assert_tenant_access, resolve_tenant_scope
from app.models.enums import RecordStatusEnum, RoleEnum
from app.models.user import User
from app.repositories.master_data_repository import MasterDataRepository
from app.repositories.tenant_repository import TenantRepository


class MasterDataService:
    def __init__(
        self,
        db: Session,
        *,
        model: type,
        entity_name: str,
        search_columns: Sequence[Any],
        unique_fields: Sequence[str] = (),
    ) -> None:
        self.db = db
        self.model = model
        self.entity_name = entity_name
        self.search_columns = search_columns
        self.unique_fields = unique_fields
        self.repository = MasterDataRepository(db, model)
        self.tenant_repository = TenantRepository(db)

    def list_entities(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        search: str | None = None,
        status_filter: RecordStatusEnum | None = None,
        tenant_id: int | None = None,
        extra_filters: Sequence[Any] = (),
    ) -> tuple[list[Any], int]:
        scoped_tenant_id = resolve_tenant_scope(
            current_user,
            tenant_id,
            allow_all_for_super_admin=True,
        )
        return self.repository.list(
            page=page,
            page_size=page_size,
            search=search,
            search_columns=self.search_columns,
            tenant_id=scoped_tenant_id,
            status=status_filter,
            extra_filters=extra_filters,
        )

    def get_entity_or_404(self, entity_id: int) -> Any:
        entity = self.repository.get_by_id(entity_id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.entity_name} not found.")
        return entity

    def get_entity_for_user(self, *, current_user: User, entity_id: int) -> Any:
        entity = self.get_entity_or_404(entity_id)
        if current_user.role != RoleEnum.SUPER_ADMIN:
            assert_tenant_access(current_user, entity.tenant_id)
        return entity

    def create_entity(self, *, current_user: User, payload: Any, tenant_id: int | None = None) -> Any:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        self._validate_tenant_exists(scoped_tenant_id)

        data = payload.model_dump(exclude_none=True)
        data["tenant_id"] = scoped_tenant_id
        self._ensure_unique_fields(tenant_id=scoped_tenant_id, payload=data)
        entity = self.model(**data)
        self.repository.create(entity)
        self.db.commit()
        return self.get_entity_or_404(entity.id)

    def update_entity(self, *, current_user: User, entity_id: int, payload: Any) -> Any:
        entity = self.get_entity_for_user(current_user=current_user, entity_id=entity_id)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return entity

        self._ensure_unique_fields(tenant_id=entity.tenant_id, payload=updates, exclude_id=entity.id)
        self.repository.update(entity, updates)
        self.db.commit()
        return self.get_entity_or_404(entity.id)

    def archive_entity(self, *, current_user: User, entity_id: int) -> Any:
        entity = self.get_entity_for_user(current_user=current_user, entity_id=entity_id)
        updates = {"status": RecordStatusEnum.ARCHIVED}
        self.repository.update(entity, updates)
        self.db.commit()
        return self.get_entity_or_404(entity.id)

    def _ensure_unique_fields(self, *, tenant_id: int, payload: dict[str, Any], exclude_id: int | None = None) -> None:
        for field_name in self.unique_fields:
            field_value = payload.get(field_name)
            if field_value is None:
                continue

            existing = self.repository.find_by_field(
                field_name,
                field_value,
                tenant_id=tenant_id,
                exclude_id=exclude_id,
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"{self.entity_name} with this {field_name} already exists in this tenant.",
                )

    def _validate_tenant_exists(self, tenant_id: int) -> None:
        if not self.tenant_repository.get_by_id(tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")
