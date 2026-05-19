from __future__ import annotations

from typing import Any

from sqlalchemy import false
from sqlalchemy.orm import Session

from app.models.enums import RecordStatusEnum
from app.models.user import User
from app.models.warehouse import Warehouse
from app.services.governance_service import GovernanceService
from app.services.master_data_service import MasterDataService


class WarehouseService(MasterDataService):
    def __init__(self, db: Session) -> None:
        super().__init__(
            db,
            model=Warehouse,
            entity_name="Warehouse",
            search_columns=(
                Warehouse.name,
                Warehouse.code,
                Warehouse.city,
                Warehouse.state,
                Warehouse.country,
                Warehouse.manager_name,
                Warehouse.phone,
            ),
            unique_fields=("code",),
        )
        self.governance_service = GovernanceService(db)

    def create_entity(self, *, current_user: User, payload: Any, tenant_id: int | None = None) -> Warehouse:
        scoped_tenant_id = self._resolve_and_validate_tenant(current_user, tenant_id)
        data = payload.model_dump(exclude_none=True)
        data["tenant_id"] = scoped_tenant_id
        self.governance_service.assert_limit(tenant_id=scoped_tenant_id, metric_key="warehouses")
        self._ensure_unique_fields(tenant_id=scoped_tenant_id, payload=data)
        if data.get("is_default"):
            self._clear_default_warehouse(scoped_tenant_id)
        warehouse = Warehouse(**data)
        self.repository.create(warehouse)
        self.db.commit()
        return self.get_entity_or_404(warehouse.id)

    def update_entity(self, *, current_user: User, entity_id: int, payload: Any) -> Warehouse:
        warehouse = self.get_entity_for_user(current_user=current_user, entity_id=entity_id)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return warehouse

        self._ensure_unique_fields(tenant_id=warehouse.tenant_id, payload=updates, exclude_id=warehouse.id)
        if updates.get("is_default") is True:
            self._clear_default_warehouse(warehouse.tenant_id, exclude_id=warehouse.id)
        self.repository.update(warehouse, updates)
        self.db.commit()
        return self.get_entity_or_404(warehouse.id)

    def archive_entity(self, *, current_user: User, entity_id: int) -> Warehouse:
        warehouse = self.get_entity_for_user(current_user=current_user, entity_id=entity_id)
        was_default = warehouse.is_default
        self.repository.update(
            warehouse,
            {
                "status": RecordStatusEnum.ARCHIVED,
                "is_default": False,
            },
        )
        if was_default:
            replacement = self._get_active_replacement_warehouse(warehouse.tenant_id, warehouse.id)
            if replacement:
                self.repository.update(replacement, {"is_default": True})
        self.db.commit()
        return self.get_entity_or_404(warehouse.id)

    def _resolve_and_validate_tenant(self, current_user: User, tenant_id: int | None) -> int:
        from app.core.dependencies import resolve_tenant_scope

        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        self._validate_tenant_exists(scoped_tenant_id)
        return scoped_tenant_id

    def _clear_default_warehouse(self, tenant_id: int, exclude_id: int | None = None) -> None:
        filters = [Warehouse.is_default.is_(True), Warehouse.status == RecordStatusEnum.ACTIVE]
        if exclude_id is not None:
            filters.append(Warehouse.id != exclude_id)
        current_defaults, _ = self.repository.list(
            page=1,
            page_size=100,
            tenant_id=tenant_id,
            status=None,
            extra_filters=filters,
        )
        for current_default in current_defaults:
            self.repository.update(current_default, {"is_default": False})

    def _get_active_replacement_warehouse(self, tenant_id: int, archived_id: int) -> Warehouse | None:
        candidates, _ = self.repository.list(
            page=1,
            page_size=1,
            tenant_id=tenant_id,
            status=RecordStatusEnum.ACTIVE,
            extra_filters=(Warehouse.id != archived_id, Warehouse.is_default == false()),
        )
        return candidates[0] if candidates else None
