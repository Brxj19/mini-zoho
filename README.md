# Northstar Inventory

Northstar Inventory is a multi-tenant inventory management SaaS platform inspired by the workflows of modern business tools while keeping the product identity, interface, and implementation original. The stack follows the PRD: React frontend, FastAPI backend, MySQL database, SQLAlchemy + Alembic for persistence, and Docker Compose for local orchestration.

## Current Status

The repository currently includes:

- React + Vite frontend scaffold
- FastAPI backend scaffold with health routes
- MySQL and Docker Compose setup
- Alembic migration wiring for backend evolution
- A Zoho-inspired frontend redesign branch with:
  - token-based design system
  - compact dark sidebar and top utility bar
  - responsive app shell and onboarding flow
  - dashboard, tables, forms, reports, and settings UI patterns
  - clearly marked placeholder modules where backend APIs are not available yet

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
- `CORS_ORIGINS`
- `SUPER_ADMIN_EMAIL`
- `SUPER_ADMIN_PASSWORD`

Frontend values live in `frontend/.env`:

- `VITE_API_BASE_URL`

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

## UI Redesign Note

The frontend redesign keeps Northstar Inventory branding original while following dense inventory SaaS workflow patterns such as grouped sidebar navigation, quick-create actions, compact data tables, sectioned forms, and card-based dashboards. The implementation plan for this redesign is tracked in `docs/UI_REDESIGN_PLAN.md`.

## Milestone Roadmap

- Phase 2: authentication, tenant model, user model, roles, and tenant isolation
- Phase 3: categories, brands, vendors, customers, and warehouses
- Phase 4+: product inventory, transfers, orders, reports, audit logs, and AI features
