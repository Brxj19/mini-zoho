# Northstar Inventory

Northstar Inventory is a multi-tenant inventory management SaaS platform inspired by the workflows of modern business tools while keeping the product identity, interface, and implementation original. The stack follows the PRD: React frontend, FastAPI backend, MySQL database, SQLAlchemy + Alembic for persistence, and Docker Compose for local orchestration.

## Current Status

Phase 1 through Phase 9 are implemented:

- React frontend scaffold with routing, auth shell, and starter dashboard
- Real frontend login and tenant registration wired to the backend auth APIs
- FastAPI backend scaffold with config, DB session management, centralized error handling, and health routes
- JWT auth, password hashing, tenant-aware users, role checks, and super admin seeding
- Tenant-scoped master data modules for categories, brands, vendors, customers, and warehouses
- Product catalog, warehouse stock, inventory transactions, stock in/out/adjustment APIs, and low-stock reporting
- Stock transfer workflow with DRAFT, IN_TRANSIT, COMPLETED, and CANCELLED statuses
- Purchase order workflow with DRAFT, ISSUED, PARTIALLY_RECEIVED, RECEIVED, and CANCELLED statuses
- Sales order workflow with DRAFT, CONFIRMED, PACKED, SHIPPED, DELIVERED, and CANCELLED statuses
- Tenant and Super Admin dashboard APIs
- Report APIs with CSV export for major inventory and order reports
- Audit log listing APIs and in-app notifications
- A full React SaaS shell with compact rail navigation, themed dashboard, operational lists, forms, detail views, reports, and notifications
- Ongoing UI/UX redesign work with standardized headers, in-shell list actions, lighter back navigation, and responsive table/layout polish
- MySQL service wired through Docker Compose
- Alembic migrations for tenants, users, master data tables, inventory core tables, stock transfers, purchase orders, sales orders, and notifications
- Environment variable examples for frontend and backend

## Project Structure

```text
.
├── backend
│   ├── alembic
│   ├── app
│   ├── Dockerfile
│   └── requirements.txt
├── docs
│   └── PRD.md
├── frontend
│   ├── src
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Local Setup

1. Copy the example environment files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

2. Start the stack:

```bash
docker compose up --build
```

3. Open the services:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Mailpit UI: `http://localhost:8025`

## Environment Variables

Backend values live in `backend/.env` and currently support:

- `APP_NAME`
- `API_V1_PREFIX`
- `ENV`
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `INITIAL_TENANT_STATUS`
- `CORS_ORIGINS`
- `SUPER_ADMIN_NAME`
- `SUPER_ADMIN_EMAIL`
- `SUPER_ADMIN_PASSWORD`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_FROM_NAME`
- `EMAIL_ENABLED`
- `SMS_PROVIDER`
- `OTP_TTL_MINUTES`
- `OTP_MAX_ATTEMPTS`

The backend also adds request-level middleware for:

- CORS handling
- request ID propagation via `X-Request-ID`
- response timing via `X-Process-Time-MS`
- basic security headers on API responses

Frontend values live in `frontend/.env`:

- `VITE_API_BASE_URL`

## Auth and Roles

- `POST /api/auth/register` creates a tenant and the first `TENANT_ADMIN`
- `POST /api/auth/login` issues JWT access and refresh tokens
- `GET /api/auth/me` returns the current authenticated user
- `POST /api/auth/request-email-verification` and `POST /api/auth/verify-email` support optional email verification
- `POST /api/auth/request-phone-verification` and `POST /api/auth/verify-phone` support optional phone verification
- Roles included in Milestone 2:
  - `SUPER_ADMIN`
  - `TENANT_ADMIN`
  - `INVENTORY_MANAGER`
  - `SALES_STAFF`
  - `PURCHASE_STAFF`
  - `VIEWER`

The backend enforces tenant isolation by resolving tenant access from the authenticated user rather than trusting tenant IDs from the frontend.

## Communication and Documents

- Development email is routed to Mailpit instead of a real provider.
- Development SMS is written to the local SMS outbox and exposed through `GET /api/dev/sms-outbox` for super admins.
- Invoice and bill PDFs are available through dedicated document endpoints and can be emailed as PDF attachments.

See [docs/COMMUNICATION_AND_DOCUMENT_SERVICES.md](docs/COMMUNICATION_AND_DOCUMENT_SERVICES.md) for details.

## Master Data APIs

Phase 3 adds tenant-aware CRUD APIs for:

- `GET/POST/PATCH/DELETE /api/categories`
- `GET/POST/PATCH/DELETE /api/brands`
- `GET/POST/PATCH/DELETE /api/vendors`
- `GET/POST/PATCH/DELETE /api/customers`
- `GET/POST/PATCH/DELETE /api/warehouses`

List endpoints support pagination, search, and status filtering. Warehouse lists also support `is_default` filtering. Delete actions archive records instead of hard deleting them.

## Product and Inventory APIs

Phase 4 adds:

- `GET/POST/PATCH/DELETE /api/products`
- `GET /api/products/{id}/stock`
- `GET /api/products/{id}/transactions`
- `GET /api/inventory/transactions`
- `POST /api/inventory/stock-in`
- `POST /api/inventory/stock-out`
- `POST /api/inventory/adjust`
- `GET /api/inventory/low-stock`

Stock is stored per warehouse in `warehouse_stock`, not on the product row itself. Every stock-changing action creates an immutable inventory transaction and an audit log entry.

## Stock Transfer APIs

Phase 5 adds:

- `GET /api/inventory/transfers`
- `POST /api/inventory/transfers`
- `GET /api/inventory/transfers/{id}`
- `PATCH /api/inventory/transfers/{id}`
- `POST /api/inventory/transfers/{id}/in-transit`
- `POST /api/inventory/transfers/{id}/complete`
- `POST /api/inventory/transfers/{id}/cancel`

Completing a transfer reduces source warehouse stock, increases destination warehouse stock, and creates matching `TRANSFER_OUT` and `TRANSFER_IN` inventory transactions for each transfer item.

## Purchase Order APIs

Phase 6 adds:

- `GET /api/purchase-orders`
- `POST /api/purchase-orders`
- `GET /api/purchase-orders/{id}`
- `PATCH /api/purchase-orders/{id}`
- `POST /api/purchase-orders/{id}/issue`
- `POST /api/purchase-orders/{id}/receive`
- `POST /api/purchase-orders/{id}/cancel`

Receiving stock updates `warehouse_stock`, creates `PURCHASE_RECEIVE` inventory transactions, supports partial receipts per line item, and blocks receipts on cancelled purchase orders.

## Sales Order APIs

Phase 7 adds:

- `GET /api/sales-orders`
- `POST /api/sales-orders`
- `GET /api/sales-orders/{id}`
- `PATCH /api/sales-orders/{id}`
- `POST /api/sales-orders/{id}/confirm`
- `POST /api/sales-orders/{id}/pack`
- `POST /api/sales-orders/{id}/ship`
- `POST /api/sales-orders/{id}/deliver`
- `POST /api/sales-orders/{id}/cancel`

Confirming a sales order reserves stock by warehouse, cancelling a confirmed workflow order releases that reservation, and delivering a shipped order converts reserved stock into a final `SALES_ORDER_DEDUCT` inventory transaction.

## Dashboard APIs

Phase 8 adds:

- `GET /api/dashboard/tenant`
- `GET /api/dashboard/super-admin`

The tenant dashboard returns core inventory, order, and notification metrics for the current tenant. The super admin dashboard returns cross-tenant SaaS-wide metrics and recent tenant activity.

## Report APIs

Phase 8 adds tenant-isolated reporting endpoints with filters and optional `?export=csv` support:

- `GET /api/reports/inventory-summary`
- `GET /api/reports/stock-movement`
- `GET /api/reports/low-stock`
- `GET /api/reports/warehouse-stock`
- `GET /api/reports/product-valuation`
- `GET /api/reports/purchase-orders`
- `GET /api/reports/sales-orders`

Each report supports relevant filters such as date range, warehouse, product, category, vendor, customer, and status where applicable.

## Audit Log APIs

Phase 8 adds:

- `GET /api/audit-logs`

Audit logs are immutable and tenant-scoped for tenant users. Super Admin users can query logs across tenants.

## Notification APIs

Phase 8 adds:

- `GET /api/notifications`
- `POST /api/notifications/{id}/read`
- `POST /api/notifications/read-all`

Low-stock events, purchase receiving, sales order status changes, suspicious large stock adjustments, and login activity now feed the dashboard and notification surfaces.

## Seeded Super Admin

When the backend starts after migrations, it ensures a default Super Admin exists using:

- Email: `SUPER_ADMIN_EMAIL`
- Password: `SUPER_ADMIN_PASSWORD`
- Name: `SUPER_ADMIN_NAME`

## Useful Commands

Run the backend locally without Docker:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Import the connected CSV seed archive:

```bash
cd backend
python -m app.cli.seed_from_csv --zip-path ../mini_zoho_connected_seed_csvs.zip --truncate-existing
```

The importer preserves explicit IDs, hashes `users.csv` passwords from `seed_password`, validates connected foreign keys, and checks `inventory_balance_audit.csv` after import. See [docs/CSV_SEED_IMPORT.md](docs/CSV_SEED_IMPORT.md) for the full workflow.

If you run the backend directly from your host machine instead of Docker, make sure `DATABASE_URL` uses a host your machine can reach, such as `127.0.0.1` or `localhost`. The default Compose-oriented value uses `mysql` as the hostname because that name resolves inside the Docker network.
If you already created the virtualenv before dependency updates, rerun `pip install -r requirements.txt` so the pinned backend hashing dependencies are refreshed.

Run the frontend locally without Docker:

```bash
cd frontend
npm install
npm run dev
```

## Verification

- Backend syntax check: `python3 -m compileall backend/app`
- Backend app import: `.venv/bin/python -c "import app.main; print('app-import-ok')"`
- Backend migrations: `.venv/bin/alembic upgrade head`
- Frontend build: `npm run build` from `frontend/` after installing dependencies

## Milestone Roadmap

- Phase 10: AI inventory assistant and reorder suggestions
