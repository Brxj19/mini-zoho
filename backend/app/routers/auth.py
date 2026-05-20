from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models.enums import OtpChannelEnum, OtpPurposeEnum
from app.schemas.auth import (
    AuthSessionResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RequestEmailVerificationRequest,
    RequestOtpResponse,
    RequestPhoneVerificationRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordPlaceholderRequest,
    VerifyOtpRequest,
)
from app.schemas.tenant import TenantResponse
from app.schemas.user import UserDetailResponse
from app.services.auth_service import AuthService
from app.services.otp_service import OtpService

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


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(_: ForgotPasswordRequest) -> MessageResponse:
    return MessageResponse(detail="Password reset placeholder received. Email delivery is not implemented in this MVP.")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(_: ResetPasswordPlaceholderRequest) -> MessageResponse:
    return MessageResponse(detail="Password reset placeholder accepted. Token verification is not implemented in this MVP.")


@router.post("/request-email-verification", response_model=RequestOtpResponse)
def request_email_verification(payload: RequestEmailVerificationRequest, current_user: CurrentUser, db: DbSession) -> RequestOtpResponse:
    challenge, _raw_code = OtpService(db).create_otp(
        destination=current_user.email,
        channel=OtpChannelEnum.EMAIL,
        purpose=payload.purpose,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )
    db.commit()
    return RequestOtpResponse(
        challenge_id=challenge.id,
        channel=challenge.channel,
        destination=challenge.destination,
        detail="Verification email sent.",
    )


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(payload: VerifyOtpRequest, current_user: CurrentUser, db: DbSession) -> MessageResponse:
    challenge = OtpService(db).verify_otp(challenge_id=payload.challenge_id, code=payload.code)
    if challenge.user_id != current_user.id or challenge.channel != OtpChannelEnum.EMAIL:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification challenge does not belong to the current user.")
    current_user.email_verified_at = datetime.now(UTC)
    db.add(current_user)
    db.commit()
    return MessageResponse(detail="Email verified successfully.")


@router.post("/request-phone-verification", response_model=RequestOtpResponse)
def request_phone_verification(payload: RequestPhoneVerificationRequest, current_user: CurrentUser, db: DbSession) -> RequestOtpResponse:
    current_user.phone = payload.phone.strip()
    db.add(current_user)
    challenge, _raw_code = OtpService(db).create_otp(
        destination=current_user.phone,
        channel=OtpChannelEnum.SMS,
        purpose=OtpPurposeEnum.PHONE_VERIFY,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )
    db.commit()
    return RequestOtpResponse(
        challenge_id=challenge.id,
        channel=challenge.channel,
        destination=challenge.destination,
        detail="Verification SMS queued.",
    )


@router.post("/verify-phone", response_model=MessageResponse)
def verify_phone(payload: VerifyOtpRequest, current_user: CurrentUser, db: DbSession) -> MessageResponse:
    challenge = OtpService(db).verify_otp(challenge_id=payload.challenge_id, code=payload.code)
    if challenge.user_id != current_user.id or challenge.channel != OtpChannelEnum.SMS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification challenge does not belong to the current user.")
    current_user.phone_verified_at = datetime.now(UTC)
    db.add(current_user)
    db.commit()
    return MessageResponse(detail="Phone verified successfully.")
