import { useEffect, useState } from "react";

import api from "../lib/api";
import { DataTable } from "../components/DataTable";
import { PageHeader } from "../components/PageHeader";

const listConfigs = {
  items: {
    title: "Items",
    description: "Track products, variants, stock, reorder points, and pricing from one dense item list.",
    filters: [
      { label: "All Items", value: "all" },
      { label: "Active Items", value: "active" },
      { label: "Inactive Items", value: "inactive" },
      { label: "Low Stock Items", value: "low_stock" },
    ],
    columns: [
      { key: "name", label: "Name" },
      { key: "sku", label: "SKU" },
      { key: "category", label: "Category" },
      { key: "brand", label: "Brand" },
      { key: "stockOnHand", label: "Stock on Hand" },
      { key: "reorderLevel", label: "Reorder Level" },
      { key: "sellingPrice", label: "Selling Price" },
      { key: "status", label: "Status" },
    ],
    createLabel: "+ New Item",
    createTo: "/items/new",
    rowLink: (row) => `/items/${row.id}`,
    searchPlaceholder: "Search by name, SKU, brand, or barcode",
  },
  warehouses: {
    title: "Warehouses",
    description: "Monitor locations, primary warehouse status, managers, and transfer entry points.",
    filters: [
      { label: "All Warehouses", value: "all" },
      { label: "Active Warehouses", value: "active" },
      { label: "Inactive Warehouses", value: "inactive" },
    ],
    columns: [
      { key: "name", label: "Warehouse" },
      { key: "location", label: "Location" },
      { key: "stockCount", label: "Stock Count" },
      { key: "manager", label: "Manager" },
      { key: "status", label: "Status" },
    ],
    createLabel: "+ New Warehouse",
    createTo: "/settings?section=warehouses",
    rowLink: (row) => `/warehouses/${row.id}`,
    searchPlaceholder: "Search warehouse name or location",
  },
  customers: {
    title: "Customers",
    description: "Customer account directory for quotes, sales orders, and fulfillment history.",
    filters: [
      { label: "All Customers", value: "all" },
      { label: "Active Customers", value: "active" },
      { label: "Inactive Customers", value: "inactive" },
    ],
    columns: [
      { key: "name", label: "Customer" },
      { key: "email", label: "Email" },
      { key: "phone", label: "Phone" },
      { key: "city", label: "City" },
      { key: "status", label: "Status" },
    ],
    createLabel: "+ New Customer",
    createTo: "/customers",
    searchPlaceholder: "Search customers by name, email, or city",
  },
  vendors: {
    title: "Vendors",
    description: "Supplier directory for procurement, receiving, and cost visibility.",
    filters: [
      { label: "All Vendors", value: "all" },
      { label: "Active Vendors", value: "active" },
      { label: "Inactive Vendors", value: "inactive" },
    ],
    columns: [
      { key: "name", label: "Vendor" },
      { key: "email", label: "Email" },
      { key: "phone", label: "Phone" },
      { key: "city", label: "City" },
      { key: "status", label: "Status" },
    ],
    createLabel: "+ New Vendor",
    createTo: "/vendors",
    searchPlaceholder: "Search vendors by name, email, or city",
  },
  "sales-orders": {
    title: "Sales Orders",
    description: "Track order status from draft through delivery with dense, action-ready list views.",
    filters: [
      { label: "All Sales Orders", value: "all" },
      { label: "Draft", value: "draft" },
      { label: "Confirmed", value: "confirmed" },
      { label: "Packed", value: "packed" },
      { label: "Shipped", value: "shipped" },
      { label: "Delivered", value: "delivered" },
    ],
    columns: [
      { key: "date", label: "Date" },
      { key: "orderNumber", label: "Sales Order#" },
      { key: "reference", label: "Reference#" },
      { key: "customerName", label: "Customer" },
      { key: "status", label: "Status" },
      { key: "amount", label: "Amount" },
    ],
    createLabel: "+ New Sales Order",
    createTo: "/sales-orders/new",
    rowLink: (row) => `/sales-orders/${row.id}`,
    searchPlaceholder: "Search by order number, customer, or reference",
  },
  "purchase-orders": {
    title: "Purchase Orders",
    description: "Monitor vendor purchasing workflows, receiving progress, and outstanding inventory inflow.",
    filters: [
      { label: "All Purchase Orders", value: "all" },
      { label: "Draft", value: "draft" },
      { label: "Issued", value: "issued" },
      { label: "Partially Received", value: "partially_received" },
      { label: "Received", value: "received" },
    ],
    columns: [
      { key: "date", label: "Date" },
      { key: "orderNumber", label: "PO#" },
      { key: "reference", label: "Reference#" },
      { key: "vendorName", label: "Vendor" },
      { key: "status", label: "Status" },
      { key: "amount", label: "Amount" },
    ],
    createLabel: "+ New Purchase Order",
    createTo: "/purchase-orders/new",
    rowLink: (row) => `/purchase-orders/${row.id}`,
    searchPlaceholder: "Search by PO number, vendor, or reference",
  },
  "stock-transfers": {
    title: "Stock Transfers",
    description: "Coordinate movement between source and destination warehouses with transfer status tracking.",
    filters: [
      { label: "All Transfers", value: "all" },
      { label: "Draft", value: "draft" },
      { label: "In Transit", value: "in_transit" },
      { label: "Completed", value: "completed" },
    ],
    columns: [
      { key: "transferNumber", label: "Transfer#" },
      { key: "source", label: "Source" },
      { key: "destination", label: "Destination" },
      { key: "items", label: "Items" },
      { key: "status", label: "Status" },
      { key: "updatedAt", label: "Updated At" },
    ],
    createLabel: "+ New Transfer",
    createTo: "/stock-transfers",
    searchPlaceholder: "Search by transfer number or warehouse",
  },
  "inventory-adjustments": {
    title: "Inventory Adjustments",
    description: "Capture cycle counts, damage corrections, and warehouse reconciliation adjustments.",
    filters: [
      { label: "All Adjustments", value: "all" },
      { label: "Draft", value: "draft" },
      { label: "Completed", value: "completed" },
    ],
    columns: [
      { key: "adjustmentNumber", label: "Adjustment#" },
      { key: "date", label: "Date" },
      { key: "warehouse", label: "Warehouse" },
      { key: "reason", label: "Reason" },
      { key: "quantity", label: "Quantity" },
      { key: "status", label: "Status" },
    ],
    createLabel: "+ New Adjustment",
    createTo: "/inventory-adjustments",
    searchPlaceholder: "Search by adjustment number or warehouse",
  },
  "low-stock": {
    title: "Low Stock",
    description: "Focused queue of items at or below reorder level for purchasing follow-up.",
    filters: [
      { label: "All Low Stock", value: "all" },
      { label: "Active Low Stock", value: "active" },
      { label: "Inactive Low Stock", value: "inactive" },
    ],
    columns: [
      { key: "name", label: "Name" },
      { key: "sku", label: "SKU" },
      { key: "category", label: "Category" },
      { key: "stockOnHand", label: "Stock on Hand" },
      { key: "reorderLevel", label: "Reorder Level" },
      { key: "status", label: "Status" },
    ],
    createLabel: "Create Purchase Order",
    createTo: "/purchase-orders/new",
    rowLink: (row) => `/items/${row.id}`,
    searchPlaceholder: "Search low-stock items",
  },
  users: {
    title: "Users",
    description: "User directory, role assignments, and account status visibility.",
    filters: [
      { label: "All Users", value: "all" },
      { label: "Active Users", value: "active" },
      { label: "Inactive Users", value: "inactive" },
    ],
    columns: [
      { key: "name", label: "Name" },
      { key: "email", label: "Email" },
      { key: "role", label: "Role" },
      { key: "status", label: "Status" },
      { key: "lastLogin", label: "Last Login" },
    ],
    createLabel: "+ New User",
    createTo: "/settings?section=users",
    searchPlaceholder: "Search by name, email, or role",
  },
  tenants: {
    title: "Tenants",
    description: "Super admin tenant management view for plan, status, and account footprint.",
    filters: [
      { label: "All Tenants", value: "all" },
      { label: "Active", value: "active" },
      { label: "Disabled", value: "disabled" },
    ],
    columns: [
      { key: "companyName", label: "Company" },
      { key: "contactEmail", label: "Contact Email" },
      { key: "plan", label: "Plan" },
      { key: "users", label: "Users" },
      { key: "status", label: "Status" },
    ],
    createLabel: "+ New Tenant",
    createTo: "/tenants",
    searchPlaceholder: "Search company, plan, or contact email",
  },
  "activity-logs": {
    title: "Activity Logs",
    description: "Operational event stream across inventory, purchasing, and sales actions.",
    filters: [{ label: "All Activity", value: "all" }],
    columns: [
      { key: "actor", label: "Actor" },
      { key: "action", label: "Action" },
      { key: "module", label: "Module" },
      { key: "createdAt", label: "Created At" },
    ],
    searchPlaceholder: "Search actor, action, or module",
  },
  "audit-logs": {
    title: "Audit Logs",
    description: "Compliance-friendly audit trail for admin, security, and system-level events.",
    filters: [{ label: "All Audit Events", value: "all" }],
    columns: [
      { key: "actor", label: "Actor" },
      { key: "action", label: "Action" },
      { key: "module", label: "Module" },
      { key: "severity", label: "Severity" },
      { key: "createdAt", label: "Created At" },
    ],
    searchPlaceholder: "Search actor, action, or severity",
  },
};

export function ListPage({ moduleKey }) {
  const config = listConfigs[moduleKey];
  const [rows, setRows] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    api
      .get(`/app/${moduleKey}`)
      .then(({ data }) => {
        if (active) {
          setRows(data.rows ?? []);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [moduleKey]);

  return (
    <div className="page-stack">
      <PageHeader eyebrow="Data Table" title={config.title} description={config.description} />
      <DataTable
        {...config}
        rows={rows}
        isLoading={isLoading}
        sourceNote="Rows are loaded from the backend seed data and filtered client-side in the table."
        emptyState={{
          icon: "box",
          title: `No ${config.title.toLowerCase()} yet`,
          description: "Use the primary action to start populating this module.",
          actionLabel: config.createLabel,
          actionTo: config.createTo,
        }}
      />
    </div>
  );
}
