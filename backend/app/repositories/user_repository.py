from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import RoleEnum, UserStatusEnum
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        statement = select(User).options(joinedload(User.tenant)).where(User.id == user_id)
        return self.db.scalar(statement)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).options(joinedload(User.tenant)).where(User.email == email)
        return self.db.scalar(statement)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        role: RoleEnum | None = None,
        status: UserStatusEnum | None = None,
        tenant_id: int | None = None,
    ) -> tuple[list[User], int]:
        query: Select[tuple[User]] = select(User).options(joinedload(User.tenant))
        count_query = select(func.count(User.id))

        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)
            count_query = count_query.where(User.tenant_id == tenant_id)

        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)

        if status:
            query = query.where(User.status == status)
            count_query = count_query.where(User.status == status)

        query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).unique().all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def count_by_tenant(self, tenant_id: int) -> int:
        return self.db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant_id)) or 0

    def count_active_by_tenant(self, tenant_id: int) -> int:
        statement = select(func.count(User.id)).where(
            User.tenant_id == tenant_id,
            User.status == UserStatusEnum.ACTIVE,
        )
        return self.db.scalar(statement) or 0

    def update(self, user: User, updates: dict[str, object]) -> User:
        for field, value in updates.items():
            setattr(user, field, value)
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user
