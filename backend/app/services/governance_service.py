from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder
from app.models.stock_transfer import StockTransfer
from app.models.subscription_plan import SubscriptionPlan
from app.models.tenant import Tenant
from app.models.warehouse import Warehouse
from app.repositories.subscription_plan_repository import SubscriptionPlanRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class LimitDefinition:
    label: str
    attr_name: str


class GovernanceService:
    LIMITS: dict[str, LimitDefinition] = {
        "users": LimitDefinition(label="users", attr_name="max_users"),
        "products": LimitDefinition(label="products", attr_name="max_products"),
        "warehouses": LimitDefinition(label="warehouses", attr_name="max_warehouses"),
        "monthly_sales_orders": LimitDefinition(label="monthly sales orders", attr_name="max_monthly_sales_orders"),
        "monthly_purchase_orders": LimitDefinition(label="monthly purchase orders", attr_name="max_monthly_purchase_orders"),
        "monthly_stock_transfers": LimitDefinition(label="monthly stock transfers", attr_name="max_monthly_stock_transfers"),
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.tenant_repository = TenantRepository(db)
        self.user_repository = UserRepository(db)
        self.plan_repository = SubscriptionPlanRepository(db)

    def get_plan_for_tenant(self, tenant_id: int) -> SubscriptionPlan | None:
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant or tenant.subscription_plan_id is None:
            return None
        return self.plan_repository.get_by_id(tenant.subscription_plan_id)

    def get_tenant_with_plan_or_404(self, tenant_id: int) -> tuple[Tenant, SubscriptionPlan | None]:
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")
        return tenant, self.get_plan_for_tenant(tenant_id)

    def assert_limit(self, *, tenant_id: int, metric_key: str, increment: int = 1) -> None:
        plan = self.get_plan_for_tenant(tenant_id)
        if not plan:
            return

        limit_def = self.LIMITS[metric_key]
        limit_value = getattr(plan, limit_def.attr_name)
        if limit_value is None:
            return

        current_value = self._metric_value(tenant_id=tenant_id, metric_key=metric_key)
        if current_value + increment > limit_value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The tenant has reached the {limit_def.label} limit for the {plan.name} plan.",
            )

    def assert_feature_enabled(self, *, tenant_id: int, feature_attr: str, feature_label: str) -> None:
        plan = self.get_plan_for_tenant(tenant_id)
        if not plan:
            return
        if not getattr(plan, feature_attr):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{feature_label} is not enabled on the {plan.name} plan.",
            )

    def get_usage_summary(self, tenant_id: int) -> dict[str, object]:
        plan = self.get_plan_for_tenant(tenant_id)
        total_users = self.user_repository.count_by_tenant(tenant_id)
        active_users = self.user_repository.count_active_by_tenant(tenant_id)
        total_products = self._count_model(Product, tenant_id)
        total_warehouses = self._count_model(Warehouse, tenant_id)
        total_purchase_orders = self._count_model(PurchaseOrder, tenant_id)
        total_sales_orders = self._count_model(SalesOrder, tenant_id)
        total_stock_transfers = self._count_model(StockTransfer, tenant_id)
        monthly_sales_orders = self._count_monthly_model(SalesOrder, tenant_id)
        monthly_purchase_orders = self._count_monthly_model(PurchaseOrder, tenant_id)
        monthly_stock_transfers = self._count_monthly_model(StockTransfer, tenant_id)

        metrics_current = {
            "users": total_users,
            "products": total_products,
            "warehouses": total_warehouses,
            "monthly_sales_orders": monthly_sales_orders,
            "monthly_purchase_orders": monthly_purchase_orders,
            "monthly_stock_transfers": monthly_stock_transfers,
        }

        limits = {}
        for key, limit_def in self.LIMITS.items():
            limit_value = getattr(plan, limit_def.attr_name) if plan else None
            current_value = metrics_current[key]
            percentage = None if limit_value in (None, 0) else round((current_value / limit_value) * 100, 2)
            limits[key] = {
                "label": limit_def.label,
                "current": current_value,
                "limit": limit_value,
                "remaining": None if limit_value is None else max(limit_value - current_value, 0),
                "percentage": percentage,
                "limit_reached": False if limit_value is None else current_value >= limit_value,
            }

        return {
            "tenant_id": tenant_id,
            "plan_id": plan.id if plan else None,
            "plan_code": plan.code if plan else None,
            "plan_name": plan.name if plan else None,
            "total_users": total_users,
            "active_users": active_users,
            "total_products": total_products,
            "total_warehouses": total_warehouses,
            "total_orders": total_purchase_orders + total_sales_orders,
            "total_purchase_orders": total_purchase_orders,
            "total_sales_orders": total_sales_orders,
            "total_stock_transfers": total_stock_transfers,
            "monthly_sales_orders": monthly_sales_orders,
            "monthly_purchase_orders": monthly_purchase_orders,
            "monthly_stock_transfers": monthly_stock_transfers,
            "limits": limits,
        }

    def _metric_value(self, *, tenant_id: int, metric_key: str) -> int:
        if metric_key == "users":
            return self.user_repository.count_by_tenant(tenant_id)
        if metric_key == "products":
            return self._count_model(Product, tenant_id)
        if metric_key == "warehouses":
            return self._count_model(Warehouse, tenant_id)
        if metric_key == "monthly_sales_orders":
            return self._count_monthly_model(SalesOrder, tenant_id)
        if metric_key == "monthly_purchase_orders":
            return self._count_monthly_model(PurchaseOrder, tenant_id)
        if metric_key == "monthly_stock_transfers":
            return self._count_monthly_model(StockTransfer, tenant_id)
        raise KeyError(metric_key)

    def _count_model(self, model, tenant_id: int) -> int:
        return int(self.db.scalar(select(func.count(model.id)).where(model.tenant_id == tenant_id)) or 0)

    def _count_monthly_model(self, model, tenant_id: int) -> int:
        now = datetime.now(UTC)
        start = datetime(now.year, now.month, 1, tzinfo=UTC)
        return int(self.db.scalar(select(func.count(model.id)).where(model.tenant_id == tenant_id, model.created_at >= start)) or 0)
