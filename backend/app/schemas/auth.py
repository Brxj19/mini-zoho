from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.schemas.tenant import TenantResponse
from app.schemas.user import UserDetailResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    contact_email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = None
    gst_number: str | None = Field(default=None, max_length=64)
    business_type: str | None = Field(default=None, max_length=128)


class AuthSessionResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserDetailResponse
    tenant: TenantResponse | None = None


class MessageResponse(BaseModel):
    detail: str
