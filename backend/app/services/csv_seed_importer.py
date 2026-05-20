from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, Integer, JSON, Numeric, delete, func, insert, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.bill import Bill
from app.models.brand import Brand
from app.models.category import Category
from app.models.customer import Customer
from app.models.inventory_batch import InventoryBatch
from app.models.inventory_serial import InventorySerial
from app.models.inventory_transaction import InventoryTransaction
from app.models.invoice import Invoice
from app.models.notification import Notification
from app.models.package import Package
from app.models.package_item import PackageItem
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.purchase_receive import PurchaseReceive
from app.models.purchase_receive_item import PurchaseReceiveItem
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.sales_return import SalesReturn
from app.models.sales_return_item import SalesReturnItem
from app.models.stock_transfer import StockTransfer
from app.models.stock_transfer_item import StockTransferItem
from app.models.subscription_plan import SubscriptionPlan
from app.models.tenant import Tenant
from app.models.user import User
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock

CSV_MODEL_MAP = {
    "subscription_plans.csv": SubscriptionPlan,
    "tenants.csv": Tenant,
    "users.csv": User,
    "categories.csv": Category,
    "brands.csv": Brand,
    "vendors.csv": Vendor,
    "customers.csv": Customer,
    "warehouses.csv": Warehouse,
    "products.csv": Product,
    "warehouse_stock.csv": WarehouseStock,
    "purchase_orders.csv": PurchaseOrder,
    "purchase_order_items.csv": PurchaseOrderItem,
    "purchase_receives.csv": PurchaseReceive,
    "purchase_receive_items.csv": PurchaseReceiveItem,
    "bills.csv": Bill,
    "sales_orders.csv": SalesOrder,
    "sales_order_items.csv": SalesOrderItem,
    "packages.csv": Package,
    "package_items.csv": PackageItem,
    "invoices.csv": Invoice,
    "stock_transfers.csv": StockTransfer,
    "stock_transfer_items.csv": StockTransferItem,
    "sales_returns.csv": SalesReturn,
    "sales_return_items.csv": SalesReturnItem,
    "inventory_batches.csv": InventoryBatch,
    "inventory_serials.csv": InventorySerial,
    "inventory_transactions.csv": InventoryTransaction,
    "notifications.csv": Notification,
    "audit_logs.csv": AuditLog,
}

AUDIT_FILENAME = "inventory_balance_audit.csv"
IMPORT_ORDER_FILENAME = "import_order.txt"
MANIFEST_FILENAME = "manifest.json"
USERS_FILENAME = "users.csv"
DEFAULT_PASSWORD = "Password123!"
RESERVE_TRANSACTION_TYPES = {"SALES_ORDER_RESERVE", "SALES_ORDER_CANCEL_RELEASE"}


@dataclass(slots=True)
class TableImportResult:
    filename: str
    table_name: str
    row_count: int
    inserted: bool


class SeedValidationError(ValueError):
    """Raised when the connected seed archive is internally inconsistent."""


def parse_bool(value: str | None) -> bool | None:
    if value is None or value == "":
        return None

    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def parse_date_value(value: str | None) -> date | None:
    if value is None or value == "":
        return None
    return date.fromisoformat(value)


def parse_datetime_value(value: str | None) -> datetime | None:
    if value is None or value == "":
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def parse_decimal_value(value: str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(value)


def parse_json_value(value: str | None) -> Any:
    if value is None or value == "":
        return None
    return json.loads(value)


class CSVSeedImporter:
    def __init__(
        self,
        session_factory: sessionmaker[Session] | Callable[[], Session] = SessionLocal,
        *,
        zip_path: str | Path,
        truncate_existing: bool = False,
        dry_run: bool = False,
        tenant_id: int | None = None,
        echo: Callable[[str], None] = print,
    ) -> None:
        self.session_factory = session_factory
        self.zip_path = Path(zip_path)
        self.truncate_existing = truncate_existing
        self.dry_run = dry_run
        self.tenant_id = tenant_id
        self.echo = echo
        self._zip_file: zipfile.ZipFile | None = None
        self._manifest: dict[str, Any] | None = None
        self._import_order: list[str] | None = None
        self._selected_ids: dict[str, set[int]] = {}

    def run(self) -> list[TableImportResult]:
        self._open_archive()
        try:
            self._load_manifest()
            self._load_import_order()
            self._validate_archive_files()
            self._validate_archive_data()

            if self.truncate_existing and not self.dry_run:
                self._truncate_existing_rows()
            elif self.truncate_existing and self.dry_run:
                self.echo("Dry run enabled; existing database rows will not be truncated.")

            results: list[TableImportResult] = []

            for filename in self.import_order:
                model = CSV_MODEL_MAP[filename]
                result = self._import_table(filename, model)
                results.append(result)

            if not self.dry_run:
                self._reset_auto_increments()
                self._validate_inventory_balance()

            return results
        finally:
            if self._zip_file is not None:
                self._zip_file.close()

    @property
    def manifest(self) -> dict[str, Any]:
        if self._manifest is None:
            raise RuntimeError("Manifest has not been loaded.")
        return self._manifest

    @property
    def import_order(self) -> list[str]:
        if self._import_order is None:
            raise RuntimeError("Import order has not been loaded.")
        return self._import_order

    def _open_archive(self) -> None:
        if not self.zip_path.exists():
            raise FileNotFoundError(f"Seed ZIP not found: {self.zip_path}")
        self._zip_file = zipfile.ZipFile(self.zip_path)

    @property
    def zip_file(self) -> zipfile.ZipFile:
        if self._zip_file is None:
            raise RuntimeError("ZIP archive is not open.")
        return self._zip_file

    def _load_manifest(self) -> None:
        self._manifest = json.loads(self.zip_file.read(MANIFEST_FILENAME).decode("utf-8"))

    def _load_import_order(self) -> None:
        raw_text = self.zip_file.read(IMPORT_ORDER_FILENAME).decode("utf-8")
        filenames: list[str] = []
        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            match = re.match(r"^\d+\.\s+(?P<filename>.+)$", line)
            filenames.append(match.group("filename") if match else line)
        self._import_order = filenames

    def _validate_archive_files(self) -> None:
        archive_names = set(self.zip_file.namelist())
        required = {MANIFEST_FILENAME, IMPORT_ORDER_FILENAME, AUDIT_FILENAME, "README_seed_data.md", *self.import_order}
        missing = sorted(required - archive_names)
        if missing:
            raise ValueError(f"Seed ZIP is missing required files: {', '.join(missing)}")

    def _iter_csv_rows(self, filename: str) -> list[dict[str, str]]:
        data = self.zip_file.read(filename).decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(data))
        return list(reader)

    def _validate_archive_data(self) -> None:
        validation_errors: list[str] = []

        for filename in self.import_order:
            model = CSV_MODEL_MAP[filename]
            rows = self._iter_csv_rows(filename)
            rows = self._filter_rows_for_tenant(filename, rows)

            for column in model.__table__.columns:
                if not getattr(column, "unique", False):
                    continue

                grouped: dict[str, list[dict[str, str]]] = {}
                for row in rows:
                    raw_value = row.get(column.name)
                    if raw_value in (None, ""):
                        continue
                    grouped.setdefault(raw_value, []).append(row)

                for value, duplicates in grouped.items():
                    if len(duplicates) < 2:
                        continue
                    duplicate_ids = ", ".join(item.get("id", "?") for item in duplicates[:10])
                    validation_errors.append(
                        f"{filename}: duplicate unique value for {column.name}={value!r} on row id(s): {duplicate_ids}"
                    )

        if validation_errors:
            preview = "\n".join(f"- {message}" for message in validation_errors[:25])
            if len(validation_errors) > 25:
                preview += f"\n- ... and {len(validation_errors) - 25} more"
            raise SeedValidationError(
                "Connected seed archive failed preflight validation:\n"
                f"{preview}\n"
                "Fix the duplicate values in the CSV archive and rerun the importer."
            )

    def _filter_rows_for_tenant(self, filename: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        if self.tenant_id is None:
            return rows

        model = CSV_MODEL_MAP[filename]
        table = model.__table__
        fk_columns = {fk.parent.name: fk.column.table.name for fk in table.foreign_keys}
        filtered: list[dict[str, str]] = []

        for row in rows:
            keep = True
            tenant_raw = row.get("tenant_id")
            if tenant_raw is not None and tenant_raw != "":
                keep = int(tenant_raw) == self.tenant_id
            elif tenant_raw == "":
                keep = filename == USERS_FILENAME

            if not keep and fk_columns:
                keep = True
                for column_name, ref_table_name in fk_columns.items():
                    raw_value = row.get(column_name)
                    if not raw_value:
                        continue
                    selected = self._selected_ids.get(ref_table_name)
                    if selected is None:
                        continue
                    if int(raw_value) not in selected:
                        keep = False
                        break

            if keep:
                filtered.append(row)

        return filtered

    def _coerce_row(self, model: type[Any], row: dict[str, str]) -> dict[str, Any]:
        column_map = model.__table__.columns
        coerced: dict[str, Any] = {}
        row_copy = dict(row)

        if model is User:
            seed_password = row_copy.pop("seed_password", "") or DEFAULT_PASSWORD
            coerced["password_hash"] = hash_password(seed_password)

        unknown_columns = sorted(set(row_copy) - set(column_map.keys()))
        if unknown_columns:
            raise ValueError(
                f"{model.__tablename__} received unsupported CSV columns: {', '.join(unknown_columns)}"
            )

        for column in column_map:
            if column.name == "password_hash" and model is User:
                continue
            if column.name not in row_copy:
                continue
            raw_value = row_copy[column.name]
            coerced[column.name] = self._coerce_value_for_column(column, raw_value)

        return coerced

    def _coerce_value_for_column(self, column: Any, raw_value: str | None) -> Any:
        if raw_value == "":
            return None

        column_type = column.type
        if isinstance(column_type, Integer):
            return None if raw_value is None else int(raw_value)
        if isinstance(column_type, Numeric):
            return parse_decimal_value(raw_value)
        if isinstance(column_type, Boolean):
            return parse_bool(raw_value)
        if isinstance(column_type, DateTime):
            return parse_datetime_value(raw_value)
        if isinstance(column_type, Date):
            return parse_date_value(raw_value)
        if isinstance(column_type, JSON):
            return parse_json_value(raw_value)
        if isinstance(column_type, SAEnum):
            if raw_value is None:
                return None
            enum_class = column_type.enum_class
            return enum_class(raw_value) if enum_class else raw_value
        return raw_value

    def _import_table(self, filename: str, model: type[Any]) -> TableImportResult:
        raw_rows = self._iter_csv_rows(filename)
        filtered_rows = self._filter_rows_for_tenant(filename, raw_rows)
        coerced_rows = [self._coerce_row(model, row) for row in filtered_rows]
        self._selected_ids[model.__tablename__] = {
            int(row["id"]) for row in coerced_rows if row.get("id") is not None
        }

        expected_full_count = self.manifest["row_counts"].get(model.__tablename__)
        self.echo(
            f"{model.__tablename__}: parsed {len(coerced_rows)} row(s)"
            + (
                f" (manifest expects {expected_full_count})"
                if self.tenant_id is None and expected_full_count is not None
                else ""
            )
        )

        if self.dry_run:
            return TableImportResult(filename=filename, table_name=model.__tablename__, row_count=len(coerced_rows), inserted=False)

        if not coerced_rows:
            return TableImportResult(filename=filename, table_name=model.__tablename__, row_count=0, inserted=True)

        with self.session_factory() as session:
            with session.begin():
                self._validate_foreign_keys(session, model, coerced_rows)
                session.execute(insert(model), coerced_rows)

        return TableImportResult(filename=filename, table_name=model.__tablename__, row_count=len(coerced_rows), inserted=True)

    def _validate_foreign_keys(self, session: Session, model: type[Any], rows: list[dict[str, Any]]) -> None:
        if not rows:
            return

        for foreign_key in model.__table__.foreign_keys:
            column_name = foreign_key.parent.name
            ref_column = foreign_key.column
            ref_table_name = ref_column.table.name

            referenced_ids = {
                int(row[column_name])
                for row in rows
                if row.get(column_name) is not None
            }
            if not referenced_ids:
                continue

            ref_model = self._model_for_table_name(ref_table_name)
            existing_ids = set(
                session.scalars(
                    select(ref_model.id).where(ref_model.id.in_(referenced_ids))
                ).all()
            )
            missing_ids = sorted(referenced_ids - existing_ids)
            if missing_ids:
                sample = ", ".join(str(item) for item in missing_ids[:10])
                raise ValueError(
                    f"Foreign key validation failed for {model.__tablename__}.{column_name} -> {ref_table_name}.id; missing ids: {sample}"
                )

    def _truncate_existing_rows(self) -> None:
        for filename in reversed(self.import_order):
            model = CSV_MODEL_MAP[filename]
            with self.session_factory() as session:
                with session.begin():
                    deleted = session.execute(delete(model))
                self.echo(f"Cleared {deleted.rowcount or 0} existing row(s) from {model.__tablename__}")

    def _reset_auto_increments(self) -> None:
        with self.session_factory() as session:
            dialect_name = session.bind.dialect.name
            if dialect_name != "mysql":
                return

            for model in CSV_MODEL_MAP.values():
                next_value = session.scalar(select(func.coalesce(func.max(model.id), 0) + 1)) or 1
                session.execute(text(f"ALTER TABLE `{model.__tablename__}` AUTO_INCREMENT = {int(next_value)}"))
            session.commit()

    def _validate_inventory_balance(self) -> None:
        with self.session_factory() as session:
            physical_sums: dict[tuple[int, int, int], int] = {}
            reserve_sums: dict[tuple[int, int, int], int] = {}

            for tenant_id, warehouse_id, product_id, quantity, transaction_type in session.execute(
                select(
                    InventoryTransaction.tenant_id,
                    InventoryTransaction.warehouse_id,
                    InventoryTransaction.product_id,
                    InventoryTransaction.quantity,
                    InventoryTransaction.transaction_type,
                )
            ):
                key = (tenant_id, warehouse_id, product_id)
                transaction_name = (
                    transaction_type.value if hasattr(transaction_type, "value") else str(transaction_type)
                )
                if transaction_name in RESERVE_TRANSACTION_TYPES:
                    reserve_sums[key] = reserve_sums.get(key, 0) + int(quantity or 0)
                else:
                    physical_sums[key] = physical_sums.get(key, 0) + int(quantity or 0)

            stock_rows = {
                (tenant_id, warehouse_id, product_id): (quantity, reserved_quantity, available_quantity)
                for tenant_id, warehouse_id, product_id, quantity, reserved_quantity, available_quantity in session.execute(
                    select(
                        WarehouseStock.tenant_id,
                        WarehouseStock.warehouse_id,
                        WarehouseStock.product_id,
                        WarehouseStock.quantity,
                        WarehouseStock.reserved_quantity,
                        WarehouseStock.available_quantity,
                    )
                )
            }

        control_rows = self._iter_csv_rows(AUDIT_FILENAME)
        mismatches: list[str] = []

        for raw_row in control_rows:
            tenant_id = int(raw_row["tenant_id"])
            if self.tenant_id is not None and tenant_id != self.tenant_id:
                continue

            key = (tenant_id, int(raw_row["warehouse_id"]), int(raw_row["product_id"]))
            if key not in stock_rows:
                mismatches.append(f"{key}: warehouse_stock row missing after import")
                continue

            stock_quantity, stock_reserved, stock_available = stock_rows[key]
            ledger_quantity = physical_sums.get(key, 0)
            reserve_quantity = reserve_sums.get(key, 0)
            expected_quantity = int(raw_row["warehouse_stock_quantity"])
            expected_reserved = int(raw_row["warehouse_stock_reserved"])
            expected_available = int(raw_row["warehouse_stock_available"])

            if stock_quantity != expected_quantity or ledger_quantity != expected_quantity:
                mismatches.append(
                    f"{key}: quantity mismatch stock={stock_quantity} ledger={ledger_quantity} expected={expected_quantity}"
                )
            if stock_reserved != expected_reserved or reserve_quantity != expected_reserved:
                mismatches.append(
                    f"{key}: reserved mismatch stock={stock_reserved} ledger={reserve_quantity} expected={expected_reserved}"
                )
            if stock_available != expected_available:
                mismatches.append(
                    f"{key}: available mismatch stock={stock_available} expected={expected_available}"
                )

        if mismatches:
            self.echo("Inventory balance audit mismatches found:")
            for mismatch in mismatches[:50]:
                self.echo(f"  - {mismatch}")
            if len(mismatches) > 50:
                self.echo(f"  ... and {len(mismatches) - 50} more")
        else:
            self.echo("Inventory balance audit passed.")

    def _model_for_table_name(self, table_name: str) -> type[Any]:
        for model in CSV_MODEL_MAP.values():
            if model.__tablename__ == table_name:
                return model
        raise KeyError(f"No model is registered for table {table_name}")
