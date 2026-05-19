from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.enums import RoleEnum, UserStatusEnum
from app.models.user import User
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.services.governance_service import GovernanceService
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.tenant_repository = TenantRepository(db)
        self.governance_service = GovernanceService(db)

    def get_user_or_404(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user

    def create_user(self, actor: User, payload: UserCreate) -> User:
        if self.user_repository.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

        tenant_id = payload.tenant_id
        role = payload.role

        if actor.role != RoleEnum.SUPER_ADMIN:
            tenant_id = actor.tenant_id
            if role == RoleEnum.SUPER_ADMIN:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admins can assign the SUPER_ADMIN role.")
        elif role != RoleEnum.SUPER_ADMIN and tenant_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id is required for tenant users.")

        if role == RoleEnum.SUPER_ADMIN:
            tenant_id = None
        elif tenant_id is not None and not self.tenant_repository.get_by_id(tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

        if tenant_id is not None:
            self.governance_service.assert_limit(tenant_id=tenant_id, metric_key="users")

        user = User(
            tenant_id=tenant_id,
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=role,
            status=payload.status,
        )
        self.user_repository.create(user)
        self.db.commit()
        return self.get_user_or_404(user.id)

    def update_user(self, actor: User, user: User, payload: UserUpdate) -> User:
        self._assert_actor_can_manage_user(actor, user)
        updates = payload.model_dump(exclude_unset=True)
        if "email" in updates and updates["email"] != user.email:
            existing_user = self.user_repository.get_by_email(str(updates["email"]))
            if existing_user and existing_user.id != user.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

        self.user_repository.update(user, updates)
        self.db.commit()
        return self.get_user_or_404(user.id)

    def update_user_status(self, actor: User, user: User, status_value: UserStatusEnum) -> User:
        self._assert_actor_can_manage_user(actor, user)
        self.user_repository.update(user, {"status": status_value})
        self.db.commit()
        return self.get_user_or_404(user.id)

    def update_user_role(self, actor: User, user: User, role: RoleEnum) -> User:
        self._assert_actor_can_manage_user(actor, user)
        if actor.role != RoleEnum.SUPER_ADMIN and role == RoleEnum.SUPER_ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admins can assign the SUPER_ADMIN role.")

        tenant_id = None if role == RoleEnum.SUPER_ADMIN else user.tenant_id
        if actor.role != RoleEnum.SUPER_ADMIN and tenant_id != actor.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only manage users in your own tenant.")

        self.user_repository.update(user, {"role": role, "tenant_id": tenant_id})
        self.db.commit()
        return self.get_user_or_404(user.id)

    def _assert_actor_can_manage_user(self, actor: User, user: User) -> None:
        if actor.role == RoleEnum.SUPER_ADMIN:
            return
        if actor.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only manage users in your own tenant.")
        if user.role == RoleEnum.SUPER_ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant admins cannot manage super admin users.")
