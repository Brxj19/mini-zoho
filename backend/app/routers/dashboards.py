from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.models.enums import RoleEnum
from app.models.user import User
from app.schemas.dashboard import (
    DashboardActivityItem,
    RecentTenantItem,
    SuperAdminDashboardResponse,
    TenantDashboardResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/tenant", response_model=TenantDashboardResponse)
def tenant_dashboard(db: DbSession, current_user: CurrentUser) -> TenantDashboardResponse:
    data = DashboardService(db).get_tenant_dashboard(current_user=current_user)
    return TenantDashboardResponse(
        total_products=data["total_products"],
        total_warehouses=data["total_warehouses"],
        total_customers=data["total_customers"],
        total_vendors=data["total_vendors"],
        low_stock_items=data["low_stock_items"],
        total_sales_orders=data["total_sales_orders"],
        total_purchase_orders=data["total_purchase_orders"],
        inventory_value=data["inventory_value"],
        unread_notifications=data["unread_notifications"],
        recent_activities=[
            DashboardActivityItem(
                id=item.id,
                action=item.action,
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                created_at=item.created_at,
            )
            for item in data["recent_activities"]
        ],
    )


@router.get("/super-admin", response_model=SuperAdminDashboardResponse)
def super_admin_dashboard(
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> SuperAdminDashboardResponse:
    data = DashboardService(db).get_super_admin_dashboard(current_user=current_user)
    return SuperAdminDashboardResponse(
        total_tenants=data["total_tenants"],
        active_tenants=data["active_tenants"],
        total_users=data["total_users"],
        total_products=data["total_products"],
        total_sales_orders=data["total_sales_orders"],
        total_purchase_orders=data["total_purchase_orders"],
        recent_tenants=[
            RecentTenantItem(
                id=item.id,
                company_name=item.company_name,
                contact_email=item.contact_email,
                status=item.status.value,
                created_at=item.created_at,
            )
            for item in data["recent_tenants"]
        ],
        recent_activities=[
            DashboardActivityItem(
                id=item.id,
                action=item.action,
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                created_at=item.created_at,
            )
            for item in data["recent_activities"]
        ],
    )
