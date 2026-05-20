from __future__ import annotations

import argparse

from app.core.database import SessionLocal
from app.services.inventory_engine import InventoryEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reconcile warehouse stock against inventory transactions.")
    parser.add_argument("--tenant-id", required=True, type=int, help="Tenant ID to reconcile.")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply the reconciled values back to warehouse_stock after printing mismatches.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    db = SessionLocal()
    try:
        engine = InventoryEngine(db)
        results = engine.reconcile_tenant(tenant_id=args.tenant_id, fix=args.fix)
        mismatches = [
            result
            for result in results
            if (
                result.expected_quantity != result.actual_quantity
                or result.expected_reserved_quantity != result.actual_reserved_quantity
                or result.expected_available_quantity != result.actual_available_quantity
            )
        ]

        if not mismatches:
            print("No inventory mismatches found.")
            return

        print("")
        print("Inventory reconciliation")
        print("------------------------")
        for mismatch in mismatches:
            status = "fixed" if mismatch.fixed else "dry-run"
            print(
                f"tenant={mismatch.tenant_id} product={mismatch.product_id} warehouse={mismatch.warehouse_id} "
                f"quantity {mismatch.actual_quantity}->{mismatch.expected_quantity}, "
                f"reserved {mismatch.actual_reserved_quantity}->{mismatch.expected_reserved_quantity}, "
                f"available {mismatch.actual_available_quantity}->{mismatch.expected_available_quantity} [{status}]"
            )

        if args.fix:
            db.commit()
        else:
            db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
