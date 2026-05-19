export const homeNavigation = { label: "Home", path: "/", icon: "home" };

const tenantNavigationGroups = [
  {
    title: "Inventory",
    items: [
      { label: "Items", path: "/items", icon: "box" },
      { label: "Categories", path: "/categories", icon: "layers", roles: ["TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Brands", path: "/brands", icon: "stars", roles: ["TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Item Groups", path: "/item-groups", icon: "group" },
      { label: "Inventory Adjustments", path: "/inventory/adjustment", icon: "sliders", roles: ["TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Stock Transfers", path: "/inventory/transfers", icon: "shuffle", roles: ["TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Warehouses", path: "/warehouses", icon: "warehouse", roles: ["TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Low Stock", path: "/inventory/low-stock", icon: "alert" },
      { label: "Barcode Tools", path: "/inventory/barcodes", icon: "hash", roles: ["TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Transactions", path: "/inventory/transactions", icon: "activity", roles: ["TENANT_ADMIN", "INVENTORY_MANAGER"] },
    ],
  },
  {
    title: "Sales",
    items: [
      { label: "Customers", path: "/customers", icon: "users", roles: ["TENANT_ADMIN", "SALES_STAFF"] },
      { label: "Sales Orders", path: "/sales-orders", icon: "cart", roles: ["TENANT_ADMIN", "SALES_STAFF"] },
      { label: "Packages", path: "/packages", icon: "package", roles: ["TENANT_ADMIN", "SALES_STAFF"] },
      { label: "Invoices", path: "/invoices", icon: "receipt", roles: ["TENANT_ADMIN", "SALES_STAFF"] },
      { label: "Sales Returns", path: "/sales-returns", icon: "undo", roles: ["TENANT_ADMIN", "SALES_STAFF"] },
    ],
  },
  {
    title: "Purchases",
    items: [
      { label: "Vendors", path: "/vendors", icon: "briefcase", roles: ["TENANT_ADMIN", "PURCHASE_STAFF", "INVENTORY_MANAGER"] },
      { label: "Purchase Orders", path: "/purchase-orders", icon: "clipboard", roles: ["TENANT_ADMIN", "PURCHASE_STAFF"] },
      { label: "Purchase Receives", path: "/purchase-receives", icon: "truck", roles: ["TENANT_ADMIN", "PURCHASE_STAFF", "INVENTORY_MANAGER"] },
      { label: "Bills", path: "/bills", icon: "bill", roles: ["TENANT_ADMIN", "PURCHASE_STAFF"] },
    ],
  },
  {
    title: "Analytics",
    items: [
      { label: "Reports", path: "/reports", icon: "chart" },
      { label: "Activity Logs", path: "/activity-logs", icon: "activity" },
      { label: "Audit Logs", path: "/audit-logs", icon: "shield" },
      { label: "Notifications", path: "/notifications", icon: "bell" },
    ],
  },
  {
    title: "Admin",
    items: [
      { label: "Users", path: "/users", icon: "userCog", roles: ["TENANT_ADMIN"] },
      { label: "Settings", path: "/settings", icon: "settings", roles: ["TENANT_ADMIN"] },
      { label: "Subscription / Usage", path: "/subscription", icon: "sparkles", roles: ["TENANT_ADMIN"] },
    ],
  },
  {
    title: "AI",
    items: [{ label: "AI Assistant", path: "/ai-assistant", icon: "stars", roles: ["TENANT_ADMIN"] }],
  },
];

const superAdminNavigationGroups = [
  {
    title: "Platform",
    items: [
      { label: "Tenants", path: "/tenants", icon: "building" },
      { label: "Subscription Plans", path: "/subscription", icon: "sparkles" },
      { label: "System Users", path: "/users", icon: "userCog" },
      { label: "System Audit Logs", path: "/audit-logs", icon: "shield" },
      { label: "Notifications", path: "/notifications", icon: "bell" },
    ],
  },
  {
    title: "Analytics",
    items: [
      { label: "Reports", path: "/reports", icon: "chart" },
      { label: "Platform Activity", path: "/activity-logs", icon: "activity" },
    ],
  },
  {
    title: "Settings",
    items: [
      { label: "Platform Settings", path: "/settings", icon: "settings" },
      { label: "AI Assistant", path: "/ai-assistant", icon: "stars" },
    ],
  },
];

const inventoryManagerGroups = [
  {
    title: "Inventory",
    items: [
      { label: "Items", path: "/items", icon: "box" },
      { label: "Categories", path: "/categories", icon: "layers" },
      { label: "Brands", path: "/brands", icon: "stars" },
      { label: "Warehouses", path: "/warehouses", icon: "warehouse" },
      { label: "Transactions", path: "/inventory/transactions", icon: "activity" },
      { label: "Inventory Adjustments", path: "/inventory/adjustment", icon: "sliders" },
      { label: "Stock Transfers", path: "/inventory/transfers", icon: "shuffle" },
      { label: "Low Stock", path: "/inventory/low-stock", icon: "alert" },
      { label: "Barcode Tools", path: "/inventory/barcodes", icon: "hash" },
    ],
  },
  {
    title: "Purchases",
    items: [
      { label: "Vendors", path: "/vendors", icon: "briefcase" },
      { label: "Purchase Receives", path: "/purchase-receives", icon: "truck" },
    ],
  },
  {
    title: "Analytics",
    items: [
      { label: "Reports", path: "/reports", icon: "chart" },
      { label: "Audit Logs", path: "/audit-logs", icon: "shield" },
    ],
  },
];

const salesStaffGroups = [
  {
    title: "Sales",
    items: [
      { label: "Customers", path: "/customers", icon: "users" },
      { label: "Sales Orders", path: "/sales-orders", icon: "cart" },
      { label: "Packages", path: "/packages", icon: "package" },
      { label: "Invoices", path: "/invoices", icon: "receipt" },
      { label: "Sales Returns", path: "/sales-returns", icon: "undo" },
    ],
  },
  {
    title: "Analytics",
    items: [
      { label: "Reports", path: "/reports", icon: "chart" },
      { label: "Notifications", path: "/notifications", icon: "bell" },
    ],
  },
];

const purchaseStaffGroups = [
  {
    title: "Purchases",
    items: [
      { label: "Vendors", path: "/vendors", icon: "briefcase" },
      { label: "Purchase Orders", path: "/purchase-orders", icon: "clipboard" },
      { label: "Purchase Receives", path: "/purchase-receives", icon: "truck" },
      { label: "Bills", path: "/bills", icon: "bill" },
    ],
  },
  {
    title: "Analytics",
    items: [
      { label: "Reports", path: "/reports", icon: "chart" },
      { label: "Notifications", path: "/notifications", icon: "bell" },
    ],
  },
];

const viewerGroups = [
  {
    title: "Workspace",
    items: [
      { label: "Items", path: "/items", icon: "box" },
      { label: "Warehouses", path: "/warehouses", icon: "warehouse" },
      { label: "Customers", path: "/customers", icon: "users" },
      { label: "Vendors", path: "/vendors", icon: "briefcase" },
    ],
  },
  {
    title: "Analytics",
    items: [
      { label: "Reports", path: "/reports", icon: "chart" },
      { label: "Audit Logs", path: "/audit-logs", icon: "shield" },
      { label: "Notifications", path: "/notifications", icon: "bell" },
    ],
  },
];

export function getNavigationGroups(role) {
  switch (role) {
    case "SUPER_ADMIN":
      return superAdminNavigationGroups;
    case "TENANT_ADMIN":
      return tenantNavigationGroups;
    case "INVENTORY_MANAGER":
      return inventoryManagerGroups;
    case "SALES_STAFF":
      return salesStaffGroups;
    case "PURCHASE_STAFF":
      return purchaseStaffGroups;
    case "VIEWER":
      return viewerGroups;
    default:
      return tenantNavigationGroups;
  }
}

const quickCreateByRole = {
  SUPER_ADMIN: [
    { label: "New Tenant", path: "/tenants/new", icon: "building" },
    { label: "New System User", path: "/users/new", icon: "userCog" },
  ],
  TENANT_ADMIN: [
    { label: "New Item", path: "/items/new", icon: "box" },
    { label: "New Customer", path: "/customers/new", icon: "users" },
    { label: "New Vendor", path: "/vendors/new", icon: "briefcase" },
    { label: "New Sales Order", path: "/sales-orders/new", icon: "cart" },
    { label: "New Purchase Order", path: "/purchase-orders/new", icon: "clipboard" },
    { label: "Stock Adjustment", path: "/inventory/adjustment", icon: "sliders" },
    { label: "Stock Transfer", path: "/inventory/transfers/new", icon: "shuffle" },
  ],
  INVENTORY_MANAGER: [
    { label: "New Item", path: "/items/new", icon: "box" },
    { label: "New Warehouse", path: "/warehouses/new", icon: "warehouse" },
    { label: "Stock In", path: "/inventory/stock-in", icon: "packagePlus" },
    { label: "Stock Adjustment", path: "/inventory/adjustment", icon: "sliders" },
    { label: "Stock Transfer", path: "/inventory/transfers/new", icon: "shuffle" },
  ],
  SALES_STAFF: [
    { label: "New Customer", path: "/customers/new", icon: "users" },
    { label: "New Sales Order", path: "/sales-orders/new", icon: "cart" },
    { label: "New Package", path: "/packages/new", icon: "package" },
    { label: "New Invoice", path: "/invoices/new", icon: "receipt" },
  ],
  PURCHASE_STAFF: [
    { label: "New Vendor", path: "/vendors/new", icon: "briefcase" },
    { label: "New Purchase Order", path: "/purchase-orders/new", icon: "clipboard" },
    { label: "New Purchase Receive", path: "/purchase-receives/new", icon: "truck" },
    { label: "New Bill", path: "/bills/new", icon: "bill" },
  ],
  VIEWER: [],
};

export function getQuickCreateItems(role) {
  return quickCreateByRole[role] ?? [];
}

export const settingsNavigation = [
  { key: "organization", label: "Organization Profile", icon: "building" },
  { key: "users", label: "Users", icon: "users" },
  { key: "roles", label: "Roles", icon: "shield" },
  { key: "warehouses", label: "Warehouses", icon: "warehouse" },
  { key: "taxes", label: "Taxes", icon: "receipt" },
  { key: "preferences", label: "Preferences", icon: "sliders" },
  { key: "numbers", label: "Number Series", icon: "hash" },
  { key: "subscription", label: "Subscription", icon: "sparkles" },
  { key: "security", label: "Security", icon: "shield" },
  { key: "notifications", label: "Notifications", icon: "bell" },
  { key: "integrations", label: "Integrations", icon: "plug" },
  { key: "ai", label: "AI Settings", icon: "stars" },
];
