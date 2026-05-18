from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import RoleEnum, UserStatusEnum
from app.models.user import User
from app.schemas.common import PaginationMeta
from app.schemas.user import (
    UserCreate,
    UserDetailResponse,
    UserListResponse,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=UserListResponse)
def list_users(
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN)),
    pagination: tuple[int, int] = Depends(get_pagination_params),
    search: str | None = Query(default=None),
    role: RoleEnum | None = Query(default=None),
    status_filter: UserStatusEnum | None = Query(default=None, alias="status"),
    tenant_id: int | None = Query(default=None),
) -> UserListResponse:
    page, page_size = pagination
    effective_tenant_id = tenant_id if current_user.role == RoleEnum.SUPER_ADMIN else current_user.tenant_id
    items, total = UserService(db).user_repository.list(
        page=page,
        page_size=page_size,
        search=search,
        role=role,
        status=status_filter,
        tenant_id=effective_tenant_id,
    )
    return UserListResponse(
        items=[UserDetailResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN)),
) -> UserDetailResponse:
    user = UserService(db).create_user(current_user, payload)
    return UserDetailResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: int, db: DbSession, current_user: CurrentUser) -> UserDetailResponse:
    service = UserService(db)
    user = service.get_user_or_404(user_id)
    if current_user.role == RoleEnum.SUPER_ADMIN:
        return UserDetailResponse.model_validate(user)
    if current_user.id == user.id:
        return UserDetailResponse.model_validate(user)
    if current_user.role == RoleEnum.TENANT_ADMIN and current_user.tenant_id == user.tenant_id:
        return UserDetailResponse.model_validate(user)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this user.")


@router.patch("/{user_id}", response_model=UserDetailResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN)),
) -> UserDetailResponse:
    service = UserService(db)
    user = service.get_user_or_404(user_id)
    updated_user = service.update_user(current_user, user, payload)
    return UserDetailResponse.model_validate(updated_user)


@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN)),
) -> UserResponse:
    service = UserService(db)
    user = service.get_user_or_404(user_id)
    updated_user = service.update_user_status(current_user, user, payload.status)
    return UserResponse.model_validate(updated_user)


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN)),
) -> UserResponse:
    service = UserService(db)
    user = service.get_user_or_404(user_id)
    updated_user = service.update_user_role(current_user, user, payload.role)
    return UserResponse.model_validate(updated_user)
