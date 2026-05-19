from __future__ import annotations

from sqlalchemy import func, select
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.enums import RoleEnum, TenantStatusEnum, UserStatusEnum
from app.models.sales_order import SalesOrder
from app.models.stock_transfer import StockTransfer
from app.models.tenant import Tenant
from app.models.user import User
from app.models.warehouse import Warehouse
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.tenant_repository = TenantRepository(db)
        self.user_repository = UserRepository(db)

    def create_tenant(self, payload: TenantCreate) -> Tenant:
        admin_fields = [payload.admin_name, payload.admin_email, payload.admin_password]
        if any(admin_fields) and not all(admin_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="admin_name, admin_email, and admin_password must be provided together.",
            )

        if payload.admin_email and self.user_repository.get_by_email(payload.admin_email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin email is already in use.")

        tenant = Tenant(
            company_name=payload.company_name,
            contact_email=payload.contact_email,
            phone=payload.phone,
            address=payload.address,
            gst_number=payload.gst_number,
            business_type=payload.business_type,
            status=TenantStatusEnum.ACTIVE,
        )

        try:
            self.tenant_repository.create(tenant)
            if payload.admin_email and payload.admin_name and payload.admin_password:
                admin_user = User(
                    tenant_id=tenant.id,
                    name=payload.admin_name,
                    email=payload.admin_email,
                    password_hash=hash_password(payload.admin_password),
                    role=RoleEnum.TENANT_ADMIN,
                    status=UserStatusEnum.ACTIVE,
                )
                self.user_repository.create(admin_user)
            self.db.commit()
            self.db.refresh(tenant)
        except Exception:
            self.db.rollback()
            raise

        return tenant

    def get_tenant_or_404(self, tenant_id: int) -> Tenant:
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")
        return tenant

    def update_tenant(self, tenant: Tenant, payload: TenantUpdate) -> Tenant:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return tenant

        self.tenant_repository.update(tenant, updates)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def update_status(self, tenant: Tenant, status_value: TenantStatusEnum) -> Tenant:
        self.tenant_repository.update(tenant, {"status": status_value})
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def get_usage(self, tenant_id: int) -> dict[str, int]:
        total_users = self.user_repository.count_by_tenant(tenant_id)
        active_users = self.user_repository.count_active_by_tenant(tenant_id)
        total_products = self._count_model(Product, tenant_id)
        total_warehouses = self._count_model(Warehouse, tenant_id)
        total_purchase_orders = self._count_model(PurchaseOrder, tenant_id)
        total_sales_orders = self._count_model(SalesOrder, tenant_id)
        total_stock_transfers = self._count_model(StockTransfer, tenant_id)
        return {
            "tenant_id": tenant_id,
            "total_users": total_users,
            "active_users": active_users,
            "total_products": total_products,
            "total_warehouses": total_warehouses,
            "total_orders": total_purchase_orders + total_sales_orders,
            "total_purchase_orders": total_purchase_orders,
            "total_sales_orders": total_sales_orders,
            "total_stock_transfers": total_stock_transfers,
        }

    def _count_model(self, model, tenant_id: int) -> int:
        return int(self.db.scalar(select(func.count(model.id)).where(model.tenant_id == tenant_id)) or 0)
