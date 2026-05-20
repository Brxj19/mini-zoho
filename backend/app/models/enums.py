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


class InventoryTransactionTypeEnum(str, Enum):
    STOCK_IN = "STOCK_IN"
    STOCK_OUT = "STOCK_OUT"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    SALES_ORDER_RESERVE = "SALES_ORDER_RESERVE"
    SALES_ORDER_DEDUCT = "SALES_ORDER_DEDUCT"
    SALES_ORDER_CANCEL_RELEASE = "SALES_ORDER_CANCEL_RELEASE"
    PURCHASE_RECEIVE = "PURCHASE_RECEIVE"
    RETURN_IN = "RETURN_IN"
    DAMAGE_OUT = "DAMAGE_OUT"


class InventorySerialStatusEnum(str, Enum):
    IN_STOCK = "IN_STOCK"
    ALLOCATED = "ALLOCATED"
    SOLD = "SOLD"
    RETURNED = "RETURNED"


class StockTransferStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    IN_TRANSIT = "IN_TRANSIT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PurchaseOrderStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class SalesOrderStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class NotificationTypeEnum(str, Enum):
    LOW_STOCK = "LOW_STOCK"
    ORDER_STATUS = "ORDER_STATUS"
    PURCHASE_RECEIVE = "PURCHASE_RECEIVE"
    STOCK_ALERT = "STOCK_ALERT"
    SYSTEM = "SYSTEM"


class OtpChannelEnum(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"


class OtpPurposeEnum(str, Enum):
    SIGNUP_VERIFY = "SIGNUP_VERIFY"
    LOGIN_2FA = "LOGIN_2FA"
    PHONE_VERIFY = "PHONE_VERIFY"
    PASSWORD_RESET = "PASSWORD_RESET"


class OtpChallengeStatusEnum(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"
    BLOCKED = "BLOCKED"


class PackageStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class InvoiceStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    VOID = "VOID"


class SalesReturnStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    RECEIVED = "RECEIVED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class PurchaseReceiveStatusEnum(str, Enum):
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"


class BillStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    PAID = "PAID"
    VOID = "VOID"
