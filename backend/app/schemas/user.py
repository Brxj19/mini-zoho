from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import RoleEnum, UserStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta
from app.schemas.tenant import TenantResponse


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: RoleEnum = RoleEnum.VIEWER
    tenant_id: int | None = None
    status: UserStatusEnum = UserStatusEnum.ACTIVE


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None


class UserRoleUpdate(BaseModel):
    role: RoleEnum


class UserStatusUpdate(BaseModel):
    status: UserStatusEnum


class UserResponse(ORMBaseSchema):
    id: int
    tenant_id: int | None
    name: str
    email: EmailStr
    role: RoleEnum
    status: UserStatusEnum
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserDetailResponse(UserResponse):
    tenant: TenantResponse | None = None


class UserListResponse(BaseModel):
    items: list[UserDetailResponse]
    meta: PaginationMeta
