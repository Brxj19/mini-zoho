import { Navigate, createBrowserRouter } from "react-router-dom";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { AppShell } from "../layouts/AppShell";
import { DashboardPage } from "../pages/DashboardPage";
import { BarcodeToolsPage } from "../pages/BarcodeToolsPage";
import { AIAssistantPage } from "../pages/AIAssistantPage";
import { BusinessRecordFormPage } from "../pages/BusinessRecordFormPage";
import { ForgotPasswordPage } from "../pages/ForgotPasswordPage";
import { ItemGroupsPage } from "../pages/ItemGroupsPage";
import { LoginPage } from "../pages/LoginPage";
import { MasterDataFormPage } from "../pages/MasterDataFormPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { NotificationsPage } from "../pages/NotificationsPage";
import { OrderFormPage } from "../pages/OrderFormPage";
import { OnboardingPage } from "../pages/OnboardingPage";
import { ProductFormPage } from "../pages/ProductFormPage";
import { RegisterPage } from "../pages/RegisterPage";
import { ResetPasswordPage } from "../pages/ResetPasswordPage";
import { ReportsPage } from "../pages/ReportsPage";
import { ResourceDetailPage } from "../pages/ResourceDetailPage";
import { ResourceListPage } from "../pages/ResourceListPage";
import { SettingsPage } from "../pages/SettingsPage";
import { StockActionPage } from "../pages/StockActionPage";
import { StockTransferFormPage } from "../pages/StockTransferFormPage";
import { SubscriptionPage } from "../pages/SubscriptionPage";
import { WarehouseFormPage } from "../pages/WarehouseFormPage";
import { LowStockPage } from "../pages/LowStockPage";
import { InventoryDetailPage } from "../pages/InventoryDetailPage";
import { InventoryListPage } from "../pages/InventoryListPage";
import { UserFormPage } from "../pages/UserFormPage";
import { TenantFormPage } from "../pages/TenantFormPage";

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
    path: "/forgot-password",
    element: <ForgotPasswordPage />,
  },
  {
    path: "/reset-password",
    element: <ResetPasswordPage />,
  },
  {
    path: "/onboarding",
    element: (
      <ProtectedRoute>
        <OnboardingPage />
      </ProtectedRoute>
    ),
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

      { path: "categories", element: <ResourceListPage resourceKey="categories" />, handle: withHandle("Categories", "Inventory") },
      { path: "categories/new", element: <MasterDataFormPage entityKey="category" paramKey="categoryId" />, handle: withHandle("New Category", "Inventory") },
      { path: "categories/:categoryId", element: <ResourceDetailPage detailKey="category" paramKey="categoryId" />, handle: withHandle("Category Detail", "Inventory") },
      { path: "categories/:categoryId/edit", element: <MasterDataFormPage entityKey="category" paramKey="categoryId" />, handle: withHandle("Edit Category", "Inventory") },
      { path: "brands", element: <ResourceListPage resourceKey="brands" />, handle: withHandle("Brands", "Inventory") },
      { path: "brands/new", element: <MasterDataFormPage entityKey="brand" paramKey="brandId" />, handle: withHandle("New Brand", "Inventory") },
      { path: "brands/:brandId", element: <ResourceDetailPage detailKey="brand" paramKey="brandId" />, handle: withHandle("Brand Detail", "Inventory") },
      { path: "brands/:brandId/edit", element: <MasterDataFormPage entityKey="brand" paramKey="brandId" />, handle: withHandle("Edit Brand", "Inventory") },
      { path: "items", element: <InventoryListPage kind="products" />, handle: withHandle("Items", "Inventory") },
      { path: "items/new", element: <ProductFormPage />, handle: withHandle("New Item", "Inventory") },
      { path: "items/:productId", element: <InventoryDetailPage kind="product" />, handle: withHandle("Item Detail", "Inventory") },
      { path: "items/:productId/edit", element: <ProductFormPage />, handle: withHandle("Edit Item", "Inventory") },
      { path: "products", element: <Navigate to="/items" replace /> },
      { path: "products/new", element: <Navigate to="/items/new" replace /> },
      { path: "products/:productId", element: <Navigate to="/items" replace /> },
      { path: "products/:productId/edit", element: <Navigate to="/items" replace /> },
      { path: "item-groups", element: <ItemGroupsPage />, handle: withHandle("Item Groups", "Inventory") },

      { path: "warehouses", element: <InventoryListPage kind="warehouses" />, handle: withHandle("Warehouses", "Inventory") },
      { path: "warehouses/new", element: <WarehouseFormPage />, handle: withHandle("New Warehouse", "Inventory") },
      { path: "warehouses/:warehouseId", element: <InventoryDetailPage kind="warehouse" />, handle: withHandle("Warehouse Detail", "Inventory") },
      { path: "warehouses/:warehouseId/edit", element: <WarehouseFormPage />, handle: withHandle("Edit Warehouse", "Inventory") },
      { path: "inventory/transactions", element: <InventoryListPage kind="inventoryTransactions" />, handle: withHandle("Inventory Transactions", "Inventory") },
      { path: "inventory/barcodes", element: <BarcodeToolsPage />, handle: withHandle("Barcode Tools", "Inventory") },
      { path: "inventory/transfers", element: <InventoryListPage kind="stockTransfers" />, handle: withHandle("Stock Transfers", "Inventory") },
      { path: "inventory/transfers/new", element: <StockTransferFormPage />, handle: withHandle("New Stock Transfer", "Inventory") },
      { path: "inventory/transfers/:transferId", element: <ResourceDetailPage detailKey="stockTransfer" paramKey="transferId" />, handle: withHandle("Stock Transfer Detail", "Inventory") },
      { path: "inventory/transfers/:transferId/edit", element: <StockTransferFormPage />, handle: withHandle("Edit Stock Transfer", "Inventory") },
      { path: "inventory/low-stock", element: <LowStockPage />, handle: withHandle("Low Stock", "Inventory") },
      { path: "inventory/stock-in", element: <StockActionPage actionKey="stock-in" />, handle: withHandle("Stock In", "Inventory") },
      { path: "inventory/stock-out", element: <StockActionPage actionKey="stock-out" />, handle: withHandle("Stock Out", "Inventory") },
      { path: "inventory/adjustment", element: <StockActionPage actionKey="adjustment" />, handle: withHandle("Inventory Adjustment", "Inventory") },

      { path: "customers", element: <ResourceListPage resourceKey="customers" />, handle: withHandle("Customers", "Sales") },
      { path: "customers/new", element: <MasterDataFormPage entityKey="customer" paramKey="customerId" />, handle: withHandle("New Customer", "Sales") },
      { path: "customers/:customerId", element: <ResourceDetailPage detailKey="customer" paramKey="customerId" />, handle: withHandle("Customer Detail", "Sales") },
      { path: "customers/:customerId/edit", element: <MasterDataFormPage entityKey="customer" paramKey="customerId" />, handle: withHandle("Edit Customer", "Sales") },
      { path: "sales-orders", element: <ResourceListPage resourceKey="salesOrders" />, handle: withHandle("Sales Orders", "Sales") },
      { path: "sales-orders/new", element: <OrderFormPage kind="sales" />, handle: withHandle("New Sales Order", "Sales") },
      { path: "sales-orders/:salesOrderId", element: <ResourceDetailPage detailKey="salesOrder" paramKey="salesOrderId" />, handle: withHandle("Sales Order Detail", "Sales") },
      { path: "sales-orders/:salesOrderId/edit", element: <OrderFormPage kind="sales" />, handle: withHandle("Edit Sales Order", "Sales") },
      { path: "packages", element: <ResourceListPage resourceKey="packages" />, handle: withHandle("Packages", "Sales") },
      { path: "packages/new", element: <BusinessRecordFormPage kind="package" />, handle: withHandle("New Package", "Sales") },
      { path: "packages/:packageId", element: <ResourceDetailPage detailKey="package" paramKey="packageId" />, handle: withHandle("Package Detail", "Sales") },
      { path: "invoices", element: <ResourceListPage resourceKey="invoices" />, handle: withHandle("Invoices", "Sales") },
      { path: "invoices/new", element: <BusinessRecordFormPage kind="invoice" />, handle: withHandle("New Invoice", "Sales") },
      { path: "invoices/:invoiceId", element: <ResourceDetailPage detailKey="invoice" paramKey="invoiceId" />, handle: withHandle("Invoice Detail", "Sales") },
      { path: "sales-returns", element: <ResourceListPage resourceKey="salesReturns" />, handle: withHandle("Sales Returns", "Sales") },
      { path: "sales-returns/new", element: <BusinessRecordFormPage kind="salesReturn" />, handle: withHandle("New Sales Return", "Sales") },
      { path: "sales-returns/:salesReturnId", element: <ResourceDetailPage detailKey="salesReturn" paramKey="salesReturnId" />, handle: withHandle("Sales Return Detail", "Sales") },

      { path: "vendors", element: <ResourceListPage resourceKey="vendors" />, handle: withHandle("Vendors", "Purchases") },
      { path: "vendors/new", element: <MasterDataFormPage entityKey="vendor" paramKey="vendorId" />, handle: withHandle("New Vendor", "Purchases") },
      { path: "vendors/:vendorId", element: <ResourceDetailPage detailKey="vendor" paramKey="vendorId" />, handle: withHandle("Vendor Detail", "Purchases") },
      { path: "vendors/:vendorId/edit", element: <MasterDataFormPage entityKey="vendor" paramKey="vendorId" />, handle: withHandle("Edit Vendor", "Purchases") },
      { path: "purchase-orders", element: <ResourceListPage resourceKey="purchaseOrders" />, handle: withHandle("Purchase Orders", "Purchases") },
      { path: "purchase-orders/new", element: <OrderFormPage kind="purchase" />, handle: withHandle("New Purchase Order", "Purchases") },
      { path: "purchase-orders/:purchaseOrderId", element: <ResourceDetailPage detailKey="purchaseOrder" paramKey="purchaseOrderId" />, handle: withHandle("Purchase Order Detail", "Purchases") },
      { path: "purchase-orders/:purchaseOrderId/edit", element: <OrderFormPage kind="purchase" />, handle: withHandle("Edit Purchase Order", "Purchases") },
      { path: "purchase-receives", element: <ResourceListPage resourceKey="purchaseReceives" />, handle: withHandle("Purchase Receives", "Purchases") },
      { path: "purchase-receives/new", element: <BusinessRecordFormPage kind="purchaseReceive" />, handle: withHandle("New Purchase Receive", "Purchases") },
      { path: "purchase-receives/:purchaseReceiveId", element: <ResourceDetailPage detailKey="purchaseReceive" paramKey="purchaseReceiveId" />, handle: withHandle("Purchase Receive Detail", "Purchases") },
      { path: "bills", element: <ResourceListPage resourceKey="bills" />, handle: withHandle("Bills", "Purchases") },
      { path: "bills/new", element: <BusinessRecordFormPage kind="bill" />, handle: withHandle("New Bill", "Purchases") },
      { path: "bills/:billId", element: <ResourceDetailPage detailKey="bill" paramKey="billId" />, handle: withHandle("Bill Detail", "Purchases") },

      { path: "reports", element: <ReportsPage />, handle: withHandle("Reports", "Analytics") },
      { path: "activity-logs", element: <ResourceListPage resourceKey="auditLogs" />, handle: withHandle("Activity Logs", "Analytics") },
      { path: "audit-logs", element: <ResourceListPage resourceKey="auditLogs" />, handle: withHandle("Audit Logs", "Analytics") },
      { path: "users", element: <ResourceListPage resourceKey="users" />, handle: withHandle("Users", "Admin") },
      { path: "users/new", element: <UserFormPage />, handle: withHandle("New User", "Admin") },
      { path: "users/:userId", element: <ResourceDetailPage detailKey="user" paramKey="userId" />, handle: withHandle("User Detail", "Admin") },
      { path: "users/:userId/edit", element: <UserFormPage />, handle: withHandle("Edit User", "Admin") },
      { path: "tenants", element: <ResourceListPage resourceKey="tenants" />, handle: withHandle("Tenants", "Admin") },
      { path: "tenants/new", element: <TenantFormPage />, handle: withHandle("New Tenant", "Admin") },
      { path: "tenants/:tenantId", element: <ResourceDetailPage detailKey="tenant" paramKey="tenantId" />, handle: withHandle("Tenant Detail", "Admin") },
      { path: "tenants/:tenantId/edit", element: <TenantFormPage />, handle: withHandle("Edit Tenant", "Admin") },
      { path: "subscription", element: <SubscriptionPage />, handle: withHandle("Subscription", "Admin") },
      { path: "settings", element: <SettingsPage />, handle: withHandle("Settings", "Admin") },
      { path: "ai-assistant", element: <AIAssistantPage />, handle: withHandle("AI Assistant", "AI") },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
