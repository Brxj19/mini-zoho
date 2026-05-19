# PRD Execution Roadmap

This roadmap reflects the current `main` branch state compared against [PRD.md](./PRD.md).

## 1. Must Finish For PRD

### 1.1 Master Data UI Completion
- Add category management UI: list, create, edit, detail
- Add brand management UI: list, create, edit, detail
- Add warehouse create/edit UI
- Improve warehouse detail with stronger stock and transaction context

### 1.2 Operations UI Completion
- Add stock transfer create/edit/status actions in the frontend
- Add richer purchase order actions: issue, receive, cancel
- Add richer sales order actions: confirm, pack, ship, deliver, cancel
- Add low-stock dedicated page and better report drilldown

### 1.3 Reports Completion
- Add missing backend reports:
  - out-of-stock
  - vendor purchase
  - customer sales
  - inventory adjustment
  - audit log report endpoint
- Add report filter controls in the frontend:
  - date range
  - warehouse
  - product
  - category
  - status where relevant

### 1.4 Admin UI Completion
- Add user detail/create/edit flows
- Add tenant detail/create/edit flows
- Add tenant usage visibility in the frontend

### 1.5 PRD Compliance Gaps
- Add archive restrictions for linked categories, brands, vendors, and customers
- Add forgot password and reset password placeholders
- Expose audit log report in the report router/UI

## 2. Good Production Hardening

### 2.1 Backend Hardening
- Remove dead compatibility modules not used by the active app
- Add stronger validation and domain rules around linked archives
- Improve observability around DB errors and request tracing
- Add higher-confidence transactional tests around stock/order workflows

### 2.2 Frontend Hardening
- Remove dead legacy pages and stores
- Strengthen role-based action visibility
- Add better loading/empty/error states to detail and workbench screens
- Add richer inline action feedback for order and stock workflows

### 2.3 UX Consistency
- Unify table filters and server-side query wiring
- Add consistent breadcrumbs and page actions across all modules
- Improve navigation discoverability for admin/master-data modules

## 3. Nice-To-Have Post-MVP

### 3.1 Subscription And SaaS Governance
- Subscription plan model and APIs
- Tenant plan assignment
- Usage limit enforcement
- Tenant plan usage UI

### 3.2 Advanced Inventory
- Barcode generation/search UX improvements
- Serial tracking
- Batch tracking
- Expiry and warranty tracking

### 3.3 Extended Business Workflows
- First-class packages module
- First-class invoices module
- First-class sales returns module
- First-class purchase receives module
- First-class bills/payables module

### 3.4 AI And Integrations
- AI assistant backend and frontend
- Reorder suggestions
- Shipping, payment, and marketplace placeholders or integrations

## 4. Current Build Order

1. Master data UI completion
2. Operations UI completion
3. Reports completion
4. Admin UI completion
5. Hardening cleanup
6. Subscription and post-MVP features

## 5. Current Active Work

This pass starts with:

- Category management UI
- Brand management UI
- Warehouse create/edit UI
