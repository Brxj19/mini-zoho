from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.app import LoginRequest, RegisterRequest, SetupRequest
from app.services.auth_service import login_user, register_tenant_admin, update_setup

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, db: DbSession) -> dict:
    return login_user(db, payload.email, payload.password)


@router.post("/register")
def register(payload: RegisterRequest, db: DbSession) -> dict:
    return register_tenant_admin(db, payload)


@router.get("/me")
def me(db: DbSession, user: CurrentUser) -> dict:
    from app.services.auth_service import build_auth_payload

    return build_auth_payload(db, user)


@router.post("/setup")
def complete_setup(payload: SetupRequest, db: DbSession, user: CurrentUser) -> dict:
    return update_setup(db, user, payload)
