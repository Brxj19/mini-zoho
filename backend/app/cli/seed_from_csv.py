from __future__ import annotations

import argparse
from pathlib import Path

from app.services.csv_seed_importer import CSVSeedImporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import connected CSV seed data from a ZIP archive.")
    parser.add_argument("--zip-path", required=True, help="Path to the CSV seed ZIP archive.")
    parser.add_argument(
        "--truncate-existing",
        action="store_true",
        help="Delete existing rows in reverse dependency order before import.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate the ZIP without writing anything to the database.",
    )
    parser.add_argument(
        "--tenant-id",
        type=int,
        default=None,
        help="Optional tenant filter for future scoped imports.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    importer = CSVSeedImporter(
        zip_path=Path(args.zip_path),
        truncate_existing=args.truncate_existing,
        dry_run=args.dry_run,
        tenant_id=args.tenant_id,
    )
    results = importer.run()

    print("")
    print("CSV seed import summary")
    print("-----------------------")
    for result in results:
        status = "validated" if not result.inserted else "imported"
        print(f"{result.table_name}: {result.row_count} row(s) {status}")


if __name__ == "__main__":
    main()
