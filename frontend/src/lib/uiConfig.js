export const roleMatrix = {
  adminOnly: ["SUPER_ADMIN", "TENANT_ADMIN"],
  inventory: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"],
  purchases: ["SUPER_ADMIN", "TENANT_ADMIN", "PURCHASE_STAFF"],
  sales: ["SUPER_ADMIN", "TENANT_ADMIN", "SALES_STAFF"],
  operations: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER", "PURCHASE_STAFF", "SALES_STAFF"],
};

export const navigationGroups = [
  {
    key: "home",
    label: "Home",
    icon: "home",
    matcher: (pathname) => pathname === "/",
    items: [
      { label: "Workspace Overview", path: "/" },
      { label: "Notifications", path: "/notifications" },
    ],
  },
  {
    key: "items",
    label: "Items",
    icon: "box",
    matcher: (pathname) => pathname.startsWith("/products"),
    items: [
      { label: "Products", path: "/products" },
      { label: "Create Product", path: "/products/new", roles: roleMatrix.inventory },
    ],
  },
  {
    key: "inventory",
    label: "Inventory",
    icon: "layers",
    matcher: (pathname) => pathname.startsWith("/inventory"),
    items: [
      { label: "Transactions", path: "/inventory/transactions" },
      { label: "Stock In", path: "/inventory/stock-in", roles: roleMatrix.inventory },
      { label: "Stock Out", path: "/inventory/stock-out", roles: roleMatrix.inventory },
      { label: "Adjustments", path: "/inventory/adjustment", roles: roleMatrix.inventory },
      { label: "Transfers", path: "/inventory/transfers" },
    ],
  },
  {
    key: "sales",
    label: "Sales",
    icon: "cart",
    matcher: (pathname) => pathname.startsWith("/sales-orders") || pathname.startsWith("/customers"),
    items: [
      { label: "Sales Orders", path: "/sales-orders" },
      { label: "Create Sales Order", path: "/sales-orders/new", roles: roleMatrix.sales },
      { label: "Customers", path: "/customers" },
    ],
  },
  {
    key: "purchases",
    label: "Purchases",
    icon: "bag",
    matcher: (pathname) => pathname.startsWith("/purchase-orders") || pathname.startsWith("/vendors"),
    items: [
      { label: "Purchase Orders", path: "/purchase-orders" },
      { label: "Create Purchase Order", path: "/purchase-orders/new", roles: roleMatrix.purchases },
      { label: "Vendors", path: "/vendors" },
    ],
  },
  {
    key: "warehouses",
    label: "Warehouses",
    icon: "warehouse",
    matcher: (pathname) => pathname.startsWith("/warehouses"),
    items: [
      { label: "Locations", path: "/warehouses" },
      { label: "Stock Health", path: "/reports?focus=warehouse" },
    ],
  },
  {
    key: "reports",
    label: "Reports",
    icon: "chart",
    matcher: (pathname) => pathname.startsWith("/reports"),
    items: [
      { label: "Command Center", path: "/reports" },
      { label: "Inventory Summary", path: "/reports?report=inventory-summary" },
      { label: "Order Analytics", path: "/reports?report=sales-orders" },
    ],
  },
  {
    key: "admin",
    label: "Admin",
    icon: "users",
    matcher: (pathname) => pathname.startsWith("/users") || pathname.startsWith("/settings"),
    items: [
      { label: "Users", path: "/users", roles: roleMatrix.adminOnly },
      { label: "Settings", path: "/settings" },
    ],
  },
];

export const resourceConfigs = {
  products: {
    title: "Products",
    description: "Manage SKUs, pricing, vendors, and replenishment settings.",
    endpoint: "/products",
    createPath: "/products/new",
    detailPath: (id) => `/products/${id}`,
    searchPlaceholder: "Search products, SKUs, or barcode",
    columns: [
      { key: "name", label: "Product" },
      { key: "sku", label: "SKU" },
      { key: "unit", label: "Unit" },
      { key: "selling_price", label: "Selling" },
      { key: "reorder_level", label: "Reorder" },
      { key: "status", label: "Status", kind: "status" },
    ],
  },
  warehouses: {
    title: "Warehouses",
    description: "Track stock locations, default sites, and local operations coverage.",
    endpoint: "/warehouses",
    detailPath: (id) => `/warehouses/${id}`,
    searchPlaceholder: "Search location, code, or city",
    columns: [
      { key: "name", label: "Warehouse" },
      { key: "code", label: "Code" },
      { key: "city", label: "City" },
      { key: "manager_name", label: "Manager" },
      { key: "is_default", label: "Default", kind: "boolean" },
      { key: "status", label: "Status", kind: "status" },
    ],
  },
  vendors: {
    title: "Vendors",
    description: "Supplier relationships for inbound purchasing and replenishment.",
    endpoint: "/vendors",
    searchPlaceholder: "Search vendors",
    columns: [
      { key: "name", label: "Vendor" },
      { key: "email", label: "Email" },
      { key: "phone", label: "Phone" },
      { key: "gst_number", label: "Tax ID" },
      { key: "status", label: "Status", kind: "status" },
    ],
  },
  customers: {
    title: "Customers",
    description: "Maintain customer billing details and sales-ready contact records.",
    endpoint: "/customers",
    searchPlaceholder: "Search customers",
    columns: [
      { key: "name", label: "Customer" },
      { key: "email", label: "Email" },
      { key: "phone", label: "Phone" },
      { key: "gst_number", label: "Tax ID" },
      { key: "status", label: "Status", kind: "status" },
    ],
  },
  inventoryTransactions: {
    title: "Inventory Transactions",
    description: "A running ledger of stock movement across warehouses.",
    endpoint: "/inventory/transactions",
    searchPlaceholder: "Filter by transaction context",
    columns: [
      { key: "transaction_type", label: "Type", kind: "status" },
      { key: "product_id", label: "Product ID" },
      { key: "warehouse_id", label: "Warehouse" },
      { key: "quantity", label: "Quantity" },
      { key: "reference_type", label: "Reference" },
      { key: "created_at", label: "Created", kind: "date" },
    ],
  },
  stockTransfers: {
    title: "Stock Transfers",
    description: "Move inventory between locations with full status tracking.",
    endpoint: "/inventory/transfers",
    searchPlaceholder: "Search transfer notes or IDs",
    columns: [
      { key: "id", label: "Transfer #" },
      { key: "source_warehouse_id", label: "Source" },
      { key: "destination_warehouse_id", label: "Destination" },
      { key: "status", label: "Status", kind: "status" },
      { key: "created_by", label: "Owner" },
      { key: "created_at", label: "Created", kind: "date" },
    ],
  },
  purchaseOrders: {
    title: "Purchase Orders",
    description: "Plan inbound stock, issue vendor orders, and receive inventory cleanly.",
    endpoint: "/purchase-orders",
    createPath: "/purchase-orders/new",
    detailPath: (id) => `/purchase-orders/${id}`,
    searchPlaceholder: "Search PO number or note",
    columns: [
      { key: "po_number", label: "PO Number" },
      { key: "vendor_id", label: "Vendor" },
      { key: "order_date", label: "Order Date", kind: "date" },
      { key: "total_amount", label: "Total" },
      { key: "status", label: "Status", kind: "status" },
    ],
  },
  salesOrders: {
    title: "Sales Orders",
    description: "Coordinate reservations, fulfillment, and shipped inventory flow.",
    endpoint: "/sales-orders",
    createPath: "/sales-orders/new",
    detailPath: (id) => `/sales-orders/${id}`,
    searchPlaceholder: "Search SO number or note",
    columns: [
      { key: "so_number", label: "SO Number" },
      { key: "customer_id", label: "Customer" },
      { key: "order_date", label: "Order Date", kind: "date" },
      { key: "total_amount", label: "Total" },
      { key: "status", label: "Status", kind: "status" },
    ],
  },
  users: {
    title: "Users",
    description: "Control workspace access, roles, and operational permissions.",
    endpoint: "/users",
    searchPlaceholder: "Search users",
    columns: [
      { key: "name", label: "Name" },
      { key: "email", label: "Email" },
      { key: "role", label: "Role", kind: "status" },
      { key: "status", label: "Status", kind: "status" },
      { key: "last_login_at", label: "Last Login", kind: "date" },
    ],
  },
};

export const reportCatalog = [
  { key: "inventory-summary", label: "Inventory Summary", endpoint: "/reports/inventory-summary" },
  { key: "stock-movement", label: "Stock Movement", endpoint: "/reports/stock-movement" },
  { key: "low-stock", label: "Low Stock", endpoint: "/reports/low-stock" },
  { key: "warehouse-stock", label: "Warehouse Stock", endpoint: "/reports/warehouse-stock" },
  { key: "product-valuation", label: "Product Valuation", endpoint: "/reports/product-valuation" },
  { key: "purchase-orders", label: "Purchase Orders", endpoint: "/reports/purchase-orders" },
  { key: "sales-orders", label: "Sales Orders", endpoint: "/reports/sales-orders" },
];

export function canAccess(userRole, roles) {
  if (!roles?.length) {
    return true;
  }
  return roles.includes(userRole);
}

export function resolveActiveGroup(pathname) {
  return navigationGroups.find((group) => group.matcher(pathname)) ?? navigationGroups[0];
}
