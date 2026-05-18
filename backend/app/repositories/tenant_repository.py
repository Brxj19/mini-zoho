from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import TenantStatusEnum
from app.models.tenant import Tenant


class TenantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, tenant: Tenant) -> Tenant:
        self.db.add(tenant)
        self.db.flush()
        self.db.refresh(tenant)
        return tenant

    def get_by_id(self, tenant_id: int) -> Tenant | None:
        return self.db.get(Tenant, tenant_id)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        status: TenantStatusEnum | None = None,
        tenant_id: int | None = None,
    ) -> tuple[list[Tenant], int]:
        query: Select[tuple[Tenant]] = select(Tenant)
        count_query = select(func.count(Tenant.id))

        if tenant_id is not None:
            query = query.where(Tenant.id == tenant_id)
            count_query = count_query.where(Tenant.id == tenant_id)

        if search:
            search_filter = or_(
                Tenant.company_name.ilike(f"%{search}%"),
                Tenant.contact_email.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if status:
            query = query.where(Tenant.status == status)
            count_query = count_query.where(Tenant.status == status)

        query = query.order_by(Tenant.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def update(self, tenant: Tenant, updates: dict[str, object]) -> Tenant:
        for field, value in updates.items():
            setattr(tenant, field, value)
        self.db.add(tenant)
        self.db.flush()
        self.db.refresh(tenant)
        return tenant
