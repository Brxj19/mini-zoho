import { Navigate, createBrowserRouter } from "react-router-dom";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { AppShell } from "../layouts/AppShell";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { NotificationsPage } from "../pages/NotificationsPage";
import { OrderFormPage } from "../pages/OrderFormPage";
import { PlaceholderModulePage } from "../pages/PlaceholderModulePage";
import { ProductFormPage } from "../pages/ProductFormPage";
import { RegisterPage } from "../pages/RegisterPage";
import { ReportsPage } from "../pages/ReportsPage";
import { ResourceDetailPage } from "../pages/ResourceDetailPage";
import { ResourceListPage } from "../pages/ResourceListPage";
import { SettingsPage } from "../pages/SettingsPage";
import { StockActionPage } from "../pages/StockActionPage";

function withHandle(title, section, breadcrumb = title) {
  return { title, section, breadcrumb };
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
    path: "/",
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    handle: withHandle("Home", "Main", "Home"),
    children: [
      { index: true, element: <DashboardPage />, handle: withHandle("Dashboard", "Main", "Dashboard") },
      { path: "notifications", element: <NotificationsPage />, handle: withHandle("Notifications", "Main") },

      { path: "items", element: <ResourceListPage resourceKey="products" />, handle: withHandle("Items", "Inventory") },
      { path: "items/new", element: <ProductFormPage />, handle: withHandle("New Item", "Inventory") },
      { path: "items/:productId", element: <ResourceDetailPage detailKey="product" paramKey="productId" />, handle: withHandle("Item Detail", "Inventory") },
      { path: "items/:productId/edit", element: <ProductFormPage />, handle: withHandle("Edit Item", "Inventory") },
      { path: "products", element: <Navigate to="/items" replace /> },
      { path: "products/new", element: <Navigate to="/items/new" replace /> },
      { path: "products/:productId", element: <Navigate to="/items" replace /> },
      { path: "products/:productId/edit", element: <Navigate to="/items" replace /> },
      { path: "item-groups", element: <PlaceholderModulePage title="Item Groups" description="Grouping, variant, and matrix catalog tooling can land here without changing the shell." actionLabel="Back to items" actionTo="/items" />, handle: withHandle("Item Groups", "Inventory") },

      { path: "warehouses", element: <ResourceListPage resourceKey="warehouses" />, handle: withHandle("Warehouses", "Inventory") },
      { path: "warehouses/:warehouseId", element: <ResourceDetailPage detailKey="warehouse" paramKey="warehouseId" />, handle: withHandle("Warehouse Detail", "Inventory") },
      { path: "inventory/transactions", element: <ResourceListPage resourceKey="inventoryTransactions" />, handle: withHandle("Inventory Transactions", "Inventory") },
      { path: "inventory/transfers", element: <ResourceListPage resourceKey="stockTransfers" />, handle: withHandle("Stock Transfers", "Inventory") },
      { path: "inventory/stock-in", element: <StockActionPage actionKey="stock-in" />, handle: withHandle("Stock In", "Inventory") },
      { path: "inventory/stock-out", element: <StockActionPage actionKey="stock-out" />, handle: withHandle("Stock Out", "Inventory") },
      { path: "inventory/adjustment", element: <StockActionPage actionKey="adjustment" />, handle: withHandle("Inventory Adjustment", "Inventory") },

      { path: "customers", element: <ResourceListPage resourceKey="customers" />, handle: withHandle("Customers", "Sales") },
      { path: "sales-orders", element: <ResourceListPage resourceKey="salesOrders" />, handle: withHandle("Sales Orders", "Sales") },
      { path: "sales-orders/new", element: <OrderFormPage kind="sales" />, handle: withHandle("New Sales Order", "Sales") },
      { path: "sales-orders/:salesOrderId", element: <ResourceDetailPage detailKey="salesOrder" paramKey="salesOrderId" />, handle: withHandle("Sales Order Detail", "Sales") },
      { path: "sales-orders/:salesOrderId/edit", element: <OrderFormPage kind="sales" />, handle: withHandle("Edit Sales Order", "Sales") },
      { path: "packages", element: <PlaceholderModulePage title="Packages" description="Packaging flow is reserved for the next backend pass." actionLabel="Back to sales orders" actionTo="/sales-orders" />, handle: withHandle("Packages", "Sales") },
      { path: "invoices", element: <PlaceholderModulePage title="Invoices" description="Invoice generation and mailing can plug into this workflow later." actionLabel="Back to sales orders" actionTo="/sales-orders" />, handle: withHandle("Invoices", "Sales") },
      { path: "sales-returns", element: <PlaceholderModulePage title="Sales Returns" description="Returns processing is held as a guided placeholder for now." actionLabel="Back to sales orders" actionTo="/sales-orders" />, handle: withHandle("Sales Returns", "Sales") },

      { path: "vendors", element: <ResourceListPage resourceKey="vendors" />, handle: withHandle("Vendors", "Purchases") },
      { path: "purchase-orders", element: <ResourceListPage resourceKey="purchaseOrders" />, handle: withHandle("Purchase Orders", "Purchases") },
      { path: "purchase-orders/new", element: <OrderFormPage kind="purchase" />, handle: withHandle("New Purchase Order", "Purchases") },
      { path: "purchase-orders/:purchaseOrderId", element: <ResourceDetailPage detailKey="purchaseOrder" paramKey="purchaseOrderId" />, handle: withHandle("Purchase Order Detail", "Purchases") },
      { path: "purchase-orders/:purchaseOrderId/edit", element: <OrderFormPage kind="purchase" />, handle: withHandle("Edit Purchase Order", "Purchases") },
      { path: "purchase-receives", element: <PlaceholderModulePage title="Purchase Receives" description="Receiving-specific staging can be layered here once the backend expands." actionLabel="Back to purchase orders" actionTo="/purchase-orders" />, handle: withHandle("Purchase Receives", "Purchases") },
      { path: "bills", element: <PlaceholderModulePage title="Bills" description="Bills and payables remain a planned finance-side placeholder." actionLabel="Back to purchase orders" actionTo="/purchase-orders" />, handle: withHandle("Bills", "Purchases") },

      { path: "reports", element: <ReportsPage />, handle: withHandle("Reports", "Analytics") },
      { path: "activity-logs", element: <ResourceListPage resourceKey="auditLogs" />, handle: withHandle("Activity Logs", "Analytics") },
      { path: "audit-logs", element: <ResourceListPage resourceKey="auditLogs" />, handle: withHandle("Audit Logs", "Analytics") },
      { path: "users", element: <ResourceListPage resourceKey="users" />, handle: withHandle("Users", "Admin") },
      { path: "tenants", element: <ResourceListPage resourceKey="tenants" />, handle: withHandle("Tenants", "Admin") },
      { path: "subscription", element: <PlaceholderModulePage title="Subscription" description="Plan usage, billing, and quotas are intentionally held as a placeholder for now." actionLabel="Back to dashboard" actionTo="/" />, handle: withHandle("Subscription", "Admin") },
      { path: "settings", element: <SettingsPage />, handle: withHandle("Settings", "Admin") },
      { path: "ai-assistant", element: <PlaceholderModulePage title="AI Assistant" description="The AI assistant page is reserved until the tenant-safe GenAI layer is finalized." actionLabel="Back to dashboard" actionTo="/" />, handle: withHandle("AI Assistant", "AI") },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
