# Multi-Tenant Inventory Management System — Zoho-Inspired PRD

## 1. Project Title

Multi-Tenant Inventory Management and Order Fulfillment System

## 2. Project Summary

This project is a Zoho Inventory-inspired SaaS platform that allows multiple businesses/retailers to manage products, stock, warehouses, vendors, customers, purchase orders, sales orders, inventory movements, and reports from a single web application.

The system will support multi-tenant architecture, meaning each business/retailer will operate in an isolated workspace. A Super Admin can manage all tenants, while each tenant can have its own users, products, warehouses, vendors, customers, and inventory transactions.

The project will be built using:

- Frontend: React
- Backend: Python FastAPI
- Database: MySQL
- Authentication: JWT-based authentication
- Deployment: Docker-based setup

The goal is to build a production-style inventory SaaS similar in concept to Zoho Inventory, but with an original UI, original branding, and simplified implementation suitable for a GenAI training final project.

---

## 3. Problem Statement

Small and medium retailers often manage inventory using Excel sheets, manual registers, WhatsApp messages, and disconnected billing systems. This causes problems such as:

- Incorrect stock counts
- No clear history of stock movement
- Difficulty managing multiple warehouses
- No centralized product catalog
- No low-stock alerts
- Manual purchase and sales tracking
- Lack of role-based control
- Poor reporting and business visibility
- No tenant-level isolation for SaaS businesses

This project solves these problems by providing a centralized multi-tenant inventory platform where businesses can manage stock, orders, users, warehouses, vendors, customers, and reports efficiently.

---

## 4. Target Users

### 4.1 Super Admin

The platform owner who manages the entire SaaS application.

Responsibilities:

- Create and manage tenants
- View system-wide statistics
- Manage subscription plans
- Monitor tenant activity
- Disable or activate tenants
- View audit logs

### 4.2 Tenant Owner / Retailer Admin

The business owner or admin of a retailer/company.

Responsibilities:

- Manage company profile
- Manage users and roles
- Manage products
- Manage warehouses
- Manage vendors and customers
- View reports
- Configure inventory settings

### 4.3 Inventory Manager

The staff member responsible for daily inventory operations.

Responsibilities:

- Add/update products
- Record stock in
- Record stock out
- Transfer stock between warehouses
- View low-stock alerts
- Manage inventory transactions

### 4.4 Sales / Order Staff

The user responsible for creating and managing sales orders.

Responsibilities:

- Create sales orders
- Select customers
- Check stock availability
- Reserve or deduct stock
- Track order status

### 4.5 Purchase Staff

The user responsible for supplier and purchase workflows.

Responsibilities:

- Create purchase orders
- Select vendors
- Receive items
- Convert received items into stock
- Track purchase order status

---

## 5. Business Goals

The application should:

1. Provide a clean Zoho-like dashboard experience.
2. Support multiple tenants with strict data isolation.
3. Allow businesses to manage products, inventory, warehouses, vendors, customers, sales orders, and purchase orders.
4. Track every stock movement with transaction history.
5. Provide low-stock alerts and reorder suggestions.
6. Provide useful reports for decision-making.
7. Support role-based access control.
8. Provide a scalable FastAPI + MySQL backend.
9. Provide clean React UI with reusable components.
10. Be Docker-ready for local and production deployment.

---

## 6. Scope

### 6.1 MVP Scope

The MVP should include:

- Authentication
- Role-based authorization
- Tenant management
- Dashboard
- Product management
- Category management
- Brand management
- Vendor management
- Customer management
- Warehouse management
- Inventory stock in/out/adjustment
- Stock transfer between warehouses
- Purchase order management
- Sales order management
- Low-stock alerts
- Search, filters, pagination
- Reports
- Audit logs
- Docker setup

### 6.2 Post-MVP Scope

The following features can be implemented after the MVP:

- Barcode generation and scanning
- Serial number tracking
- Batch/lot tracking
- Expiry date tracking
- Invoice PDF generation
- Email notifications
- GST/tax module
- Payment integration
- Shipping integration
- Marketplace integrations
- AI inventory assistant
- Demand forecasting
- Invoice/bill parser using GenAI

---

## 7. Product Modules

## 7.1 Authentication Module

### Features

- User signup
- User login
- JWT access token
- JWT refresh token
- Logout
- Profile API
- Change password
- Forgot password placeholder
- Tenant-aware authentication
- Role-based access control

### Roles

- SUPER_ADMIN
- TENANT_ADMIN
- INVENTORY_MANAGER
- SALES_STAFF
- PURCHASE_STAFF
- VIEWER

### Acceptance Criteria

- User can login using email and password.
- JWT token is issued after successful login.
- APIs are protected using authentication middleware.
- Users can access only allowed modules based on their role.
- Tenant users cannot access another tenant’s data.

---

## 7.2 Tenant Management Module

### Purpose

The Super Admin should be able to create and manage businesses using the platform.

### Features

- Create tenant/company
- Update tenant details
- Activate/deactivate tenant
- View tenant list
- View tenant statistics
- Assign subscription plan
- View tenant users
- View tenant activity logs

### Tenant Fields

- id
- company_name
- contact_email
- phone
- address
- gst_number
- business_type
- status
- subscription_plan_id
- created_at
- updated_at

### Acceptance Criteria

- Super Admin can create tenants.
- Tenant Admin can only access their own tenant.
- Disabled tenants cannot access the platform.
- Every business-related table must include tenant_id.

---

## 7.3 User Management Module

### Purpose

Tenant Admins should be able to manage users inside their organization.

### Features

- Invite/create user
- Assign role
- Activate/deactivate user
- Reset password placeholder
- View user activity
- Filter users by role/status

### User Fields

- id
- tenant_id
- name
- email
- password_hash
- role
- status
- last_login_at
- created_at
- updated_at

### Acceptance Criteria

- Tenant Admin can create users only within their tenant.
- Super Admin can view all users.
- Inventory Manager cannot manage users.
- Deactivated users cannot login.

---

## 7.4 Dashboard Module

### Purpose

Provide a high-level overview of business activity.

### Tenant Dashboard Widgets

- Total products
- Total warehouses
- Total vendors
- Total customers
- Low-stock items
- Out-of-stock items
- Total sales orders
- Total purchase orders
- Recently updated inventory
- Inventory movement summary
- Top moving products
- Stock value summary

### Super Admin Dashboard Widgets

- Total tenants
- Active tenants
- Disabled tenants
- Total users
- Total products across tenants
- Total orders across tenants
- Tenant growth summary
- Recent platform activity

### Acceptance Criteria

- Dashboard data should be tenant-isolated.
- Super Admin dashboard should show system-wide data.
- Tenant dashboard should show only tenant-specific data.
- Dashboard should be responsive.

---

## 7.5 Product Management Module

### Purpose

Allow tenants to create and manage their product catalog.

### Features

- Add product/item
- Edit product
- Delete/archive product
- View product details
- Product image upload placeholder
- SKU uniqueness per tenant
- Category assignment
- Brand assignment
- Vendor assignment
- Product status: active/inactive
- Reorder level
- Opening stock
- Product search/filter

### Product Fields

- id
- tenant_id
- name
- sku
- barcode
- category_id
- brand_id
- vendor_id
- description
- unit
- cost_price
- selling_price
- reorder_level
- status
- created_at
- updated_at

### Acceptance Criteria

- Product SKU must be unique inside a tenant.
- Same SKU may exist in another tenant.
- Product quantity should not be stored only in the product table if multi-warehouse is enabled.
- Product stock should be calculated from warehouse stock records.
- Product deletion should be soft delete if transactions exist.

---

## 7.6 Category and Brand Module

### Features

- Create category
- Edit category
- Delete category
- Create brand
- Edit brand
- Delete brand
- Filter products by category and brand

### Category Fields

- id
- tenant_id
- name
- description
- status

### Brand Fields

- id
- tenant_id
- name
- description
- status

### Acceptance Criteria

- Categories and brands are tenant-specific.
- A category or brand cannot be deleted if products are assigned unless handled by soft delete.

---

## 7.7 Vendor/Supplier Management Module

### Purpose

Manage suppliers from whom the business purchases stock.

### Features

- Add vendor
- Edit vendor
- Delete/archive vendor
- View vendor details
- Vendor-wise purchase order history
- Search/filter vendors

### Vendor Fields

- id
- tenant_id
- name
- email
- phone
- gst_number
- address
- opening_balance
- status
- created_at
- updated_at

### Acceptance Criteria

- Vendors are tenant-specific.
- Purchase orders can be linked to vendors.
- Vendor cannot be deleted if purchase orders exist.

---

## 7.8 Customer Management Module

### Purpose

Manage customers for sales orders.

### Features

- Add customer
- Edit customer
- Delete/archive customer
- View customer details
- Customer-wise sales order history
- Search/filter customers

### Customer Fields

- id
- tenant_id
- name
- email
- phone
- gst_number
- billing_address
- shipping_address
- status
- created_at
- updated_at

### Acceptance Criteria

- Customers are tenant-specific.
- Sales orders can be linked to customers.
- Customer cannot be deleted if sales orders exist.

---

## 7.9 Warehouse Management Module

### Purpose

Allow businesses to manage stock across multiple warehouses or store locations.

### Features

- Add warehouse
- Edit warehouse
- Delete/archive warehouse
- Set default warehouse
- View warehouse stock
- Transfer stock between warehouses
- Warehouse-wise reports

### Warehouse Fields

- id
- tenant_id
- name
- code
- address
- city
- state
- country
- manager_name
- phone
- is_default
- status
- created_at
- updated_at

### Acceptance Criteria

- A tenant can have multiple warehouses.
- Every stock record must be linked to a warehouse.
- A warehouse with stock or transactions cannot be hard deleted.
- Tenant Admin can set one default warehouse.

---

## 7.10 Warehouse Stock Module

### Purpose

Maintain product quantity per warehouse.

### WarehouseStock Fields

- id
- tenant_id
- warehouse_id
- product_id
- quantity
- reserved_quantity
- available_quantity
- reorder_level
- updated_at

### Stock Formula

available_quantity = quantity - reserved_quantity

### Acceptance Criteria

- Stock should be tracked per product per warehouse.
- Available stock should consider reserved quantities.
- Stock cannot become negative unless negative stock is enabled in settings.
- All stock updates must create inventory transactions.

---

## 7.11 Inventory Transaction Module

### Purpose

Track every stock movement.

### Transaction Types

- STOCK_IN
- STOCK_OUT
- ADJUSTMENT
- TRANSFER_IN
- TRANSFER_OUT
- SALES_ORDER_RESERVE
- SALES_ORDER_DEDUCT
- SALES_ORDER_CANCEL_RELEASE
- PURCHASE_RECEIVE
- RETURN_IN
- DAMAGE_OUT

### InventoryTransaction Fields

- id
- tenant_id
- product_id
- warehouse_id
- source_warehouse_id
- destination_warehouse_id
- transaction_type
- quantity
- reference_type
- reference_id
- note
- created_by
- created_at

### Acceptance Criteria

- Every stock movement must generate a transaction record.
- Stock transfer should create TRANSFER_OUT and TRANSFER_IN records.
- Transactions should be immutable.
- Adjustments must require a reason/note.
- Transaction list should support search, filters, and pagination.

---

## 7.12 Stock Adjustment Module

### Purpose

Allow authorized users to correct inventory counts.

### Features

- Increase stock
- Decrease stock
- Add adjustment reason
- View adjustment history
- Audit adjustment action

### Acceptance Criteria

- Inventory Manager and Tenant Admin can perform adjustments.
- Viewer cannot perform adjustments.
- Adjustment reason is mandatory.
- Adjustment creates inventory transaction and audit log.

---

## 7.13 Stock Transfer Module

### Purpose

Move stock from one warehouse to another.

### Features

- Select source warehouse
- Select destination warehouse
- Select products
- Enter quantity
- Add notes
- Track transfer status

### Transfer Status

- DRAFT
- IN_TRANSIT
- COMPLETED
- CANCELLED

### Acceptance Criteria

- Source and destination warehouses must be different.
- Source warehouse must have enough available stock.
- Completing transfer updates both warehouses.
- Transfer creates transaction history.

---

## 7.14 Purchase Order Module

### Purpose

Allow businesses to order stock from vendors.

### Features

- Create purchase order
- Select vendor
- Add products and quantities
- Add expected delivery date
- PO status management
- Receive full or partial stock
- Convert received items into inventory
- View PO history

### Purchase Order Status

- DRAFT
- ISSUED
- PARTIALLY_RECEIVED
- RECEIVED
- CANCELLED

### PurchaseOrder Fields

- id
- tenant_id
- vendor_id
- po_number
- order_date
- expected_delivery_date
- status
- subtotal
- tax_amount
- total_amount
- notes
- created_by
- created_at
- updated_at

### PurchaseOrderItem Fields

- id
- purchase_order_id
- product_id
- warehouse_id
- quantity_ordered
- quantity_received
- unit_price
- tax_rate
- total_price

### Acceptance Criteria

- PO number must be unique per tenant.
- Receiving stock should increase warehouse stock.
- Partial receiving should be supported.
- Received stock should create PURCHASE_RECEIVE inventory transactions.
- Cancelled PO should not allow receiving.

---

## 7.15 Sales Order Module

### Purpose

Allow businesses to create sales orders for customers.

### Features

- Create sales order
- Select customer
- Add products
- Select warehouse
- Check stock availability
- Reserve stock
- Confirm order
- Cancel order
- Mark as packed/shipped/delivered placeholder
- View order history

### Sales Order Status

- DRAFT
- CONFIRMED
- PACKED
- SHIPPED
- DELIVERED
- CANCELLED

### SalesOrder Fields

- id
- tenant_id
- customer_id
- so_number
- order_date
- status
- subtotal
- tax_amount
- discount_amount
- total_amount
- notes
- created_by
- created_at
- updated_at

### SalesOrderItem Fields

- id
- sales_order_id
- product_id
- warehouse_id
- quantity
- unit_price
- tax_rate
- discount
- total_price

### Acceptance Criteria

- SO number must be unique per tenant.
- Confirmed order should reserve stock.
- Delivered order should deduct stock.
- Cancelled order should release reserved stock.
- Stock deduction should create SALES_ORDER_DEDUCT transaction.

---

## 7.16 Low-Stock Alert Module

### Purpose

Notify users when product stock is below reorder level.

### Features

- Low-stock dashboard card
- Product-wise reorder level
- Warehouse-wise reorder level
- Low-stock list
- Optional notification table
- Reorder suggestion

### Acceptance Criteria

- Product should appear in low-stock list when available stock <= reorder level.
- Low-stock alert should be warehouse-specific.
- Tenant Admin and Inventory Manager can view alerts.

---

## 7.17 Reports Module

### Purpose

Provide useful business insights.

### Reports

1. Inventory Summary Report
2. Stock Movement Report
3. Low-Stock Report
4. Out-of-Stock Report
5. Warehouse Stock Report
6. Product Valuation Report
7. Purchase Order Report
8. Sales Order Report
9. Vendor Purchase Report
10. Customer Sales Report
11. Inventory Adjustment Report
12. Audit Log Report

### Features

- Date range filter
- Warehouse filter
- Product filter
- Category filter
- Export to CSV
- Export to PDF placeholder

### Acceptance Criteria

- Reports must be tenant-isolated.
- Reports should support filters.
- CSV export should work for major reports.
- Dashboard should link to reports.

---

## 7.18 Audit Log Module

### Purpose

Track important user actions.

### AuditLog Fields

- id
- tenant_id
- user_id
- action
- entity_type
- entity_id
- old_value_json
- new_value_json
- ip_address
- user_agent
- created_at

### Events to Track

- Login
- Product created/updated/deleted
- Stock adjustment
- Stock transfer
- Purchase order created/received/cancelled
- Sales order created/confirmed/cancelled
- User created/role changed/deactivated
- Tenant activated/deactivated

### Acceptance Criteria

- Audit logs should be immutable.
- Tenant Admin can view logs of own tenant.
- Super Admin can view all logs.

---

## 7.19 Subscription Plan Module

### Purpose

Support SaaS-style limits similar to real inventory platforms.

### Features

- Create subscription plans
- Assign plan to tenant
- Enforce limits
- Show usage on tenant dashboard

### Example Plans

#### Free

- 1 user
- 1 warehouse
- 50 products
- 50 orders/month

#### Standard

- 3 users
- 2 warehouses
- 500 products
- 500 orders/month

#### Professional

- 10 users
- 5 warehouses
- 5000 products
- 3000 orders/month
- Barcode generation

#### Enterprise

- Unlimited users configurable
- Unlimited warehouses configurable
- Advanced reports
- API access placeholder
- AI assistant placeholder

### SubscriptionPlan Fields

- id
- name
- max_users
- max_warehouses
- max_products
- max_orders_per_month
- barcode_enabled
- ai_enabled
- advanced_reports_enabled
- price
- status

### Acceptance Criteria

- Tenant cannot exceed plan limits.
- Super Admin can update tenant subscription.
- Tenant dashboard should show plan usage.

---

## 7.20 Barcode Module

### MVP Status

Optional / Phase 2.

### Features

- Barcode field in product
- Auto-generate barcode value
- Barcode image generation placeholder
- Search product by barcode
- Scan barcode placeholder page

### Acceptance Criteria

- Barcode must be unique per tenant.
- Product can be searched using barcode.
- Barcode scanning UI can initially use manual input.

---

## 7.21 Serial and Batch Tracking Module

### MVP Status

Optional / Phase 2.

### Features

- Enable serial tracking per product
- Enable batch tracking per product
- Track expiry date
- Track manufacturing date
- Track warranty date

### Use Cases

- Electronics
- Medicines
- Food items
- Cosmetics
- Manufacturing

### Acceptance Criteria

- Serial number should be unique per tenant and product.
- Batch items can have expiry dates.
- Stock out should allow selecting batch/serial.

---

## 7.22 Notification Module

### Features

- In-app notifications
- Low-stock notification
- Order status notification
- Purchase receiving notification
- Suspicious stock adjustment notification

### Notification Fields

- id
- tenant_id
- user_id
- title
- message
- type
- is_read
- created_at

### Acceptance Criteria

- Users can view notifications.
- Users can mark notifications as read.
- Low-stock alerts should create notifications.

---

## 7.23 GenAI Features

### MVP GenAI Feature: AI Inventory Assistant

A chatbot-like assistant that answers tenant-specific inventory questions.

Example prompts:

- Which products are low in stock?
- Show me fast-moving products this month.
- Which warehouse has the highest stock value?
- Summarize today’s inventory activity.
- Which items should I reorder?

### AI Report Summary

Generate natural language summaries from reports.

Example:

"Inventory movement increased by 18% this month. The fastest-moving category was electronics. 12 products are below reorder level."

### Future AI Features

- Demand forecasting
- Smart reorder quantity suggestion
- Invoice/bill parser
- Anomaly detection in stock adjustments
- Auto product categorization
- SKU suggestion generator

### Acceptance Criteria

- AI should only use tenant-specific data.
- AI should never expose another tenant’s data.
- AI responses should be based on database queries, not hallucinated numbers.
- AI features should be disabled if the tenant plan does not support AI.

---

## 8. UI/UX Requirements

The UI should be inspired by modern SaaS tools like Zoho Inventory, but it must use original branding and design.

### Layout

- Left sidebar navigation
- Top header with search, notifications, profile menu
- Dashboard cards
- Data tables with filters
- Detail pages
- Create/edit forms
- Modal confirmations
- Responsive layout

### Main Sidebar Sections

1. Dashboard
2. Items
3. Inventory
4. Warehouses
5. Sales
6. Purchases
7. Customers
8. Vendors
9. Reports
10. Users
11. Settings

### Design Style

- Clean white/light UI
- Minimal borders
- Soft shadows
- Professional table layout
- Clear primary action buttons
- Status badges
- Responsive cards
- Consistent spacing
- Form validation messages
- Empty states
- Loading skeletons

### Important UI Pages

- Login
- Register
- Super Admin Dashboard
- Tenant Dashboard
- Product List
- Product Create/Edit
- Product Detail
- Warehouse List
- Warehouse Detail
- Inventory Transactions
- Stock Adjustment
- Stock Transfer
- Purchase Order List
- Purchase Order Create/Edit
- Purchase Order Detail
- Sales Order List
- Sales Order Create/Edit
- Sales Order Detail
- Vendor List
- Customer List
- Reports
- User Management
- Subscription Usage
- Settings
- AI Assistant

---

## 9. Backend Requirements

### Tech Stack

- Python FastAPI
- MySQL
- SQLAlchemy ORM
- Alembic migrations
- Pydantic schemas
- JWT authentication
- Role-based middleware
- Tenant isolation middleware
- Docker
- Docker Compose

### Backend Folder Structure

backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   └── dependencies.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── repositories/
│   ├── middleware/
│   └── utils/
├── alembic/
├── requirements.txt
├── Dockerfile
└── README.md

### API Design Rules

- Use REST conventions.
- Use plural resource names.
- Use proper HTTP status codes.
- Use pagination for list APIs.
- Use filters through query params.
- Never trust tenant_id from frontend for tenant users.
- Extract tenant_id from authenticated user token.
- Super Admin can pass tenant_id for admin-level views.
- All write operations should create audit logs.

---

## 10. Suggested API Endpoints

### Auth

- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- POST /api/auth/logout
- GET /api/auth/me
- PATCH /api/auth/change-password

### Tenants

- GET /api/tenants
- POST /api/tenants
- GET /api/tenants/{id}
- PATCH /api/tenants/{id}
- PATCH /api/tenants/{id}/status
- GET /api/tenants/{id}/usage

### Users

- GET /api/users
- POST /api/users
- GET /api/users/{id}
- PATCH /api/users/{id}
- PATCH /api/users/{id}/status
- PATCH /api/users/{id}/role

### Products

- GET /api/products
- POST /api/products
- GET /api/products/{id}
- PATCH /api/products/{id}
- DELETE /api/products/{id}
- GET /api/products/{id}/stock
- GET /api/products/{id}/transactions

### Categories

- GET /api/categories
- POST /api/categories
- PATCH /api/categories/{id}
- DELETE /api/categories/{id}

### Brands

- GET /api/brands
- POST /api/brands
- PATCH /api/brands/{id}
- DELETE /api/brands/{id}

### Vendors

- GET /api/vendors
- POST /api/vendors
- GET /api/vendors/{id}
- PATCH /api/vendors/{id}
- DELETE /api/vendors/{id}

### Customers

- GET /api/customers
- POST /api/customers
- GET /api/customers/{id}
- PATCH /api/customers/{id}
- DELETE /api/customers/{id}

### Warehouses

- GET /api/warehouses
- POST /api/warehouses
- GET /api/warehouses/{id}
- PATCH /api/warehouses/{id}
- DELETE /api/warehouses/{id}
- GET /api/warehouses/{id}/stock

### Inventory

- GET /api/inventory/transactions
- POST /api/inventory/stock-in
- POST /api/inventory/stock-out
- POST /api/inventory/adjust
- POST /api/inventory/transfer
- GET /api/inventory/low-stock

### Purchase Orders

- GET /api/purchase-orders
- POST /api/purchase-orders
- GET /api/purchase-orders/{id}
- PATCH /api/purchase-orders/{id}
- POST /api/purchase-orders/{id}/issue
- POST /api/purchase-orders/{id}/receive
- POST /api/purchase-orders/{id}/cancel

### Sales Orders

- GET /api/sales-orders
- POST /api/sales-orders
- GET /api/sales-orders/{id}
- PATCH /api/sales-orders/{id}
- POST /api/sales-orders/{id}/confirm
- POST /api/sales-orders/{id}/pack
- POST /api/sales-orders/{id}/ship
- POST /api/sales-orders/{id}/deliver
- POST /api/sales-orders/{id}/cancel

### Reports

- GET /api/reports/inventory-summary
- GET /api/reports/stock-movement
- GET /api/reports/low-stock
- GET /api/reports/warehouse-stock
- GET /api/reports/product-valuation
- GET /api/reports/purchase-orders
- GET /api/reports/sales-orders

### Audit Logs

- GET /api/audit-logs

### Notifications

- GET /api/notifications
- PATCH /api/notifications/{id}/read
- PATCH /api/notifications/read-all

### AI Assistant

- POST /api/ai/assistant/query
- POST /api/ai/reports/summary

---

## 11. Database Design

### Important Design Rule

Every tenant-owned business table must have tenant_id.

Examples:

- users
- products
- warehouses
- vendors
- customers
- sales_orders
- purchase_orders
- inventory_transactions
- audit_logs
- notifications

### Core Tables

- tenants
- users
- subscription_plans
- categories
- brands
- vendors
- customers
- warehouses
- products
- warehouse_stock
- inventory_transactions
- stock_transfers
- stock_transfer_items
- purchase_orders
- purchase_order_items
- sales_orders
- sales_order_items
- audit_logs
- notifications

### MySQL Requirements

- Use InnoDB.
- Use foreign keys.
- Add indexes for tenant_id.
- Add indexes for SKU, barcode, status, created_at.
- Use decimal type for money.
- Use transactions for stock updates.
- Use row-level locking or safe update patterns when changing stock.
- Prevent race conditions during stock deduction.

---

## 12. Tenant Isolation Rules

1. Tenant users must only access records where tenant_id equals their tenant_id.
2. Super Admin can access system-level records.
3. Frontend must not decide tenant access.
4. Backend must enforce tenant isolation.
5. All services/repositories must include tenant filtering.
6. Audit logs must include tenant_id.
7. AI assistant must only query data for the current tenant.

---

## 13. Search, Filters, and Pagination

### Common Requirements

All list pages should support:

- Search
- Filters
- Sort
- Pagination
- Page size
- Status filter

### Product Filters

- Name
- SKU
- Barcode
- Category
- Brand
- Vendor
- Stock status
- Price range
- Warehouse

### Order Filters

- Order number
- Customer/vendor
- Status
- Date range
- Total amount range

### Inventory Transaction Filters

- Product
- Warehouse
- Transaction type
- Date range
- User

---

## 14. Security Requirements

- Passwords must be hashed.
- JWT secret must come from environment variables.
- Use access token and refresh token.
- Validate all request payloads with Pydantic.
- Use role-based access checks.
- Protect against tenant data leakage.
- Never return password hashes.
- Use CORS configuration.
- Use centralized error handling.
- Add rate limiting placeholder for auth routes.

---

## 15. Deployment Requirements

### Docker Services

- frontend
- backend
- mysql

### Environment Variables

Backend:

- DATABASE_URL
- JWT_SECRET_KEY
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES
- REFRESH_TOKEN_EXPIRE_DAYS
- CORS_ORIGINS
- ENV

Frontend:

- VITE_API_BASE_URL

### Docker Compose

The project should run with:

docker compose up --build

---

## 16. Testing Requirements

### Backend Tests

- Auth tests
- Tenant isolation tests
- Product CRUD tests
- Inventory stock update tests
- Purchase order receive tests
- Sales order stock deduction tests
- Role permission tests

### Frontend Tests

- Login page render
- Dashboard render
- Product list render
- Form validation
- Protected route behavior

---

## 17. Non-Functional Requirements

- Clean and modular code
- Scalable folder structure
- Responsive UI
- Fast API response time
- Proper error messages
- Database indexes
- Meaningful commit messages
- Clean README
- Seed data for demo
- No hardcoded secrets
- No copied Zoho branding/assets

---

## 18. Project Milestones

### Milestone 1: Project Setup

- Setup frontend React app
- Setup FastAPI backend
- Setup MySQL
- Setup Docker Compose
- Setup environment files
- Setup base README

### Milestone 2: Auth and Tenant Foundation

- JWT auth
- Role-based access
- Tenant model
- User model
- Tenant isolation dependency/middleware
- Super Admin seed user

### Milestone 3: Master Data

- Categories
- Brands
- Vendors
- Customers
- Warehouses

### Milestone 4: Product and Stock

- Product CRUD
- Warehouse stock
- Stock in/out
- Adjustment
- Transaction history
- Low-stock alerts

### Milestone 5: Orders

- Purchase orders
- Receive purchase stock
- Sales orders
- Reserve/deduct stock
- Cancel order flow

### Milestone 6: Reports and Dashboard

- Tenant dashboard
- Super Admin dashboard
- Reports
- CSV export

### Milestone 7: SaaS and Audit

- Subscription plans
- Plan limits
- Audit logs
- Notifications

### Milestone 8: GenAI Features

- AI inventory assistant
- AI report summary
- Smart reorder suggestions placeholder

---

## 19. Definition of Done

The project is considered complete when:

- A Super Admin can create tenants.
- A Tenant Admin can manage users, products, warehouses, vendors, and customers.
- Inventory Manager can perform stock operations.
- Purchase orders can increase stock after receiving.
- Sales orders can reserve and deduct stock.
- Low-stock alerts work.
- Reports show useful tenant-specific data.
- Tenant isolation is enforced.
- Docker setup works.
- UI is clean, responsive, and professional.
- README explains setup and features.
- Demo seed data is available.