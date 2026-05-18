# UI Redesign Plan

## Current UI Structure

### Frontend Structure

- `frontend/src/main.jsx`
  Bootstraps React, router, auth provider, and the global stylesheet.
- `frontend/src/routes/index.jsx`
  Contains one public route (`/login`), one protected app shell route (`/`), and a fallback `*` route.
- `frontend/src/layouts/AppShell.jsx`
  Provides the current shell with a static sidebar, a simple top bar, and an outlet.
- `frontend/src/components/ProtectedRoute.jsx`
  Redirects unauthenticated users to `/login`.
- `frontend/src/contexts/AuthContext.jsx`
  Stores a local token in `localStorage`. No backend auth integration exists yet in the current branch.
- `frontend/src/lib/api.js`
  Exposes a single Axios client using `VITE_API_BASE_URL`.
- `frontend/src/pages/DashboardPage.jsx`
  Static phase-based starter dashboard.
- `frontend/src/pages/LoginPage.jsx`
  Local demo login form with no backend request.
- `frontend/src/pages/NotFoundPage.jsx`
  Basic fallback page.
- `frontend/src/styles/index.css`
  Single-file global CSS for auth, shell, dashboard cards, and responsive behavior.

### Current Routes

- `/login`
- `/`
- `*`

### Current API Usage

- Axios client exists but is not actively used by the current frontend pages.
- Current backend branch exposes only:
  - `GET /`
  - `GET /api/health/*`

### Current State Management

- Authentication state is in React context.
- Zustand is installed but not yet used.

## Missing UI Components

- App-wide design tokens and a denser SaaS-style component system
- Zoho-inspired shell behavior:
  - compact dark sidebar
  - grouped navigation
  - top header utilities
  - organization switcher
  - quick create menu
  - recent history menu
  - breadcrumb/header system
  - responsive drawer
- Reusable UI primitives:
  - icon system
  - page header
  - metric card
  - dashboard widget
  - data table
  - filter bar
  - search input
  - action menu
  - status badge
  - empty state
  - loading skeleton
  - modal
  - drawer
  - tabs
  - timeline
  - toast/alert
  - form section
  - form row
- Business screens:
  - inventory lists and detail pages
  - sales order workflow
  - purchase order workflow
  - warehouse screens
  - inventory transactions
  - reports landing and report views
  - users/tenants/admin pages
  - settings sub-navigation
  - onboarding/setup flow

## Page-By-Page Redesign Checklist

### Auth and Onboarding

- [ ] Redesign login page with split SaaS layout
- [ ] Add register page
- [ ] Add organization setup/onboarding page
- [ ] Improve form validation and error presentation

### Shell and Navigation

- [ ] Create design token system in CSS variables
- [ ] Build responsive `AppLayout`
- [ ] Add grouped sidebar navigation
- [ ] Add top navbar with search, quick create, recent history, notifications, settings, help, org switcher, user menu
- [ ] Add breadcrumbs and page header support
- [ ] Add collapsed sidebar and mobile drawer behavior

### Dashboard

- [ ] Create tenant dashboard widgets
- [ ] Create super admin dashboard widgets
- [ ] Add pending actions and recent activity widgets
- [ ] Add card-based empty and loading states
- [ ] Add simple chart/progress visuals without relying on unavailable backend data

### Inventory and Master Data

- [ ] Build items list page
- [ ] Build item detail page
- [ ] Build item create/edit form
- [ ] Build warehouses list and detail pages
- [ ] Build customers list
- [ ] Build vendors list
- [ ] Build low stock list
- [ ] Build inventory adjustments and stock transfer screens
- [ ] Build inventory transactions screen

### Orders

- [ ] Build sales orders list, detail, and form flow
- [ ] Build purchase orders list, detail, and form flow
- [ ] Add status timelines and action bars

### Reporting and Admin

- [ ] Build reports landing page
- [ ] Build report result page pattern
- [ ] Build activity logs and audit logs lists
- [ ] Build users page
- [ ] Build tenants page
- [ ] Build settings layout with sub-navigation
- [ ] Add subscription/plan usage placeholder
- [ ] Add AI assistant placeholder page

## Component Reuse Plan

- Use a single route metadata registry to drive:
  - sidebar groups
  - breadcrumbs
  - quick create links
  - page headers
- Use a reusable `DataTable` component for:
  - items
  - warehouses
  - vendors
  - customers
  - orders
  - transactions
  - reports
  - users
  - tenants
  - audit logs
  - notifications
- Use shared form primitives for:
  - item forms
  - sales order forms
  - purchase order forms
  - settings/profile forms
- Use shared status badge mapping for all workflow states
- Use a shared shell store in Zustand for:
  - sidebar state
  - mobile drawer state
  - quick create
  - recent history
  - notifications panel state

## Risk Areas

- Backend API coverage is still minimal on the current branch, so many screens must use clearly labeled placeholder or local-state behavior until backend modules exist.
- Current auth is local-token based. A future auth API integration should not require a UI rewrite.
- The redesign needs to feel Zoho-inspired in workflow and density without copying branding, wording, icons, or proprietary assets.
- Replacing the starter shell with a much richer route tree introduces navigation complexity, so route metadata and reusable page patterns are important.
- Responsive dense tables can become unwieldy on small screens, so stacked-card fallbacks will be needed for selected modules.
