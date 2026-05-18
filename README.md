# Northstar Inventory

Northstar Inventory is a multi-tenant inventory management SaaS platform inspired by the workflows of modern business tools while keeping the product identity, interface, and implementation original. The stack follows the PRD: React frontend, FastAPI backend, MySQL database, SQLAlchemy + Alembic for persistence, and Docker Compose for local orchestration.

## Current Status

Phase 1 and Phase 2 are implemented:

- React frontend scaffold with routing, auth shell, and starter dashboard
- Real frontend login and tenant registration wired to the backend auth APIs
- FastAPI backend scaffold with config, DB session management, centralized error handling, and health routes
- JWT auth, password hashing, tenant-aware users, role checks, and super admin seeding
- MySQL service wired through Docker Compose
- Alembic migration for tenants and users
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

Frontend values live in `frontend/.env`:

- `VITE_API_BASE_URL`

## Auth and Roles

- `POST /api/auth/register` creates a tenant and the first `TENANT_ADMIN`
- `POST /api/auth/login` issues JWT access and refresh tokens
- `GET /api/auth/me` returns the current authenticated user
- Roles included in Milestone 2:
  - `SUPER_ADMIN`
  - `TENANT_ADMIN`
  - `INVENTORY_MANAGER`
  - `SALES_STAFF`
  - `PURCHASE_STAFF`
  - `VIEWER`

The backend enforces tenant isolation by resolving tenant access from the authenticated user rather than trusting tenant IDs from the frontend.

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

Run the frontend locally without Docker:

```bash
cd frontend
npm install
npm run dev
```

## Verification

- Backend syntax check: `python3 -m compileall backend/app`
- Frontend build: `npm run build` from `frontend/` after installing dependencies

## Milestone Roadmap

- Phase 3: categories, brands, vendors, customers, and warehouses
- Phase 4+: product inventory, transfers, orders, reports, audit logs, and AI features
