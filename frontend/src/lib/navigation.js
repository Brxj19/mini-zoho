export const homeNavigation = { label: "Home", path: "/", icon: "home" };

export const navigationGroups = [
  {
    title: "Inventory",
    items: [
      { label: "Items", path: "/items", icon: "box" },
      { label: "Item Groups", path: "/item-groups", icon: "layers", placeholder: true },
      { label: "Inventory Adjustments", path: "/inventory-adjustments", icon: "sliders" },
      { label: "Stock Transfers", path: "/stock-transfers", icon: "shuffle" },
      { label: "Warehouses", path: "/warehouses", icon: "warehouse" },
      { label: "Low Stock", path: "/low-stock", icon: "alert" },
    ],
  },
  {
    title: "Sales",
    items: [
      { label: "Customers", path: "/customers", icon: "users" },
      { label: "Sales Orders", path: "/sales-orders", icon: "cart" },
      { label: "Packages", path: "/packages", icon: "package", placeholder: true },
      { label: "Invoices", path: "/invoices", icon: "receipt", placeholder: true },
      { label: "Sales Returns", path: "/sales-returns", icon: "undo", placeholder: true },
    ],
  },
  {
    title: "Purchases",
    items: [
      { label: "Vendors", path: "/vendors", icon: "briefcase" },
      { label: "Purchase Orders", path: "/purchase-orders", icon: "clipboard" },
      { label: "Purchase Receives", path: "/purchase-receives", icon: "truck", placeholder: true },
      { label: "Bills", path: "/bills", icon: "bill", placeholder: true },
    ],
  },
  {
    title: "Analytics",
    items: [
      { label: "Reports", path: "/reports", icon: "chart" },
      { label: "Activity Logs", path: "/activity-logs", icon: "activity" },
      { label: "Audit Logs", path: "/audit-logs", icon: "shield" },
    ],
  },
  {
    title: "Admin",
    items: [
      { label: "Users", path: "/users", icon: "userCog" },
      { label: "Tenants", path: "/tenants", icon: "building", superAdminOnly: true },
      { label: "Subscription", path: "/subscription", icon: "sparkles" },
      { label: "Settings", path: "/settings", icon: "settings" },
    ],
  },
  {
    title: "AI",
    items: [{ label: "AI Assistant", path: "/ai-assistant", icon: "stars", placeholder: true }],
  },
];

export const quickCreateItems = [
  { label: "New Item", path: "/items/new", icon: "box" },
  { label: "New Customer", path: "/customers", icon: "users" },
  { label: "New Vendor", path: "/vendors", icon: "briefcase" },
  { label: "New Sales Order", path: "/sales-orders/new", icon: "cart" },
  { label: "New Purchase Order", path: "/purchase-orders/new", icon: "clipboard" },
  { label: "Stock Adjustment", path: "/inventory-adjustments", icon: "sliders" },
  { label: "Stock Transfer", path: "/stock-transfers", icon: "shuffle" },
];

export const settingsNavigation = [
  { key: "organization", label: "Organization Profile", icon: "building" },
  { key: "users", label: "Users & Roles", icon: "users" },
  { key: "warehouses", label: "Warehouses", icon: "warehouse" },
  { key: "taxes", label: "Taxes", icon: "receipt" },
  { key: "preferences", label: "Preferences", icon: "sliders" },
  { key: "numbers", label: "Number Series", icon: "hash" },
  { key: "subscription", label: "Subscription", icon: "sparkles" },
  { key: "security", label: "Security", icon: "shield" },
  { key: "notifications", label: "Notifications", icon: "bell" },
  { key: "integrations", label: "Integrations", icon: "plug" },
];
