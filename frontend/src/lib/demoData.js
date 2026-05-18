export const dashboardData = {
  tenantMetrics: [
    { label: "Quantity in Hand", value: "12,480", delta: "+4.8%", tone: "positive" },
    { label: "Quantity to be Received", value: "1,240", delta: "6 open POs", tone: "neutral" },
    { label: "Low-stock Items", value: "18", delta: "Needs reorder", tone: "warning" },
    { label: "Sales Orders", value: "94", delta: "12 pending actions", tone: "info" },
  ],
  superAdminMetrics: [
    { label: "Total Tenants", value: "48", delta: "+5 this month", tone: "info" },
    { label: "Active Tenants", value: "44", delta: "91.6% healthy", tone: "positive" },
    { label: "Disabled Tenants", value: "4", delta: "Needs follow-up", tone: "warning" },
    { label: "Platform Users", value: "386", delta: "+22 this week", tone: "neutral" },
  ],
  salesActivity: [
    { label: "To Be Packed", value: 11 },
    { label: "To Be Shipped", value: 8 },
    { label: "To Be Delivered", value: 5 },
    { label: "To Be Invoiced", value: 7 },
  ],
  inventorySummary: [
    { label: "Quantity in hand", value: "12,480" },
    { label: "Quantity to be received", value: "1,240" },
  ],
  productDetails: [
    { label: "Low-stock items", value: 18 },
    { label: "All item groups", value: 12 },
    { label: "All items", value: 248 },
    { label: "Unconfirmed items", value: 4 },
    { label: "Active items", value: "94%" },
  ],
  topSellingItems: [
    { name: "Northstar Mesh Chair", sku: "NS-CHAIR-01", units: 124, revenue: "$24,900" },
    { name: "Beacon Standing Desk", sku: "NS-DESK-02", units: 87, revenue: "$43,500" },
    { name: "Orbit Monitor Arm", sku: "NS-ARM-09", units: 73, revenue: "$10,220" },
  ],
  topStockedItems: [
    { name: "Orbit Monitor Arm", quantity: 410, value: "$57,400" },
    { name: "Northstar Cable Dock", quantity: 380, value: "$18,240" },
    { name: "Beacon Standing Desk", quantity: 228, value: "$114,000" },
  ],
  salesSummary: [
    { label: "Draft", value: 14 },
    { label: "Confirmed", value: 21 },
    { label: "Packed", value: 8 },
    { label: "Shipped", value: 17 },
    { label: "Delivered", value: 34 },
  ],
  purchaseSummary: [
    { label: "Draft", value: 7 },
    { label: "Issued", value: 9 },
    { label: "Partially Received", value: 4 },
    { label: "Received", value: 19 },
  ],
  pendingActions: {
    sales: [
      { label: "To Be Packed", value: 11 },
      { label: "To Be Shipped", value: 8 },
      { label: "To Be Delivered", value: 5 },
      { label: "To Be Invoiced", value: 7 },
    ],
    purchases: [
      { label: "To Be Received", value: 6 },
      { label: "Receive In Progress", value: 2 },
    ],
    inventory: [{ label: "Below Reorder Level", value: 18 }],
  },
  recentActivities: [
    { title: "SO-210 packed", detail: "Prepared for dispatch from Central Warehouse.", time: "12m ago" },
    { title: "PO-204 received", detail: "Partial receive completed by A. Sharma.", time: "31m ago" },
    { title: "Stock adjustment approved", detail: "Aisle recount updated 4 SKUs.", time: "1h ago" },
    { title: "Low stock alert", detail: "Beacon Standing Desk fell below reorder level.", time: "2h ago" },
  ],
  notifications: [
    { title: "Three stock transfers require completion", kind: "warning" },
    { title: "Weekly sales report available for export", kind: "info" },
    { title: "All critical health checks are green", kind: "success" },
  ],
};

const items = [
  {
    id: "item-1",
    name: "Northstar Mesh Chair",
    sku: "NS-CHAIR-01",
    category: "Seating",
    brand: "Northstar",
    stockOnHand: 124,
    reorderLevel: 32,
    sellingPrice: "$199",
    status: "ACTIVE",
    barcode: "8901234567001",
    unit: "pcs",
    costPrice: "$132",
    description: "Ergonomic chair with breathable mesh back.",
  },
  {
    id: "item-2",
    name: "Beacon Standing Desk",
    sku: "NS-DESK-02",
    category: "Desks",
    brand: "Beacon",
    stockOnHand: 18,
    reorderLevel: 24,
    sellingPrice: "$499",
    status: "LOW_STOCK",
    barcode: "8901234567002",
    unit: "pcs",
    costPrice: "$352",
    description: "Motorized sit-stand desk with walnut top.",
  },
  {
    id: "item-3",
    name: "Orbit Monitor Arm",
    sku: "NS-ARM-09",
    category: "Accessories",
    brand: "Orbit",
    stockOnHand: 410,
    reorderLevel: 75,
    sellingPrice: "$140",
    status: "ACTIVE",
    barcode: "8901234567003",
    unit: "pcs",
    costPrice: "$82",
    description: "Gas-spring dual monitor arm with cable routing.",
  },
  {
    id: "item-4",
    name: "Northstar Cable Dock",
    sku: "NS-DOCK-12",
    category: "Accessories",
    brand: "Northstar",
    stockOnHand: 380,
    reorderLevel: 110,
    sellingPrice: "$48",
    status: "ACTIVE",
    barcode: "8901234567004",
    unit: "pcs",
    costPrice: "$19",
    description: "Desk cable organizer with magnetic base.",
  },
  {
    id: "item-5",
    name: "Harbor Task Light",
    sku: "NS-LIGHT-06",
    category: "Lighting",
    brand: "Harbor",
    stockOnHand: 0,
    reorderLevel: 20,
    sellingPrice: "$72",
    status: "INACTIVE",
    barcode: "8901234567005",
    unit: "pcs",
    costPrice: "$34",
    description: "Adjustable LED task lamp with dimmer.",
  },
];

const warehouses = [
  {
    id: "wh-1",
    name: "Central Warehouse",
    location: "Bengaluru, India",
    stockCount: 642,
    manager: "Akash Sharma",
    primary: true,
    status: "ACTIVE",
  },
  {
    id: "wh-2",
    name: "North Hub",
    location: "Delhi, India",
    stockCount: 214,
    manager: "Priya Verma",
    primary: false,
    status: "ACTIVE",
  },
  {
    id: "wh-3",
    name: "Overflow Storage",
    location: "Pune, India",
    stockCount: 58,
    manager: "Vikram Roy",
    primary: false,
    status: "INACTIVE",
  },
];

const customers = [
  { id: "cust-1", name: "Horizon Interiors", email: "ops@horizoninteriors.co", phone: "+91 98765 10001", status: "ACTIVE", city: "Mumbai" },
  { id: "cust-2", name: "Blue Creek Offices", email: "buying@bluecreek.io", phone: "+91 98765 10002", status: "ACTIVE", city: "Bengaluru" },
  { id: "cust-3", name: "Craftline Studio", email: "studio@craftline.in", phone: "+91 98765 10003", status: "INACTIVE", city: "Chennai" },
  { id: "cust-4", name: "Urban Grid Retail", email: "stores@urbangrid.in", phone: "+91 98765 10004", status: "ACTIVE", city: "Hyderabad" },
];

const vendors = [
  { id: "vendor-1", name: "Atlas Components", email: "sales@atlascomponents.com", phone: "+91 98765 20001", status: "ACTIVE", city: "Pune" },
  { id: "vendor-2", name: "Everbeam Lighting", email: "contact@everbeam.co", phone: "+91 98765 20002", status: "ACTIVE", city: "Surat" },
  { id: "vendor-3", name: "Forge Woodworks", email: "orders@forgewoodworks.com", phone: "+91 98765 20003", status: "ACTIVE", city: "Jaipur" },
  { id: "vendor-4", name: "Linea Metal", email: "support@lineametal.in", phone: "+91 98765 20004", status: "INACTIVE", city: "Noida" },
];

const salesOrders = [
  { id: "SO-210", date: "2026-05-18", reference: "REF-4901", customerName: "Horizon Interiors", status: "CONFIRMED", amount: "$8,420" },
  { id: "SO-209", date: "2026-05-17", reference: "REF-4900", customerName: "Blue Creek Offices", status: "PACKED", amount: "$14,220" },
  { id: "SO-208", date: "2026-05-16", reference: "REF-4899", customerName: "Urban Grid Retail", status: "SHIPPED", amount: "$4,980" },
  { id: "SO-207", date: "2026-05-14", reference: "REF-4892", customerName: "Craftline Studio", status: "DELIVERED", amount: "$21,350" },
];

const purchaseOrders = [
  { id: "PO-204", date: "2026-05-18", reference: "V-3812", vendorName: "Atlas Components", status: "ISSUED", amount: "$11,920" },
  { id: "PO-203", date: "2026-05-16", reference: "V-3811", vendorName: "Forge Woodworks", status: "PARTIALLY_RECEIVED", amount: "$16,440" },
  { id: "PO-202", date: "2026-05-13", reference: "V-3810", vendorName: "Everbeam Lighting", status: "RECEIVED", amount: "$6,860" },
  { id: "PO-201", date: "2026-05-10", reference: "V-3809", vendorName: "Linea Metal", status: "DRAFT", amount: "$9,200" },
];

const stockTransfers = [
  { id: "TR-101", source: "Central Warehouse", destination: "North Hub", status: "IN_TRANSIT", items: 4, updatedAt: "2026-05-18 10:22" },
  { id: "TR-100", source: "North Hub", destination: "Central Warehouse", status: "COMPLETED", items: 2, updatedAt: "2026-05-17 15:08" },
  { id: "TR-099", source: "Central Warehouse", destination: "Overflow Storage", status: "DRAFT", items: 6, updatedAt: "2026-05-16 18:44" },
];

const inventoryAdjustments = [
  { id: "ADJ-051", date: "2026-05-18", warehouse: "Central Warehouse", reason: "Cycle count", status: "COMPLETED", quantity: "+12" },
  { id: "ADJ-050", date: "2026-05-17", warehouse: "North Hub", reason: "Damaged stock", status: "COMPLETED", quantity: "-3" },
  { id: "ADJ-049", date: "2026-05-15", warehouse: "Central Warehouse", reason: "Barcode mismatch", status: "DRAFT", quantity: "+0" },
];

const lowStock = items.filter((item) => item.status === "LOW_STOCK" || item.stockOnHand <= item.reorderLevel);

const transactions = [
  { id: "TX-9001", date: "2026-05-18 09:30", type: "STOCK_IN", product: "Northstar Mesh Chair", warehouse: "Central Warehouse", user: "Akash Sharma", reference: "PO-204", quantity: "+24" },
  { id: "TX-9002", date: "2026-05-18 10:11", type: "TRANSFER_OUT", product: "Orbit Monitor Arm", warehouse: "Central Warehouse", user: "Akash Sharma", reference: "TR-101", quantity: "-8" },
  { id: "TX-9003", date: "2026-05-18 10:12", type: "TRANSFER_IN", product: "Orbit Monitor Arm", warehouse: "North Hub", user: "Priya Verma", reference: "TR-101", quantity: "+8" },
  { id: "TX-9004", date: "2026-05-17 14:42", type: "SALES_DEDUCT", product: "Beacon Standing Desk", warehouse: "Central Warehouse", user: "Rohan Gupta", reference: "SO-209", quantity: "-4" },
  { id: "TX-9005", date: "2026-05-17 16:05", type: "PURCHASE_RECEIVE", product: "Northstar Cable Dock", warehouse: "Central Warehouse", user: "A. Sharma", reference: "PO-203", quantity: "+60" },
  { id: "TX-9006", date: "2026-05-16 11:20", type: "ADJUSTMENT", product: "Harbor Task Light", warehouse: "Overflow Storage", user: "Vikram Roy", reference: "ADJ-050", quantity: "-3" },
];

const users = [
  { id: "user-1", name: "Brajesh Kumar", email: "superadmin@example.com", role: "SUPER_ADMIN", status: "ACTIVE", lastLogin: "2m ago" },
  { id: "user-2", name: "Akash Sharma", email: "akash@northstar.io", role: "INVENTORY_MANAGER", status: "ACTIVE", lastLogin: "11m ago" },
  { id: "user-3", name: "Rohan Gupta", email: "rohan@northstar.io", role: "SALES_STAFF", status: "ACTIVE", lastLogin: "28m ago" },
  { id: "user-4", name: "Priya Verma", email: "priya@northstar.io", role: "PURCHASE_STAFF", status: "INACTIVE", lastLogin: "Yesterday" },
];

const tenants = [
  { id: "tenant-1", companyName: "Northstar Retail", contactEmail: "ops@northstar.io", plan: "Growth", status: "ACTIVE", users: 24 },
  { id: "tenant-2", companyName: "Riverline Home", contactEmail: "hello@riverlinehome.com", plan: "Starter", status: "ACTIVE", users: 10 },
  { id: "tenant-3", companyName: "Craftline Studio", contactEmail: "studio@craftline.in", plan: "Pro", status: "DISABLED", users: 7 },
];

const activityLogs = [
  { id: "activity-1", actor: "Akash Sharma", action: "Completed transfer TR-100", module: "Stock Transfers", createdAt: "2026-05-17 15:08" },
  { id: "activity-2", actor: "Rohan Gupta", action: "Packed sales order SO-209", module: "Sales Orders", createdAt: "2026-05-17 14:52" },
  { id: "activity-3", actor: "Priya Verma", action: "Issued purchase order PO-204", module: "Purchase Orders", createdAt: "2026-05-16 09:20" },
];

const auditLogs = [
  { id: "audit-1", actor: "Brajesh Kumar", action: "Updated tenant subscription", module: "Tenants", createdAt: "2026-05-18 09:01", severity: "INFO" },
  { id: "audit-2", actor: "Akash Sharma", action: "Adjusted stock for Harbor Task Light", module: "Inventory", createdAt: "2026-05-17 16:05", severity: "WARNING" },
  { id: "audit-3", actor: "System", action: "Generated weekly inventory report", module: "Reports", createdAt: "2026-05-17 06:00", severity: "SUCCESS" },
];

const reportRows = {
  "inventory-summary": [
    { metric: "Active items", value: 248 },
    { metric: "Low-stock items", value: 18 },
    { metric: "Out-of-stock items", value: 6 },
    { metric: "Stock value", value: "$218,900" },
  ],
  "stock-movement": transactions.map((transaction) => ({
    date: transaction.date,
    type: transaction.type,
    product: transaction.product,
    warehouse: transaction.warehouse,
    quantity: transaction.quantity,
  })),
  "warehouse-stock": warehouses.map((warehouse) => ({
    warehouse: warehouse.name,
    location: warehouse.location,
    items: warehouse.stockCount,
    status: warehouse.status,
  })),
  "purchase-orders": purchaseOrders.map((order) => ({
    order: order.id,
    vendor: order.vendorName,
    status: order.status,
    amount: order.amount,
  })),
  "sales-orders": salesOrders.map((order) => ({
    order: order.id,
    customer: order.customerName,
    status: order.status,
    amount: order.amount,
  })),
};

export const reportGroups = [
  {
    title: "Inventory Reports",
    reports: [
      { key: "inventory-summary", title: "Inventory Summary", description: "High-level stock health and catalog numbers." },
      { key: "stock-movement", title: "Stock Movement", description: "Track stock in, out, adjustments, and transfers." },
      { key: "warehouse-stock", title: "Warehouse Stock", description: "Warehouse-level item counts and availability." },
    ],
  },
  {
    title: "Sales Reports",
    reports: [{ key: "sales-orders", title: "Sales Orders", description: "Order status, volume, and collection-ready records." }],
  },
  {
    title: "Purchase Reports",
    reports: [{ key: "purchase-orders", title: "Purchase Orders", description: "Receiving progress and vendor-facing order summaries." }],
  },
  {
    title: "Activity Reports",
    reports: [{ key: "activity-log", title: "Activity Stream", description: "Recent system activity and operator actions." }],
  },
];

const collections = {
  items,
  warehouses,
  customers,
  vendors,
  "sales-orders": salesOrders,
  "purchase-orders": purchaseOrders,
  "stock-transfers": stockTransfers,
  "inventory-adjustments": inventoryAdjustments,
  "low-stock": lowStock,
  transactions,
  users,
  tenants,
  "activity-logs": activityLogs,
  "audit-logs": auditLogs,
};

export function getCollection(key) {
  return collections[key] ?? [];
}

export function getRecordById(key, id) {
  return getCollection(key).find((record) => record.id === id);
}

export function getReportRows(reportKey) {
  if (reportKey === "activity-log") {
    return activityLogs;
  }

  return reportRows[reportKey] ?? [];
}
