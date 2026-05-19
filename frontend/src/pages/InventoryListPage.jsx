import { useEffect, useMemo, useState } from "react";

import { DataTable } from "../components/DataTable";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import api from "../lib/api";
import { formatCurrency, formatDateTime, formatNumber } from "../lib/format";

const inventoryConfigs = {
  products: {
    eyebrow: "Inventory Catalog",
    title: "Items",
    description: "Manage your item catalog with live stock posture, reorder visibility, and tracking controls.",
    createLabel: "+ New Item",
    createTo: "/items/new",
    filters: [
      { label: "All Items", value: "all" },
      { label: "Active Items", value: "ACTIVE" },
      { label: "Archived Items", value: "ARCHIVED" },
      { label: "Low Stock Items", value: "LOW_STOCK" },
    ],
    searchPlaceholder: "Search by item name, SKU, or barcode",
  },
  warehouses: {
    eyebrow: "Inventory Locations",
    title: "Warehouses",
    description: "Review every stock location with primary-site visibility, product counts, and location context.",
    createLabel: "+ New Warehouse",
    createTo: "/warehouses/new",
    filters: [
      { label: "All Warehouses", value: "all" },
      { label: "Active Warehouses", value: "ACTIVE" },
      { label: "Archived Warehouses", value: "ARCHIVED" },
      { label: "Primary Warehouse", value: "PRIMARY" },
    ],
    searchPlaceholder: "Search warehouse name, code, city, or manager",
  },
  inventoryTransactions: {
    eyebrow: "Movement Ledger",
    title: "Inventory Transactions",
    description: "Inspect stock movement history with warehouse, item, quantity, reference, and operator context.",
    filters: [
      { label: "All Transactions", value: "all" },
      { label: "Stock In", value: "STOCK_IN" },
      { label: "Stock Out", value: "STOCK_OUT" },
      { label: "Adjustment", value: "ADJUSTMENT" },
      { label: "Transfer In", value: "TRANSFER_IN" },
      { label: "Transfer Out", value: "TRANSFER_OUT" },
      { label: "Purchase Receive", value: "PURCHASE_RECEIVE" },
      { label: "Sales Deduct", value: "SALES_ORDER_DEDUCT" },
    ],
    searchPlaceholder: "Search by item, warehouse, reference, or user",
  },
  stockTransfers: {
    eyebrow: "Stock Movement",
    title: "Stock Transfers",
    description: "Coordinate draft, in-transit, and completed stock moves across your warehouse network.",
    createLabel: "+ New Transfer",
    createTo: "/inventory/transfers/new",
    filters: [
      { label: "All Transfers", value: "all" },
      { label: "Draft", value: "DRAFT" },
      { label: "In Transit", value: "IN_TRANSIT" },
      { label: "Completed", value: "COMPLETED" },
      { label: "Cancelled", value: "CANCELLED" },
    ],
    searchPlaceholder: "Search by transfer number, notes, or warehouse",
  },
};

function buildMap(items, key = "id") {
  return new Map(items.map((item) => [item[key], item]));
}

function inventoryFilter(kind, row, filterValue) {
  if (filterValue === "all") {
    return true;
  }

  if (kind === "products" && filterValue === "LOW_STOCK") {
    return Boolean(row.low_stock);
  }

  if (kind === "warehouses" && filterValue === "PRIMARY") {
    return Boolean(row.is_default);
  }

  if (kind === "inventoryTransactions") {
    return row.transaction_type === filterValue;
  }

  return String(row.status ?? "").toUpperCase() === filterValue;
}

export function InventoryListPage({ kind }) {
  const config = inventoryConfigs[kind];
  const [query, setQuery] = useState("");
  const [filterValue, setFilterValue] = useState(config.filters[0]?.value ?? "all");
  const [sortValue, setSortValue] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: "",
    rows: [],
    metrics: [],
    sourceNote: "",
  });

  useEffect(() => {
    let active = true;

    async function load() {
      setState((current) => ({ ...current, loading: true, error: "" }));

      try {
        if (kind === "products") {
          const [productsResponse, categoriesResponse, brandsResponse, summaryResponse, lowStockResponse] = await Promise.all([
            api.get("/products", { params: { page_size: 100 } }),
            api.get("/categories", { params: { page_size: 100 } }),
            api.get("/brands", { params: { page_size: 100 } }),
            api.get("/reports/inventory-summary"),
            api.get("/reports/low-stock"),
          ]);

          if (!active) return;

          const categoryMap = buildMap(categoriesResponse.data.items ?? []);
          const brandMap = buildMap(brandsResponse.data.items ?? []);
          const summaryMap = buildMap(summaryResponse.data.rows ?? [], "product_id");
          const lowStockIds = new Set((lowStockResponse.data.rows ?? []).map((row) => row.product_id));
          const rows = (productsResponse.data.items ?? []).map((product) => {
            const summary = summaryMap.get(product.id);
            return {
              ...product,
              category_name: categoryMap.get(product.category_id)?.name ?? "Uncategorized",
              brand_name: brandMap.get(product.brand_id)?.name ?? "Unbranded",
              stock_on_hand: Number(summary?.total_quantity ?? 0),
              available_stock: Number(summary?.available_quantity ?? 0),
              inventory_value: Number(summary?.inventory_value ?? 0),
              low_stock: lowStockIds.has(product.id),
            };
          });

          setSortValue((current) => current || "name");
          setState({
            loading: false,
            error: "",
            rows,
            metrics: [
              { label: "Total Items", value: formatNumber(rows.length), delta: "Catalog records", tone: "neutral" },
              { label: "Low Stock", value: formatNumber(rows.filter((row) => row.low_stock).length), delta: "Need replenishment", tone: "warning" },
              { label: "Quantity In Hand", value: formatNumber(rows.reduce((sum, row) => sum + row.stock_on_hand, 0)), delta: "Across all items", tone: "info" },
              { label: "Tracked Items", value: formatNumber(rows.filter((row) => row.serial_tracking_enabled || row.batch_tracking_enabled).length), delta: "Serial or batch enabled", tone: "positive" },
            ],
            sourceNote: `${formatNumber(rows.filter((row) => row.status === "ACTIVE").length)} active items are currently available across the tenant catalog.`,
          });
          return;
        }

        if (kind === "warehouses") {
          const [warehousesResponse, stockResponse] = await Promise.all([
            api.get("/warehouses", { params: { page_size: 100 } }),
            api.get("/reports/warehouse-stock"),
          ]);

          if (!active) return;

          const stockByWarehouse = new Map();
          (stockResponse.data.rows ?? []).forEach((row) => {
            const current = stockByWarehouse.get(row.warehouse_id) ?? {
              product_count: 0,
              total_quantity: 0,
              available_quantity: 0,
            };
            current.product_count += 1;
            current.total_quantity += Number(row.quantity ?? 0);
            current.available_quantity += Number(row.available_quantity ?? 0);
            stockByWarehouse.set(row.warehouse_id, current);
          });

          const rows = (warehousesResponse.data.items ?? []).map((warehouse) => {
            const aggregate = stockByWarehouse.get(warehouse.id) ?? {
              product_count: 0,
              total_quantity: 0,
              available_quantity: 0,
            };
            const location = [warehouse.city, warehouse.state, warehouse.country].filter(Boolean).join(", ");
            return {
              ...warehouse,
              location,
              product_count: aggregate.product_count,
              total_quantity: aggregate.total_quantity,
              available_quantity: aggregate.available_quantity,
            };
          });

          setSortValue((current) => current || "name");
          setState({
            loading: false,
            error: "",
            rows,
            metrics: [
              { label: "Total Warehouses", value: formatNumber(rows.length), delta: "Storage locations", tone: "neutral" },
              { label: "Primary Sites", value: formatNumber(rows.filter((row) => row.is_default).length), delta: "Default fulfillment sites", tone: "info" },
              { label: "Active Locations", value: formatNumber(rows.filter((row) => row.status === "ACTIVE").length), delta: "Operational warehouses", tone: "positive" },
              { label: "Stock Positions", value: formatNumber(rows.reduce((sum, row) => sum + row.product_count, 0)), delta: "Warehouse-product slots", tone: "warning" },
            ],
            sourceNote: "Location metrics combine warehouse records with live warehouse stock report data.",
          });
          return;
        }

        if (kind === "inventoryTransactions") {
          const [transactionsResponse, productsResponse, warehousesResponse, usersResponse] = await Promise.all([
            api.get("/inventory/transactions", { params: { page_size: 100 } }),
            api.get("/products", { params: { page_size: 100 } }),
            api.get("/warehouses", { params: { page_size: 100 } }),
            api.get("/users", { params: { page_size: 100 } }),
          ]);

          if (!active) return;

          const productMap = buildMap(productsResponse.data.items ?? []);
          const warehouseMap = buildMap(warehousesResponse.data.items ?? []);
          const userMap = buildMap(usersResponse.data.items ?? []);
          const rows = (transactionsResponse.data.items ?? []).map((transaction) => ({
            ...transaction,
            product_name: productMap.get(transaction.product_id)?.name ?? `Item #${transaction.product_id}`,
            product_sku: productMap.get(transaction.product_id)?.sku ?? "—",
            warehouse_name: warehouseMap.get(transaction.warehouse_id)?.name ?? `Warehouse #${transaction.warehouse_id}`,
            actor_name: userMap.get(transaction.created_by)?.name ?? `User #${transaction.created_by}`,
            reference_label: transaction.reference_type
              ? `${transaction.reference_type.replaceAll("_", " ")}${transaction.reference_id ? ` #${transaction.reference_id}` : ""}`
              : "Manual",
          }));

          setSortValue((current) => current || "created_at");
          setState({
            loading: false,
            error: "",
            rows,
            metrics: [
              { label: "All Movements", value: formatNumber(rows.length), delta: "Logged transactions", tone: "neutral" },
              { label: "Stock In", value: formatNumber(rows.filter((row) => row.transaction_type === "STOCK_IN").length), delta: "Inbound moves", tone: "positive" },
              { label: "Stock Out", value: formatNumber(rows.filter((row) => row.transaction_type === "STOCK_OUT").length), delta: "Outbound moves", tone: "warning" },
              { label: "Adjustments", value: formatNumber(rows.filter((row) => row.transaction_type === "ADJUSTMENT").length), delta: "Count corrections", tone: "info" },
            ],
            sourceNote: "This ledger is backend-backed and includes stock in, stock out, adjustments, transfers, purchasing, and sales deductions.",
          });
          return;
        }

        if (kind === "stockTransfers") {
          const [transfersResponse, warehousesResponse, usersResponse] = await Promise.all([
            api.get("/inventory/transfers", { params: { page_size: 100 } }),
            api.get("/warehouses", { params: { page_size: 100 } }),
            api.get("/users", { params: { page_size: 100 } }),
          ]);

          if (!active) return;

          const warehouseMap = buildMap(warehousesResponse.data.items ?? []);
          const userMap = buildMap(usersResponse.data.items ?? []);
          const rows = (transfersResponse.data.items ?? []).map((transfer) => ({
            ...transfer,
            source_name: warehouseMap.get(transfer.source_warehouse_id)?.name ?? `Warehouse #${transfer.source_warehouse_id}`,
            destination_name: warehouseMap.get(transfer.destination_warehouse_id)?.name ?? `Warehouse #${transfer.destination_warehouse_id}`,
            owner_name: userMap.get(transfer.created_by)?.name ?? `User #${transfer.created_by}`,
            item_count: transfer.items?.length ?? 0,
          }));

          setSortValue((current) => current || "created_at");
          setState({
            loading: false,
            error: "",
            rows,
            metrics: [
              { label: "Transfers", value: formatNumber(rows.length), delta: "All transfer records", tone: "neutral" },
              { label: "Draft", value: formatNumber(rows.filter((row) => row.status === "DRAFT").length), delta: "Still editable", tone: "info" },
              { label: "In Transit", value: formatNumber(rows.filter((row) => row.status === "IN_TRANSIT").length), delta: "Awaiting completion", tone: "warning" },
              { label: "Completed", value: formatNumber(rows.filter((row) => row.status === "COMPLETED").length), delta: "Stock already moved", tone: "positive" },
            ],
            sourceNote: "Transfer state is driven by the live stock transfer workflow and reflected from backend status transitions.",
          });
        }
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load this inventory workspace.",
          rows: [],
          metrics: [],
          sourceNote: "",
        });
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [kind, reloadKey]);

  const columns = useMemo(() => {
    if (kind === "products") {
      return [
        { key: "name", label: "Item" },
        { key: "sku", label: "SKU" },
        { key: "category_name", label: "Category" },
        { key: "brand_name", label: "Brand" },
        { key: "stock_on_hand", label: "Stock on Hand" },
        { key: "available_stock", label: "Available" },
        { key: "reorder_level", label: "Reorder Level" },
        { key: "selling_price", label: "Selling Price", kind: "currency" },
        {
          key: "status",
          label: "Status",
          render: (_, row) => (row.low_stock ? <StatusBadge value="LOW_STOCK" /> : <StatusBadge value={row.status} />),
        },
      ];
    }

    if (kind === "warehouses") {
      return [
        { key: "name", label: "Warehouse" },
        { key: "code", label: "Code" },
        { key: "location", label: "Location" },
        { key: "manager_name", label: "Manager" },
        { key: "product_count", label: "Product Count" },
        { key: "available_quantity", label: "Available Qty" },
        {
          key: "is_default",
          label: "Primary",
          render: (value) => (value ? <StatusBadge value="PRIMARY" /> : "—"),
        },
        { key: "status", label: "Status", kind: "status" },
      ];
    }

    if (kind === "inventoryTransactions") {
      return [
        { key: "created_at", label: "Date / Time", kind: "date" },
        { key: "transaction_type", label: "Type", kind: "status" },
        {
          key: "product_name",
          label: "Item",
          render: (value, row) => (
            <div className="inventory-cell-stack">
              <strong>{value}</strong>
              <span>{row.product_sku}</span>
            </div>
          ),
        },
        { key: "warehouse_name", label: "Warehouse" },
        {
          key: "quantity",
          label: "Quantity",
          render: (value) => {
            const quantity = Number(value ?? 0);
            const tone = quantity > 0 ? "positive" : quantity < 0 ? "negative" : "neutral";
            const prefix = quantity > 0 ? "+" : "";
            return <span className={`inventory-quantity inventory-quantity-${tone}`}>{`${prefix}${quantity}`}</span>;
          },
        },
        { key: "reference_label", label: "Reference" },
        { key: "actor_name", label: "User" },
      ];
    }

    return [
      { key: "id", label: "Transfer #" },
      { key: "source_name", label: "Source" },
      { key: "destination_name", label: "Destination" },
      { key: "item_count", label: "Items" },
      { key: "owner_name", label: "Owner" },
      { key: "status", label: "Status", kind: "status" },
      { key: "created_at", label: "Created", kind: "date" },
    ];
  }, [kind]);

  const rowLink = useMemo(() => {
    if (kind === "products") return (id) => `/items/${id}`;
    if (kind === "warehouses") return (id) => `/warehouses/${id}`;
    if (kind === "stockTransfers") return (id) => `/inventory/transfers/${id}`;
    return (_, row) => `/items/${row.product_id}`;
  }, [kind]);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={config.eyebrow}
        title={config.title}
        description={config.description}
        backTo="/"
      />

      <div className="metric-grid">
        {state.metrics.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} delta={metric.delta} tone={metric.tone} />
        ))}
      </div>

      <DataTable
        title={config.title}
        description={config.description}
        rows={state.rows}
        columns={columns}
        filters={config.filters}
        createLabel={config.createLabel}
        createTo={config.createTo}
        searchPlaceholder={config.searchPlaceholder}
        rowLink={rowLink}
        isLoading={state.loading}
        error={state.error}
        onRetry={() => setReloadKey((current) => current + 1)}
        sourceNote={state.sourceNote}
        query={query}
        onQueryChange={setQuery}
        filterValue={filterValue}
        onFilterChange={setFilterValue}
        sortValue={sortValue}
        onSortChange={setSortValue}
        filterRow={(row, nextFilter) => inventoryFilter(kind, row, nextFilter)}
        hideHeaderCopy
        emptyState={{
          icon: kind === "warehouses" ? "warehouse" : kind === "inventoryTransactions" ? "activity" : kind === "stockTransfers" ? "shuffle" : "box",
          title:
            kind === "products"
              ? "No items yet"
              : kind === "warehouses"
                ? "No warehouses yet"
                : kind === "inventoryTransactions"
                  ? "No inventory movements yet"
                  : "No stock transfers yet",
          description:
            kind === "products"
              ? "Create your first item to start tracking stock, pricing, and reorder controls."
              : kind === "warehouses"
                ? "Create a warehouse to start managing stock locations and transfer flows."
                : kind === "inventoryTransactions"
                  ? "Stock movements will appear here once inventory starts moving in or out of warehouses."
                  : "Create a transfer draft when you need to move stock between warehouses.",
          actionLabel: config.createLabel,
          actionTo: config.createTo,
        }}
      />
    </div>
  );
}
