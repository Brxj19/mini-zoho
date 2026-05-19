from __future__ import annotations

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.enums import RoleEnum, UserStatusEnum
from app.models.subscription_plan import SubscriptionPlan
from app.models.user import User
from app.repositories.subscription_plan_repository import SubscriptionPlanRepository
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


def ensure_default_subscription_plans(db: Session) -> None:
    repository = SubscriptionPlanRepository(db)
    plans = [
        {
            "id": 1,
            "code": "STARTER",
            "name": "Starter",
            "description": "For smaller teams getting started with inventory operations.",
            "monthly_price": 1999,
            "annual_price": 19990,
            "max_users": 5,
            "max_products": 150,
            "max_warehouses": 2,
            "max_monthly_sales_orders": 150,
            "max_monthly_purchase_orders": 90,
            "max_monthly_stock_transfers": 60,
            "barcode_enabled": True,
            "advanced_inventory_enabled": False,
            "integrations_enabled": False,
            "ai_assistant_enabled": False,
        },
        {
            "id": 2,
            "code": "GROWTH",
            "name": "Growth",
            "description": "For scaling multi-channel retail teams needing deeper controls.",
            "monthly_price": 4999,
            "annual_price": 49990,
            "max_users": 20,
            "max_products": 1500,
            "max_warehouses": 8,
            "max_monthly_sales_orders": 1500,
            "max_monthly_purchase_orders": 750,
            "max_monthly_stock_transfers": 400,
            "barcode_enabled": True,
            "advanced_inventory_enabled": True,
            "integrations_enabled": True,
            "ai_assistant_enabled": True,
        },
        {
            "id": 3,
            "code": "SCALE",
            "name": "Scale",
            "description": "For mature operations with broad teams, advanced inventory, and integrations.",
            "monthly_price": 9999,
            "annual_price": 99990,
            "max_users": None,
            "max_products": None,
            "max_warehouses": None,
            "max_monthly_sales_orders": None,
            "max_monthly_purchase_orders": None,
            "max_monthly_stock_transfers": None,
            "barcode_enabled": True,
            "advanced_inventory_enabled": True,
            "integrations_enabled": True,
            "ai_assistant_enabled": True,
        },
    ]

    try:
        for payload in plans:
            if repository.get_by_id(payload["id"]):
                continue
            repository.create(SubscriptionPlan(**payload))
        db.commit()
        logger.info("Ensured default subscription plans exist.")
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to ensure default subscription plans exist.")
