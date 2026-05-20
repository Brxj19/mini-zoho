from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import RoleEnum, UserStatusEnum
from app.schemas.common import ORMBaseSchema, PaginationMeta
from app.schemas.tenant import TenantResponse


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=32)
    role: RoleEnum = RoleEnum.VIEWER
    tenant_id: int | None = None
    status: UserStatusEnum = UserStatusEnum.ACTIVE


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)


class UserRoleUpdate(BaseModel):
    role: RoleEnum


class UserStatusUpdate(BaseModel):
    status: UserStatusEnum


class UserResponse(ORMBaseSchema):
    id: int
    tenant_id: int | None
    name: str
    email: str
    phone: str | None
    role: RoleEnum
    status: UserStatusEnum
    last_login_at: datetime | None
    email_verified_at: datetime | None
    phone_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserDetailResponse(UserResponse):
    tenant: TenantResponse | None = None


class UserListResponse(BaseModel):
    items: list[UserDetailResponse]
    meta: PaginationMeta
