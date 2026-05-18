from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    country: str = Field(min_length=2, max_length=80)
    phone: str = Field(min_length=6, max_length=30)


class SetupRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=160)
    industry: str = Field(min_length=2, max_length=80)
    address: str = Field(min_length=2, max_length=255)
    currency: str = Field(min_length=2, max_length=10)
    timezone: str = Field(min_length=2, max_length=60)


class StatusUpdateRequest(BaseModel):
    status: str = Field(min_length=2, max_length=40)


class CreateItemRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    sku: str = Field(min_length=2, max_length=80)
    category_name: str = Field(min_length=2, max_length=120)
    brand_name: str = Field(min_length=2, max_length=120)
    unit: str = Field(min_length=1, max_length=20)
    barcode: str | None = Field(default=None, max_length=80)
    selling_price: float = Field(ge=0)
    cost_price: float = Field(ge=0)
    stock_on_hand: int = Field(ge=0)
    reorder_level: int = Field(ge=0)
    sales_description: str | None = None
    purchase_description: str | None = None


class OrderLineRequest(BaseModel):
    item_name: str = Field(min_length=2, max_length=160)
    warehouse_name: str | None = Field(default=None, max_length=120)
    quantity: int = Field(ge=1)
    rate: float = Field(ge=0)


class CreateSalesOrderRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=140)
    reference_number: str | None = Field(default=None, max_length=80)
    order_date: str = Field(min_length=8, max_length=20)
    expected_shipment_date: str | None = Field(default=None, max_length=20)
    notes: str | None = None
    items: list[OrderLineRequest] = Field(min_length=1)
    status: str = Field(default="DRAFT", min_length=2, max_length=40)


class CreatePurchaseOrderRequest(BaseModel):
    vendor_name: str = Field(min_length=2, max_length=140)
    reference_number: str | None = Field(default=None, max_length=80)
    order_date: str = Field(min_length=8, max_length=20)
    expected_delivery_date: str | None = Field(default=None, max_length=20)
    notes: str | None = None
    items: list[OrderLineRequest] = Field(min_length=1)
    status: str = Field(default="DRAFT", min_length=2, max_length=40)
