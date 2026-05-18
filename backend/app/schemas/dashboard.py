from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class DashboardActivityItem(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: int | None
    created_at: datetime


class RecentTenantItem(BaseModel):
    id: int
    company_name: str
    contact_email: str
    status: str
    created_at: datetime


class TenantDashboardResponse(BaseModel):
    total_products: int
    total_warehouses: int
    total_customers: int
    total_vendors: int
    low_stock_items: int
    total_sales_orders: int
    total_purchase_orders: int
    inventory_value: Decimal
    unread_notifications: int
    recent_activities: list[DashboardActivityItem]


class SuperAdminDashboardResponse(BaseModel):
    total_tenants: int
    active_tenants: int
    total_users: int
    total_products: int
    total_sales_orders: int
    total_purchase_orders: int
    recent_tenants: list[RecentTenantItem]
    recent_activities: list[DashboardActivityItem]
