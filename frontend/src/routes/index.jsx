import { createBrowserRouter } from "react-router-dom";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { AppShell } from "../layouts/AppShell";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { NotificationsPage } from "../pages/NotificationsPage";
import { OrderFormPage } from "../pages/OrderFormPage";
import { ProductFormPage } from "../pages/ProductFormPage";
import { RegisterPage } from "../pages/RegisterPage";
import { ReportsPage } from "../pages/ReportsPage";
import { ResourceDetailPage } from "../pages/ResourceDetailPage";
import { ResourceListPage } from "../pages/ResourceListPage";
import { SettingsPage } from "../pages/SettingsPage";
import { StockActionPage } from "../pages/StockActionPage";

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
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: "products",
        element: <ResourceListPage resourceKey="products" />,
      },
      {
        path: "products/new",
        element: <ProductFormPage />,
      },
      {
        path: "products/:productId",
        element: <ResourceDetailPage detailKey="product" paramKey="productId" />,
      },
      {
        path: "products/:productId/edit",
        element: <ProductFormPage />,
      },
      {
        path: "warehouses",
        element: <ResourceListPage resourceKey="warehouses" />,
      },
      {
        path: "warehouses/:warehouseId",
        element: <ResourceDetailPage detailKey="warehouse" paramKey="warehouseId" />,
      },
      {
        path: "vendors",
        element: <ResourceListPage resourceKey="vendors" />,
      },
      {
        path: "customers",
        element: <ResourceListPage resourceKey="customers" />,
      },
      {
        path: "inventory/transactions",
        element: <ResourceListPage resourceKey="inventoryTransactions" />,
      },
      {
        path: "inventory/transfers",
        element: <ResourceListPage resourceKey="stockTransfers" />,
      },
      {
        path: "inventory/stock-in",
        element: <StockActionPage actionKey="stock-in" />,
      },
      {
        path: "inventory/stock-out",
        element: <StockActionPage actionKey="stock-out" />,
      },
      {
        path: "inventory/adjustment",
        element: <StockActionPage actionKey="adjustment" />,
      },
      {
        path: "purchase-orders",
        element: <ResourceListPage resourceKey="purchaseOrders" />,
      },
      {
        path: "purchase-orders/new",
        element: <OrderFormPage kind="purchase" />,
      },
      {
        path: "purchase-orders/:purchaseOrderId",
        element: <ResourceDetailPage detailKey="purchaseOrder" paramKey="purchaseOrderId" />,
      },
      {
        path: "purchase-orders/:purchaseOrderId/edit",
        element: <OrderFormPage kind="purchase" />,
      },
      {
        path: "sales-orders",
        element: <ResourceListPage resourceKey="salesOrders" />,
      },
      {
        path: "sales-orders/new",
        element: <OrderFormPage kind="sales" />,
      },
      {
        path: "sales-orders/:salesOrderId",
        element: <ResourceDetailPage detailKey="salesOrder" paramKey="salesOrderId" />,
      },
      {
        path: "sales-orders/:salesOrderId/edit",
        element: <OrderFormPage kind="sales" />,
      },
      {
        path: "reports",
        element: <ReportsPage />,
      },
      {
        path: "users",
        element: <ResourceListPage resourceKey="users" />,
      },
      {
        path: "settings",
        element: <SettingsPage />,
      },
      {
        path: "notifications",
        element: <NotificationsPage />,
      },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
