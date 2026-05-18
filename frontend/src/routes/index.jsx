import { createBrowserRouter } from "react-router-dom";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { AppShell } from "../layouts/AppShell";
import { DashboardPage } from "../pages/DashboardPage";
import { ItemDetailPage } from "../pages/ItemDetailPage";
import { ItemFormPage } from "../pages/ItemFormPage";
import { ListPage } from "../pages/ListPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { OrderDetailPage } from "../pages/OrderDetailPage";
import { OrderFormPage } from "../pages/OrderFormPage";
import { PlaceholderModulePage } from "../pages/PlaceholderModulePage";
import { RegisterPage } from "../pages/RegisterPage";
import { ReportDetailPage } from "../pages/ReportDetailPage";
import { ReportsPage } from "../pages/ReportsPage";
import { SettingsPage } from "../pages/SettingsPage";
import { SetupPage } from "../pages/SetupPage";
import { WarehouseDetailPage } from "../pages/WarehouseDetailPage";

function withTitle(title, section = "") {
  return {
    title,
    breadcrumb: title,
    section,
  };
}

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    path: "/setup",
    element: (
      <ProtectedRoute>
        <SetupPage />
      </ProtectedRoute>
    ),
    handle: withTitle("Setup", "Onboarding"),
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    handle: {
      title: "Dashboard",
      breadcrumb: "Home",
      section: "Main",
    },
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "items", element: <ListPage moduleKey="items" />, handle: withTitle("Items", "Inventory") },
      { path: "items/new", element: <ItemFormPage />, handle: withTitle("New Item", "Inventory") },
      { path: "items/:itemId", element: <ItemDetailPage />, handle: { title: "Item Detail", breadcrumb: "Item Detail", section: "Inventory" } },
      { path: "item-groups", element: <PlaceholderModulePage title="Item Groups" description="Future grouping, variant, and catalog hierarchy workspace." actionLabel="Back to items" actionTo="/items" />, handle: withTitle("Item Groups", "Inventory") },
      { path: "inventory-adjustments", element: <ListPage moduleKey="inventory-adjustments" />, handle: withTitle("Inventory Adjustments", "Inventory") },
      { path: "stock-transfers", element: <ListPage moduleKey="stock-transfers" />, handle: withTitle("Stock Transfers", "Inventory") },
      { path: "warehouses", element: <ListPage moduleKey="warehouses" />, handle: withTitle("Warehouses", "Inventory") },
      { path: "warehouses/:warehouseId", element: <WarehouseDetailPage />, handle: { title: "Warehouse Detail", breadcrumb: "Warehouse Detail", section: "Inventory" } },
      { path: "low-stock", element: <ListPage moduleKey="low-stock" />, handle: withTitle("Low Stock", "Inventory") },
      { path: "customers", element: <ListPage moduleKey="customers" />, handle: withTitle("Customers", "Sales") },
      { path: "sales-orders", element: <ListPage moduleKey="sales-orders" />, handle: withTitle("Sales Orders", "Sales") },
      { path: "sales-orders/new", element: <OrderFormPage type="sales" />, handle: withTitle("New Sales Order", "Sales") },
      { path: "sales-orders/:orderId", element: <OrderDetailPage type="sales" />, handle: { title: "Sales Order Detail", breadcrumb: "Sales Order Detail", section: "Sales" } },
      { path: "packages", element: <PlaceholderModulePage title="Packages" description="Packaging workflow placeholder pending backend support." actionLabel="Back to sales orders" actionTo="/sales-orders" />, handle: withTitle("Packages", "Sales") },
      { path: "invoices", element: <PlaceholderModulePage title="Invoices" description="Invoice management placeholder pending backend support." actionLabel="Back to sales orders" actionTo="/sales-orders" />, handle: withTitle("Invoices", "Sales") },
      { path: "sales-returns", element: <PlaceholderModulePage title="Sales Returns" description="Returns management placeholder pending backend support." actionLabel="Back to sales orders" actionTo="/sales-orders" />, handle: withTitle("Sales Returns", "Sales") },
      { path: "vendors", element: <ListPage moduleKey="vendors" />, handle: withTitle("Vendors", "Purchases") },
      { path: "purchase-orders", element: <ListPage moduleKey="purchase-orders" />, handle: withTitle("Purchase Orders", "Purchases") },
      { path: "purchase-orders/new", element: <OrderFormPage type="purchase" />, handle: withTitle("New Purchase Order", "Purchases") },
      { path: "purchase-orders/:orderId", element: <OrderDetailPage type="purchase" />, handle: { title: "Purchase Order Detail", breadcrumb: "Purchase Order Detail", section: "Purchases" } },
      { path: "purchase-receives", element: <PlaceholderModulePage title="Purchase Receives" description="Receiving-specific workspace placeholder pending backend support." actionLabel="Back to purchase orders" actionTo="/purchase-orders" />, handle: withTitle("Purchase Receives", "Purchases") },
      { path: "bills", element: <PlaceholderModulePage title="Bills" description="Billing placeholder pending financial workflow support." actionLabel="Back to purchase orders" actionTo="/purchase-orders" />, handle: withTitle("Bills", "Purchases") },
      { path: "reports", element: <ReportsPage />, handle: withTitle("Reports", "Analytics") },
      { path: "reports/:reportKey", element: <ReportDetailPage />, handle: { title: "Report Detail", breadcrumb: "Report Detail", section: "Analytics" } },
      { path: "activity-logs", element: <ListPage moduleKey="activity-logs" />, handle: withTitle("Activity Logs", "Analytics") },
      { path: "audit-logs", element: <ListPage moduleKey="audit-logs" />, handle: withTitle("Audit Logs", "Analytics") },
      { path: "users", element: <ListPage moduleKey="users" />, handle: withTitle("Users", "Admin") },
      { path: "tenants", element: <ListPage moduleKey="tenants" />, handle: withTitle("Tenants", "Admin") },
      { path: "subscription", element: <PlaceholderModulePage title="Subscription & Plan Usage" description="Plan and usage management placeholder pending billing backend support." actionLabel="Back to dashboard" actionTo="/" />, handle: withTitle("Subscription", "Admin") },
      { path: "settings", element: <SettingsPage />, handle: withTitle("Settings", "Admin") },
      { path: "ai-assistant", element: <PlaceholderModulePage title="AI Assistant" description="AI inventory assistance placeholder pending stable tenant-safe data integration." actionLabel="Back to dashboard" actionTo="/" />, handle: withTitle("AI Assistant", "AI") },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
