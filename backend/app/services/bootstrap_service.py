from __future__ import annotations

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.enums import RoleEnum, UserStatusEnum
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)
settings = get_settings()


def ensure_super_admin(db: Session) -> None:
    repository = UserRepository(db)

    try:
        existing_user = repository.get_by_email(settings.super_admin_email)
        if existing_user:
            return

        user = User(
            tenant_id=None,
            name=settings.super_admin_name,
            email=settings.super_admin_email,
            password_hash=hash_password(settings.super_admin_password),
            role=RoleEnum.SUPER_ADMIN,
            status=UserStatusEnum.ACTIVE,
        )
        repository.create(user)
        db.commit()
        logger.info("Seeded default super admin user.")
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to ensure the super admin user exists.")
