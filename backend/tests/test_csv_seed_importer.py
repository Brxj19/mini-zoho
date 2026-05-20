from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.models.audit_log import AuditLog
from app.models.product import Product
from app.models.user import User
from app.services.csv_seed_importer import CSVSeedImporter
from app.services.csv_seed_importer import parse_bool
from app.services.csv_seed_importer import parse_date_value
from app.services.csv_seed_importer import parse_datetime_value
from app.services.csv_seed_importer import parse_decimal_value
from app.services.csv_seed_importer import parse_json_value


def test_parse_bool_handles_true_false_and_empty() -> None:
    assert parse_bool("true") is True
    assert parse_bool("false") is False
    assert parse_bool("") is None


def test_parse_bool_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        parse_bool("maybe")


def test_parse_date_datetime_decimal_and_json_values() -> None:
    assert parse_date_value("2026-05-20") == date(2026, 5, 20)
    assert parse_datetime_value("2026-05-20T07:28:39+00:00") == datetime.fromisoformat("2026-05-20T07:28:39+00:00")
    assert parse_decimal_value("1499.50") == Decimal("1499.50")
    assert parse_json_value('{"status":"ACTIVE"}') == {"status": "ACTIVE"}


def test_coerce_row_hashes_user_seed_password() -> None:
    importer = CSVSeedImporter(zip_path="unused.zip", dry_run=True)
    row = {
        "id": "10",
        "tenant_id": "2",
        "name": "Aarav Patel",
        "email": "aarav@example.com",
        "seed_password": "Password123!",
        "role": "TENANT_ADMIN",
        "status": "ACTIVE",
        "last_login_at": "2026-05-20T09:15:00+00:00",
        "created_at": "2026-05-20T09:15:00+00:00",
        "updated_at": "2026-05-20T09:15:00+00:00",
    }

    coerced = importer._coerce_row(User, row)

    assert coerced["id"] == 10
    assert coerced["tenant_id"] == 2
    assert coerced["password_hash"] != "Password123!"
    assert isinstance(coerced["created_at"], datetime)
    assert coerced["role"].value == "TENANT_ADMIN"


def test_coerce_row_parses_json_and_nullable_fields() -> None:
    importer = CSVSeedImporter(zip_path="unused.zip", dry_run=True)
    row = {
        "id": "1",
        "tenant_id": "",
        "user_id": "1",
        "action": "TENANT_CREATED",
        "entity_type": "Tenant",
        "entity_id": "2",
        "old_value_json": "",
        "new_value_json": '{"company_name":"Bengaluru Gadget Hub"}',
        "ip_address": "127.0.0.1",
        "user_agent": "SeedBot/1.0",
        "created_at": "2026-05-20T09:15:00+00:00",
        "updated_at": "2026-05-20T09:15:00+00:00",
    }

    coerced = importer._coerce_row(AuditLog, row)

    assert coerced["tenant_id"] is None
    assert coerced["old_value_json"] is None
    assert coerced["new_value_json"] == {"company_name": "Bengaluru Gadget Hub"}


def test_coerce_row_parses_booleans_and_decimals_for_product() -> None:
    importer = CSVSeedImporter(zip_path="unused.zip", dry_run=True)
    row = {
        "id": "5",
        "tenant_id": "1",
        "name": "Mixer Grinder",
        "sku": "MIX-001",
        "barcode": "",
        "category_id": "3",
        "brand_id": "4",
        "vendor_id": "8",
        "description": "",
        "unit": "pcs",
        "cost_price": "1250.00",
        "selling_price": "1899.00",
        "reorder_level": "12",
        "serial_tracking_enabled": "false",
        "batch_tracking_enabled": "true",
        "expiry_tracking_enabled": "false",
        "warranty_tracking_enabled": "true",
        "status": "ACTIVE",
        "created_at": "2026-05-20T09:15:00+00:00",
        "updated_at": "2026-05-20T09:15:00+00:00",
    }

    coerced = importer._coerce_row(Product, row)

    assert coerced["cost_price"] == Decimal("1250.00")
    assert coerced["selling_price"] == Decimal("1899.00")
    assert coerced["barcode"] is None
    assert coerced["batch_tracking_enabled"] is True
    assert coerced["serial_tracking_enabled"] is False
