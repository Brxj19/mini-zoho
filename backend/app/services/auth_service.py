from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import Tenant, User
from app.schemas.app import RegisterRequest, SetupRequest


def login_user(db: Session, email: str, password: str) -> dict:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if user.status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user account is not active.")

    user.last_login_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return build_auth_payload(db, user)


def register_tenant_admin(db: Session, payload: RegisterRequest) -> dict:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

    tenant = Tenant(
        company_name=payload.company_name,
        contact_email=payload.email,
        phone=payload.phone,
        city=payload.country,
        state=payload.country,
        industry="Retail",
        currency="INR",
        timezone="Asia/Kolkata",
        plan="Starter",
        status="ACTIVE",
        setup_completed=False,
    )
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        name=payload.company_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="TENANT_ADMIN",
        status="ACTIVE",
        last_login_at=datetime.now(UTC),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return build_auth_payload(db, user)


def update_setup(db: Session, user: User, payload: SetupRequest) -> dict:
    if user.role == "SUPER_ADMIN" or user.tenant_id is None:
        return build_auth_payload(db, user)

    tenant = db.get(Tenant, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    tenant.company_name = payload.organization_name
    tenant.industry = payload.industry
    tenant.address = payload.address
    tenant.currency = payload.currency
    tenant.timezone = payload.timezone
    tenant.setup_completed = True
    db.commit()
    db.refresh(user)
    return build_auth_payload(db, user)


def build_auth_payload(db: Session, user: User) -> dict:
    tenant = db.get(Tenant, user.tenant_id) if user.tenant_id else None
    token = create_access_token(str(user.id), user.role, user.tenant_id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "setup_required": bool(tenant and not tenant.setup_completed and user.role != "SUPER_ADMIN"),
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "status": user.status,
        },
        "organization": (
            {
                "id": tenant.id,
                "name": tenant.company_name,
                "plan": tenant.plan,
                "status": tenant.status,
            }
            if tenant
            else {
                "id": "platform",
                "name": "Northstar Platform",
                "plan": "Internal",
                "status": "ACTIVE",
            }
        ),
    }
