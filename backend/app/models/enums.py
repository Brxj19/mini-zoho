from __future__ import annotations

from enum import Enum


class RoleEnum(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    TENANT_ADMIN = "TENANT_ADMIN"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    SALES_STAFF = "SALES_STAFF"
    PURCHASE_STAFF = "PURCHASE_STAFF"
    VIEWER = "VIEWER"


class TenantStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class UserStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class RecordStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
