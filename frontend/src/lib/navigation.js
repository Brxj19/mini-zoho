export const homeNavigation = { label: "Home", path: "/", icon: "home" };

export const navigationGroups = [
  {
    title: "Inventory",
    items: [
      { label: "Items", path: "/items", icon: "box" },
      { label: "Categories", path: "/categories", icon: "layers", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Brands", path: "/brands", icon: "stars", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Item Groups", path: "/item-groups", icon: "layers" },
      { label: "Inventory Adjustments", path: "/inventory/adjustment", icon: "sliders", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Stock Transfers", path: "/inventory/transfers", icon: "shuffle", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Warehouses", path: "/warehouses", icon: "warehouse", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
      { label: "Low Stock", path: "/inventory/low-stock", icon: "alert" },
    ],
  },
  {
    title: "Sales",
    items: [
      { label: "Customers", path: "/customers", icon: "users", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "SALES_STAFF"] },
      { label: "Sales Orders", path: "/sales-orders", icon: "cart" },
      { label: "Packages", path: "/packages", icon: "package" },
      { label: "Invoices", path: "/invoices", icon: "receipt" },
      { label: "Sales Returns", path: "/sales-returns", icon: "undo" },
    ],
  },
  {
    title: "Purchases",
    items: [
      { label: "Vendors", path: "/vendors", icon: "briefcase", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER", "PURCHASE_STAFF"] },
      { label: "Purchase Orders", path: "/purchase-orders", icon: "clipboard" },
      { label: "Purchase Receives", path: "/purchase-receives", icon: "truck" },
      { label: "Bills", path: "/bills", icon: "bill" },
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
      { label: "Users", path: "/users", icon: "userCog", roles: ["SUPER_ADMIN", "TENANT_ADMIN"] },
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
  { label: "New Item", path: "/items/new", icon: "box", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
  { label: "New Category", path: "/categories/new", icon: "layers", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
  { label: "New Brand", path: "/brands/new", icon: "stars", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
  { label: "New Customer", path: "/customers/new", icon: "users", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "SALES_STAFF"] },
  { label: "New Vendor", path: "/vendors/new", icon: "briefcase", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER", "PURCHASE_STAFF"] },
  { label: "New Warehouse", path: "/warehouses/new", icon: "warehouse", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
  { label: "New Sales Order", path: "/sales-orders/new", icon: "cart" },
  { label: "New Purchase Order", path: "/purchase-orders/new", icon: "clipboard" },
  { label: "Stock In", path: "/inventory/stock-in", icon: "packagePlus", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
  { label: "Stock Transfer", path: "/inventory/transfers/new", icon: "shuffle", roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"] },
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
