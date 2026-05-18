from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.security import TokenError, decode_token
from app.models.enums import RoleEnum, TenantStatusEnum, UserStatusEnum
from app.models.user import User
from app.repositories.user_repository import UserRepository

DbSession = Annotated[Session, Depends(get_db_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
AccessToken = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(db: DbSession, token: AccessToken) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except TokenError as exc:
        raise credentials_exception from exc

    if payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = UserRepository(db).get_by_id(int(user_id))
    if not user:
        raise credentials_exception

    if user.status != UserStatusEnum.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user account is inactive.")

    if user.role != RoleEnum.SUPER_ADMIN:
        if user.tenant is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant membership is required.")
        if user.tenant.status != TenantStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This tenant is disabled.")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: RoleEnum):
    def dependency(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this resource.")
        return current_user

    return dependency


def get_pagination_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> tuple[int, int]:
    return page, page_size


def assert_tenant_access(current_user: User, tenant_id: int) -> None:
    if current_user.role == RoleEnum.SUPER_ADMIN:
        return
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-tenant access is not allowed.")


def resolve_tenant_scope(
    current_user: User,
    tenant_id: int | None,
    *,
    allow_all_for_super_admin: bool = False,
    require_for_super_admin: bool = False,
) -> int | None:
    if current_user.role == RoleEnum.SUPER_ADMIN:
        if tenant_id is None:
            if require_for_super_admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="tenant_id is required for super admin access to tenant-owned resources.",
                )
            return None if allow_all_for_super_admin else None
        return tenant_id

    if tenant_id is not None and tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-tenant access is not allowed.")

    return current_user.tenant_id
