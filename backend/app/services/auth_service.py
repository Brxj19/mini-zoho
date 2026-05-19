from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.enums import RoleEnum, TenantStatusEnum, UserStatusEnum
from app.models.tenant import Tenant
from app.models.user import User
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest
from app.services.audit_log_service import AuditLogService

settings = get_settings()


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.tenant_repository = TenantRepository(db)
        self.audit_log_service = AuditLogService(db)

    def register_tenant_admin(self, payload: RegisterRequest) -> tuple[User, Tenant]:
        existing_user = self.user_repository.get_by_email(payload.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

        tenant = Tenant(
            company_name=payload.company_name,
            contact_email=payload.contact_email or payload.email,
            phone=payload.phone,
            address=payload.address,
            gst_number=payload.gst_number,
            business_type=payload.business_type,
            status=TenantStatusEnum(settings.initial_tenant_status.upper()),
            subscription_plan_id=1,
        )

        user = User(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=RoleEnum.TENANT_ADMIN,
            status=UserStatusEnum.ACTIVE,
        )

        try:
            self.tenant_repository.create(tenant)
            user.tenant_id = tenant.id
            self.user_repository.create(user)
            self.db.commit()
            self.db.refresh(tenant)
            self.db.refresh(user)
        except Exception:
            self.db.rollback()
            raise

        return user, tenant

    def authenticate(self, email: str, password: str) -> User:
        user = self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

        if user.status != UserStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user account is inactive.")

        if user.role != RoleEnum.SUPER_ADMIN:
            if user.tenant is None:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant membership is required.")
            if user.tenant.status != TenantStatusEnum.ACTIVE:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This tenant is disabled.")

        user.last_login_at = datetime.now(UTC)
        self.db.add(user)
        self.audit_log_service.log(
            actor=user,
            action="auth.login",
            entity_type="user",
            entity_id=user.id,
            new_value={"last_login_at": user.last_login_at.isoformat()},
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def refresh_session(self, refresh_token: str) -> User:
        try:
            payload = decode_token(refresh_token)
        except TokenError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

        user_id = int(payload["sub"])
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        if user.status != UserStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user account is inactive.")
        if user.role != RoleEnum.SUPER_ADMIN and (not user.tenant or user.tenant.status != TenantStatusEnum.ACTIVE):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This tenant is disabled.")
        return user

    def change_password(self, user: User, current_password: str, new_password: str) -> User:
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")

        user.password_hash = hash_password(new_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def build_session_payload(self, user: User) -> dict[str, str]:
        extra_claims = {
            "role": user.role.value,
            "tenant_id": user.tenant_id,
        }
        return {
            "access_token": create_access_token(str(user.id), extra_claims=extra_claims),
            "refresh_token": create_refresh_token(str(user.id), extra_claims=extra_claims),
        }
