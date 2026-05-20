# CSV Seed Import

Northstar Inventory now includes a connected CSV seed importer for the packaged archive `mini_zoho_connected_seed_csvs.zip`.

## Archive Placement

Keep the ZIP anywhere accessible from your machine. The importer does not hardcode a path.

Example project-root placement:

```bash
mini_zoho_connected_seed_csvs.zip
```

## Run The Importer

From the backend directory:

```bash
cd backend
python -m app.cli.seed_from_csv --zip-path ../mini_zoho_connected_seed_csvs.zip --truncate-existing
```

Useful options:

```bash
python -m app.cli.seed_from_csv --zip-path ../mini_zoho_connected_seed_csvs.zip --dry-run
python -m app.cli.seed_from_csv --zip-path ../mini_zoho_connected_seed_csvs.zip --truncate-existing --tenant-id 3
```

Notes:
- `--truncate-existing` deletes data in reverse dependency order before import.
- `--dry-run` parses and validates without writing to MySQL.
- `--tenant-id` is available for future scoped imports. The current dataset is primarily intended for full connected imports.

## Passwords And Logins

`users.csv` ships `seed_password`, not `password_hash`.

The importer converts each password with `app.core.security.hash_password(...)` before insert.

Default seeded password for every imported login:

```text
Password123!
```

Quick login after import:

```text
Email: superadmin@northstar.demo
Password: Password123!
```

## Expected Row Counts

The connected archive currently expects:

- `subscription_plans`: 4
- `tenants`: 10
- `users`: 61
- `categories`: 80
- `brands`: 100
- `vendors`: 120
- `customers`: 400
- `warehouses`: 40
- `products`: 750
- `warehouse_stock`: 2484
- `purchase_orders`: 300
- `purchase_order_items`: 1001
- `purchase_receives`: 202
- `purchase_receive_items`: 671
- `bills`: 202
- `sales_orders`: 450
- `sales_order_items`: 1535
- `packages`: 283
- `package_items`: 963
- `invoices`: 245
- `stock_transfers`: 170
- `stock_transfer_items`: 375
- `sales_returns`: 38
- `sales_return_items`: 55
- `inventory_batches`: 332
- `inventory_serials`: 1079
- `inventory_transactions`: 5140
- `notifications`: 743
- `audit_logs`: 3520

The importer also reads `inventory_balance_audit.csv` after import to verify stock integrity, but it does not insert that file into the database.

## What The Importer Does

- reads `README_seed_data.md`
- reads `manifest.json`
- imports files in `import_order.txt` order
- preserves explicit IDs
- parses empty strings as `None` for nullable fields
- parses integers, decimals, dates, datetimes, booleans, enums, and JSON
- hashes user passwords from `seed_password`
- validates foreign keys where practical before each table insert
- resets MySQL auto-increment values after import
- compares imported warehouse stock against the ledger control CSV

## Troubleshooting

If import fails with foreign key errors:
- make sure you are importing the full archive
- make sure `import_order.txt` is unchanged
- prefer `--truncate-existing` when loading into a used database

If import fails with duplicate key errors:
- rerun with `--truncate-existing`
- or load into a clean database

If stock integrity reports mismatches:
- verify `inventory_balance_audit.csv` is present in the ZIP
- verify the import completed all the way through `inventory_transactions.csv`
- confirm the target DB was not partially populated with older seed data

If passwords do not work:
- verify the importer used `users.csv` from the archive
- verify the login password is `Password123!`

## Notes

- The selected connected seed archive came from your project workflow, not random runtime generation.
- Do not paste raw CSV rows directly into SQL manually.
- Do not paste raw `<script>` snippets into frontend pages for unrelated setup.
- If these CSVs or linked assets originate from third-party tooling, verify licensing and commercial usage rights before production use.
