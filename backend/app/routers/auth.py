from __future__ import annotations

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.auth import (
    AuthSessionResponse,
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
)
from app.schemas.tenant import TenantResponse
from app.schemas.user import UserDetailResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthSessionResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> AuthSessionResponse:
    service = AuthService(db)
    user, tenant = service.register_tenant_admin(payload)
    session_tokens = service.build_session_payload(user)
    return AuthSessionResponse(
        **session_tokens,
        user=UserDetailResponse.model_validate(user),
        tenant=TenantResponse.model_validate(tenant),
    )


@router.post("/login", response_model=AuthSessionResponse)
def login(payload: LoginRequest, db: DbSession) -> AuthSessionResponse:
    service = AuthService(db)
    user = service.authenticate(payload.email, payload.password)
    session_tokens = service.build_session_payload(user)
    return AuthSessionResponse(
        **session_tokens,
        user=UserDetailResponse.model_validate(user),
        tenant=TenantResponse.model_validate(user.tenant) if user.tenant else None,
    )


@router.post("/refresh", response_model=AuthSessionResponse)
def refresh(payload: RefreshTokenRequest, db: DbSession) -> AuthSessionResponse:
    service = AuthService(db)
    user = service.refresh_session(payload.refresh_token)
    session_tokens = service.build_session_payload(user)
    return AuthSessionResponse(
        **session_tokens,
        user=UserDetailResponse.model_validate(user),
        tenant=TenantResponse.model_validate(user.tenant) if user.tenant else None,
    )


@router.post("/logout", response_model=MessageResponse)
def logout(_: CurrentUser) -> MessageResponse:
    return MessageResponse(detail="Logout successful.")


@router.get("/me", response_model=UserDetailResponse)
def me(current_user: CurrentUser) -> UserDetailResponse:
    return UserDetailResponse.model_validate(current_user)


@router.patch("/change-password", response_model=MessageResponse)
def change_password(payload: ChangePasswordRequest, current_user: CurrentUser, db: DbSession) -> MessageResponse:
    AuthService(db).change_password(current_user, payload.current_password, payload.new_password)
    return MessageResponse(detail="Password updated successfully.")
