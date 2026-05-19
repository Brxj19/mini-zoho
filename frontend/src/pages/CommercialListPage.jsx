import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import api from "../lib/api";
import { formatCurrency, formatNumber } from "../lib/format";

const commercialConfigs = {
  customers: {
    eyebrow: "Sales Directory",
    title: "Customers",
    description: "Manage customer accounts, billing details, and contact context used across sales workflows.",
    endpoint: "/customers",
    createTo: "/customers/new",
    createLabel: "+ New Customer",
    rowLink: (id) => `/customers/${id}`,
    filters: [
      { label: "All Customers", value: "all" },
      { label: "Active Customers", value: "ACTIVE" },
      { label: "Archived Customers", value: "ARCHIVED" },
    ],
    searchPlaceholder: "Search customer name, email, phone, or GST",
  },
  vendors: {
    eyebrow: "Purchase Directory",
    title: "Vendors",
    description: "Manage vendors, sourcing contacts, and procurement-ready profile details.",
    endpoint: "/vendors",
    createTo: "/vendors/new",
    createLabel: "+ New Vendor",
    rowLink: (id) => `/vendors/${id}`,
    filters: [
      { label: "All Vendors", value: "all" },
      { label: "Active Vendors", value: "ACTIVE" },
      { label: "Archived Vendors", value: "ARCHIVED" },
    ],
    searchPlaceholder: "Search vendor name, email, phone, or GST",
  },
  salesOrders: {
    eyebrow: "Sales Workflow",
    title: "Sales Orders",
    description: "Track the pipeline from draft through delivery with customer visibility and status-driven action queues.",
    endpoint: "/sales-orders",
    createTo: "/sales-orders/new",
    createLabel: "+ New Sales Order",
    rowLink: (id) => `/sales-orders/${id}`,
    filters: [
      { label: "All Sales Orders", value: "all" },
      { label: "Draft", value: "DRAFT" },
      { label: "Confirmed", value: "CONFIRMED" },
      { label: "Packed", value: "PACKED" },
      { label: "Shipped", value: "SHIPPED" },
      { label: "Delivered", value: "DELIVERED" },
      { label: "Cancelled", value: "CANCELLED" },
    ],
    searchPlaceholder: "Search sales order number or customer",
  },
  purchaseOrders: {
    eyebrow: "Purchase Workflow",
    title: "Purchase Orders",
    description: "Monitor procurement from draft to receiving with vendor context and expected delivery milestones.",
    endpoint: "/purchase-orders",
    createTo: "/purchase-orders/new",
    createLabel: "+ New Purchase Order",
    rowLink: (id) => `/purchase-orders/${id}`,
    filters: [
      { label: "All Purchase Orders", value: "all" },
      { label: "Draft", value: "DRAFT" },
      { label: "Issued", value: "ISSUED" },
      { label: "Partially Received", value: "PARTIALLY_RECEIVED" },
      { label: "Received", value: "RECEIVED" },
      { label: "Cancelled", value: "CANCELLED" },
    ],
    searchPlaceholder: "Search purchase order number or vendor",
  },
  packages: {
    eyebrow: "Sales Fulfillment",
    title: "Packages",
    description: "Bundle sales-order lines into packing, shipping, and delivery records with operational traceability.",
    endpoint: "/packages",
    createTo: "/packages/new",
    createLabel: "+ New Package",
    rowLink: (id) => `/packages/${id}`,
    filters: [
      { label: "All Packages", value: "all" },
      { label: "Draft", value: "DRAFT" },
      { label: "Packed", value: "PACKED" },
      { label: "Shipped", value: "SHIPPED" },
      { label: "Delivered", value: "DELIVERED" },
      { label: "Cancelled", value: "CANCELLED" },
    ],
    searchPlaceholder: "Search package number or sales order",
  },
  invoices: {
    eyebrow: "Revenue Workflow",
    title: "Invoices",
    description: "Review billing records generated from sales orders with sent, paid, and void status visibility.",
    endpoint: "/invoices",
    createTo: "/invoices/new",
    createLabel: "+ New Invoice",
    rowLink: (id) => `/invoices/${id}`,
    filters: [
      { label: "All Invoices", value: "all" },
      { label: "Draft", value: "DRAFT" },
      { label: "Sent", value: "SENT" },
      { label: "Paid", value: "PAID" },
      { label: "Void", value: "VOID" },
    ],
    searchPlaceholder: "Search invoice number",
  },
  salesReturns: {
    eyebrow: "Reverse Logistics",
    title: "Sales Returns",
    description: "Capture returned stock, receive it back into inventory, and track refund progress.",
    endpoint: "/sales-returns",
    createTo: "/sales-returns/new",
    createLabel: "+ New Sales Return",
    rowLink: (id) => `/sales-returns/${id}`,
    filters: [
      { label: "All Sales Returns", value: "all" },
      { label: "Draft", value: "DRAFT" },
      { label: "Received", value: "RECEIVED" },
      { label: "Refunded", value: "REFUNDED" },
      { label: "Cancelled", value: "CANCELLED" },
    ],
    searchPlaceholder: "Search sales return number",
  },
  purchaseReceives: {
    eyebrow: "Inbound Stock",
    title: "Purchase Receives",
    description: "Track goods received against purchase orders and keep warehouse receipt activity visible.",
    endpoint: "/purchase-receives",
    createTo: "/purchase-receives/new",
    createLabel: "+ New Receive",
    rowLink: (id) => `/purchase-receives/${id}`,
    filters: [
      { label: "All Receives", value: "all" },
      { label: "Posted", value: "POSTED" },
      { label: "Cancelled", value: "CANCELLED" },
    ],
    searchPlaceholder: "Search receipt number",
  },
  bills: {
    eyebrow: "Accounts Payable",
    title: "Bills",
    description: "Manage vendor payables created from purchase orders with posted, paid, and void visibility.",
    endpoint: "/bills",
    createTo: "/bills/new",
    createLabel: "+ New Bill",
    rowLink: (id) => `/bills/${id}`,
    filters: [
      { label: "All Bills", value: "all" },
      { label: "Draft", value: "DRAFT" },
      { label: "Posted", value: "POSTED" },
      { label: "Paid", value: "PAID" },
      { label: "Void", value: "VOID" },
    ],
    searchPlaceholder: "Search bill number",
  },
};

function buildMap(items) {
  return new Map(items.map((item) => [item.id, item]));
}

function passesStatusFilter(row, value) {
  if (value === "all") return true;
  return String(row.status ?? "").toUpperCase() === value;
}

export function CommercialListPage({ kind }) {
  const config = commercialConfigs[kind];
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
        if (kind === "customers" || kind === "vendors") {
          const response = await api.get(config.endpoint, { params: { page_size: 100 } });
          if (!active) return;
          const rows = response.data.items ?? [];
          setSortValue((current) => current || "name");
          setState({
            loading: false,
            error: "",
            rows,
            metrics: [
              { label: kind === "customers" ? "Customers" : "Vendors", value: formatNumber(rows.length), delta: "Directory records", tone: "neutral" },
              { label: "Active", value: formatNumber(rows.filter((row) => row.status === "ACTIVE").length), delta: "Operational records", tone: "positive" },
              { label: "With GST", value: formatNumber(rows.filter((row) => row.gst_number).length), delta: "Tax-ready profiles", tone: "info" },
              { label: "With Email", value: formatNumber(rows.filter((row) => row.email).length), delta: "Contactable records", tone: "warning" },
            ],
            sourceNote: `Use the ${kind === "customers" ? "customer" : "vendor"} directory to support downstream order and billing workflows.`,
          });
          return;
        }

        const requests = [api.get(config.endpoint, { params: { page_size: 100 } })];
        if (["salesOrders", "packages", "invoices", "salesReturns"].includes(kind)) {
          requests.push(api.get("/customers", { params: { page_size: 100 } }));
          requests.push(api.get("/sales-orders", { params: { page_size: 100 } }));
        }
        if (["purchaseOrders", "purchaseReceives", "bills"].includes(kind)) {
          requests.push(api.get("/vendors", { params: { page_size: 100 } }));
          requests.push(api.get("/purchase-orders", { params: { page_size: 100 } }));
        }

        const responses = await Promise.all(requests);
        if (!active) return;

        const baseRows = responses[0].data.items ?? [];
        let rows = baseRows;

        if (["salesOrders", "packages", "invoices", "salesReturns"].includes(kind)) {
          const customerMap = buildMap(responses[1].data.items ?? []);
          const salesOrderMap = buildMap(responses[2].data.items ?? []);
          rows = baseRows.map((row) => ({
            ...row,
            customer_name:
              customerMap.get(row.customer_id)?.name ??
              customerMap.get(salesOrderMap.get(row.sales_order_id)?.customer_id)?.name ??
              "—",
            sales_order_number: salesOrderMap.get(row.sales_order_id)?.so_number ?? row.so_number ?? "—",
            item_count: row.items?.length ?? 0,
          }));
        }

        if (["purchaseOrders", "purchaseReceives", "bills"].includes(kind)) {
          const vendorMap = buildMap(responses[1].data.items ?? []);
          const purchaseOrderMap = buildMap(responses[2].data.items ?? []);
          rows = baseRows.map((row) => ({
            ...row,
            vendor_name:
              vendorMap.get(row.vendor_id)?.name ??
              vendorMap.get(purchaseOrderMap.get(row.purchase_order_id)?.vendor_id)?.name ??
              "—",
            purchase_order_number: purchaseOrderMap.get(row.purchase_order_id)?.po_number ?? row.po_number ?? "—",
            item_count: row.items?.length ?? 0,
          }));
        }

        const valueMetric =
          kind === "salesOrders" || kind === "invoices" || kind === "salesReturns"
            ? sumRows(rows, (row) => Number(row.total_amount ?? 0))
            : kind === "purchaseOrders" || kind === "bills"
              ? sumRows(rows, (row) => Number(row.total_amount ?? 0))
              : null;

        setSortValue((current) => current || defaultSortForKind(kind));
        setState({
          loading: false,
          error: "",
          rows,
          metrics: buildMetrics(kind, rows, valueMetric),
          sourceNote: buildSourceNote(kind, rows),
        });
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load this workflow workspace.",
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
  }, [config.endpoint, kind, reloadKey]);

  const columns = useMemo(() => buildColumns(kind), [kind]);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={config.eyebrow}
        title={config.title}
        description={config.description}
        actions={
          <Link className="button button-primary" to={config.createTo}>
            {config.createLabel}
          </Link>
        }
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
        rowLink={config.rowLink}
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
        filterRow={passesStatusFilter}
        emptyState={{
          icon: kind === "customers" ? "users" : kind === "vendors" ? "briefcase" : kind === "purchaseOrders" ? "clipboard" : kind === "bills" ? "bill" : kind === "packages" ? "package" : kind === "invoices" ? "receipt" : kind === "salesReturns" ? "undo" : kind === "purchaseReceives" ? "truck" : "cart",
          title: `No ${config.title.toLowerCase()} yet`,
          description: `Create the first ${config.title.slice(0, -1).toLowerCase()} to start populating this workflow queue.`,
          actionLabel: config.createLabel,
          actionTo: config.createTo,
        }}
      />
    </div>
  );
}

function sumRows(rows, selector) {
  return rows.reduce((sum, row) => sum + selector(row), 0);
}

function defaultSortForKind(kind) {
  if (kind === "customers" || kind === "vendors") return "name";
  if (kind === "salesOrders") return "order_date";
  if (kind === "purchaseOrders") return "order_date";
  if (kind === "invoices") return "invoice_date";
  if (kind === "salesReturns") return "return_date";
  if (kind === "purchaseReceives") return "received_at";
  if (kind === "bills") return "bill_date";
  return "created_at";
}

function buildMetrics(kind, rows, valueMetric) {
  if (kind === "customers" || kind === "vendors") {
    return [
      { label: kind === "customers" ? "Customers" : "Vendors", value: formatNumber(rows.length), delta: "Directory records", tone: "neutral" },
      { label: "Active", value: formatNumber(rows.filter((row) => row.status === "ACTIVE").length), delta: "Ready for use", tone: "positive" },
      { label: "Archived", value: formatNumber(rows.filter((row) => row.status === "ARCHIVED").length), delta: "Not active", tone: "warning" },
      { label: "With GST", value: formatNumber(rows.filter((row) => row.gst_number).length), delta: "Tax-aware profiles", tone: "info" },
    ];
  }

  const totalAmountLabel = ["salesOrders", "purchaseOrders", "invoices", "bills"].includes(kind)
    ? "Total Value"
    : kind === "salesReturns"
      ? "Return Volume"
      : "Workflow Records";

  return [
    { label: "Records", value: formatNumber(rows.length), delta: "Current workflow records", tone: "neutral" },
    { label: "Open", value: formatNumber(rows.filter((row) => !["DELIVERED", "RECEIVED", "PAID", "VOID", "CANCELLED", "REFUNDED"].includes(String(row.status))).length), delta: "Require action", tone: "warning" },
    { label: "Completed", value: formatNumber(rows.filter((row) => ["DELIVERED", "RECEIVED", "PAID", "REFUNDED"].includes(String(row.status))).length), delta: "Closed successfully", tone: "positive" },
    { label: totalAmountLabel, value: valueMetric == null ? formatNumber(rows.length) : formatCurrency(valueMetric), delta: "Operational throughput", tone: "info" },
  ];
}

function buildSourceNote(kind, rows) {
  if (kind === "salesOrders") {
    return `${formatNumber(rows.filter((row) => row.status === "CONFIRMED").length)} orders are currently confirmed and waiting for downstream handling.`;
  }
  if (kind === "purchaseOrders") {
    return `${formatNumber(rows.filter((row) => row.status === "ISSUED").length)} purchase orders are still awaiting receipts.`;
  }
  if (kind === "packages") {
    return "Packages help operational teams follow order fulfillment after confirmation.";
  }
  if (kind === "invoices") {
    return "Invoices extend the order workflow into billing and payment visibility.";
  }
  if (kind === "salesReturns") {
    return "Returns keep reverse-logistics decisions visible alongside the customer order trail.";
  }
  if (kind === "purchaseReceives") {
    return "Receipts represent actual inbound stock posting against purchase commitments.";
  }
  if (kind === "bills") {
    return "Bills bring purchase workflows into payable status tracking.";
  }
  if (kind === "customers") {
    return "Customer profiles feed directly into sales orders, invoices, and returns.";
  }
  return "Vendor profiles feed directly into purchase orders, receipts, and bills.";
}

function buildColumns(kind) {
  switch (kind) {
    case "customers":
      return [
        { key: "name", label: "Customer" },
        { key: "email", label: "Email" },
        { key: "phone", label: "Phone" },
        { key: "gst_number", label: "GST" },
        { key: "status", label: "Status", kind: "status" },
      ];
    case "vendors":
      return [
        { key: "name", label: "Vendor" },
        { key: "email", label: "Email" },
        { key: "phone", label: "Phone" },
        { key: "gst_number", label: "GST" },
        { key: "status", label: "Status", kind: "status" },
      ];
    case "salesOrders":
      return [
        { key: "order_date", label: "Date", kind: "date" },
        { key: "so_number", label: "Sales Order #" },
        { key: "customer_name", label: "Customer" },
        { key: "status", label: "Status", kind: "status" },
        { key: "total_amount", label: "Amount", kind: "currency" },
      ];
    case "purchaseOrders":
      return [
        { key: "order_date", label: "Date", kind: "date" },
        { key: "po_number", label: "Purchase Order #" },
        { key: "vendor_name", label: "Vendor" },
        { key: "expected_delivery_date", label: "Expected Delivery", kind: "date" },
        { key: "status", label: "Status", kind: "status" },
        { key: "total_amount", label: "Amount", kind: "currency" },
      ];
    case "packages":
      return [
        { key: "package_number", label: "Package #" },
        { key: "sales_order_number", label: "Sales Order #" },
        { key: "item_count", label: "Items" },
        { key: "status", label: "Status", kind: "status" },
        { key: "created_at", label: "Created", kind: "date" },
      ];
    case "invoices":
      return [
        { key: "invoice_date", label: "Invoice Date", kind: "date" },
        { key: "invoice_number", label: "Invoice #" },
        { key: "customer_name", label: "Customer" },
        { key: "status", label: "Status", kind: "status" },
        { key: "total_amount", label: "Amount", kind: "currency" },
      ];
    case "salesReturns":
      return [
        { key: "return_date", label: "Return Date", kind: "date" },
        { key: "return_number", label: "Return #" },
        { key: "customer_name", label: "Customer" },
        { key: "status", label: "Status", kind: "status" },
        { key: "created_at", label: "Created", kind: "date" },
      ];
    case "purchaseReceives":
      return [
        { key: "received_at", label: "Received On", kind: "date" },
        { key: "receive_number", label: "Receipt #" },
        { key: "purchase_order_number", label: "Purchase Order #" },
        { key: "vendor_name", label: "Vendor" },
        { key: "status", label: "Status", kind: "status" },
      ];
    default:
      return [
        { key: "bill_date", label: "Bill Date", kind: "date" },
        { key: "bill_number", label: "Bill #" },
        { key: "purchase_order_number", label: "Purchase Order #" },
        { key: "vendor_name", label: "Vendor" },
        { key: "status", label: "Status", kind: "status" },
        { key: "total_amount", label: "Amount", kind: "currency" },
      ];
  }
}
