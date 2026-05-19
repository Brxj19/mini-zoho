import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import { DataTable } from "../components/DataTable";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import api from "../lib/api";
import { formatCurrency, formatNumber } from "../lib/format";

const periodOptions = [
  { label: "This Month", value: "this_month" },
  { label: "Previous Month", value: "previous_month" },
  { label: "This Year", value: "this_year" },
];

const pageConfigs = {
  packages: {
    title: "Packages",
    eyebrow: "Sales Workflow",
    description: "Use confirmed and packed sales orders as your packaging queue until a dedicated package entity is introduced.",
    domain: "sales",
    sourceStatuses: ["CONFIRMED", "PACKED", "SHIPPED"],
    filters: [
      { label: "All Package Queue", value: "all" },
      { label: "To Be Packed", value: "CONFIRMED" },
      { label: "Packed", value: "PACKED" },
      { label: "Shipped", value: "SHIPPED" },
    ],
    columns: [
      { key: "document_number", label: "Sales Order" },
      { key: "partner_name", label: "Customer" },
      { key: "item_count", label: "Items" },
      { key: "order_date", label: "Order Date", kind: "date" },
      { key: "total_amount", label: "Amount", kind: "currency" },
      { key: "status", label: "Status", kind: "status" },
    ],
    metrics(rows) {
      return [
        { label: "To Be Packed", value: rows.filter((row) => row.status === "CONFIRMED").length, delta: "Ready for packaging", tone: "warning" },
        { label: "Packed", value: rows.filter((row) => row.status === "PACKED").length, delta: "Awaiting shipment", tone: "info" },
        { label: "Shipped", value: rows.filter((row) => row.status === "SHIPPED").length, delta: "Already dispatched", tone: "positive" },
        { label: "Queue Value", value: formatCurrency(rows.reduce((sum, row) => sum + Number(row.total_amount ?? 0), 0)), delta: "Order value in motion", tone: "neutral" },
      ];
    },
    detailPath: (id) => `/sales-orders/${id}`,
    sourcePath: "/sales-orders",
  },
  invoices: {
    title: "Invoices",
    eyebrow: "Sales Workflow",
    description: "Track invoice-ready sales orders from shipped and delivered records while the dedicated invoice ledger is still pending.",
    domain: "sales",
    sourceStatuses: ["SHIPPED", "DELIVERED"],
    filters: [
      { label: "All Invoice Candidates", value: "all" },
      { label: "Shipped", value: "SHIPPED" },
      { label: "Delivered", value: "DELIVERED" },
    ],
    columns: [
      { key: "document_number", label: "Sales Order" },
      { key: "partner_name", label: "Customer" },
      { key: "order_date", label: "Order Date", kind: "date" },
      { key: "total_amount", label: "Invoice Value", kind: "currency" },
      { key: "status", label: "Order Status", kind: "status" },
    ],
    metrics(rows) {
      return [
        { label: "Invoice Ready", value: rows.length, delta: "Real orders available to bill", tone: "info" },
        { label: "Delivered Orders", value: rows.filter((row) => row.status === "DELIVERED").length, delta: "Closed fulfillment", tone: "positive" },
        { label: "Shipped Orders", value: rows.filter((row) => row.status === "SHIPPED").length, delta: "Likely near-billing", tone: "warning" },
        { label: "Billable Value", value: formatCurrency(rows.reduce((sum, row) => sum + Number(row.total_amount ?? 0), 0)), delta: "Potential invoice total", tone: "neutral" },
      ];
    },
    detailPath: (id) => `/sales-orders/${id}`,
    sourcePath: "/sales-orders",
  },
  "sales-returns": {
    title: "Sales Returns",
    eyebrow: "Sales Workflow",
    description: "Review delivered orders that are eligible for return handling while formal return records are still on the roadmap.",
    domain: "sales",
    sourceStatuses: ["DELIVERED", "CANCELLED"],
    filters: [
      { label: "All Return Context", value: "all" },
      { label: "Delivered", value: "DELIVERED" },
      { label: "Cancelled", value: "CANCELLED" },
    ],
    columns: [
      { key: "document_number", label: "Sales Order" },
      { key: "partner_name", label: "Customer" },
      { key: "item_count", label: "Items" },
      { key: "order_date", label: "Order Date", kind: "date" },
      { key: "total_amount", label: "Order Value", kind: "currency" },
      { key: "status", label: "Status", kind: "status" },
    ],
    metrics(rows) {
      const delivered = rows.filter((row) => row.status === "DELIVERED");
      return [
        { label: "Return Eligible", value: delivered.length, delta: "Delivered orders", tone: "warning" },
        { label: "Delivered Value", value: formatCurrency(delivered.reduce((sum, row) => sum + Number(row.total_amount ?? 0), 0)), delta: "Value exposed to returns", tone: "neutral" },
        { label: "Cancelled Orders", value: rows.filter((row) => row.status === "CANCELLED").length, delta: "Not returnable, but relevant context", tone: "danger" },
        { label: "Orders Reviewed", value: rows.length, delta: "Operational context", tone: "info" },
      ];
    },
    detailPath: (id) => `/sales-orders/${id}`,
    sourcePath: "/sales-orders",
  },
  "purchase-receives": {
    title: "Purchase Receives",
    eyebrow: "Purchases Workflow",
    description: "Work through inbound receiving from issued and partially received purchase orders using the real receiving-capable PO flow.",
    domain: "purchase",
    sourceStatuses: ["ISSUED", "PARTIALLY_RECEIVED", "RECEIVED"],
    filters: [
      { label: "All Receive Queue", value: "all" },
      { label: "Issued", value: "ISSUED" },
      { label: "Partially Received", value: "PARTIALLY_RECEIVED" },
      { label: "Received", value: "RECEIVED" },
    ],
    columns: [
      { key: "document_number", label: "Purchase Order" },
      { key: "partner_name", label: "Vendor" },
      { key: "item_count", label: "Items" },
      { key: "order_date", label: "Order Date", kind: "date" },
      { key: "total_amount", label: "Amount", kind: "currency" },
      { key: "status", label: "Status", kind: "status" },
    ],
    metrics(rows) {
      return [
        { label: "To Be Received", value: rows.filter((row) => row.status === "ISSUED").length, delta: "Waiting on inbound stock", tone: "warning" },
        { label: "Receiving In Progress", value: rows.filter((row) => row.status === "PARTIALLY_RECEIVED").length, delta: "Partial receipts logged", tone: "info" },
        { label: "Received", value: rows.filter((row) => row.status === "RECEIVED").length, delta: "Inbound closed", tone: "positive" },
        { label: "Inbound Value", value: formatCurrency(rows.reduce((sum, row) => sum + Number(row.total_amount ?? 0), 0)), delta: "Tracked purchase value", tone: "neutral" },
      ];
    },
    detailPath: (id) => `/purchase-orders/${id}`,
    sourcePath: "/purchase-orders",
  },
  bills: {
    title: "Bills",
    eyebrow: "Purchases Workflow",
    description: "Use received purchase orders as the billable queue until dedicated AP bill records are introduced.",
    domain: "purchase",
    sourceStatuses: ["PARTIALLY_RECEIVED", "RECEIVED"],
    filters: [
      { label: "All Bill Candidates", value: "all" },
      { label: "Partially Received", value: "PARTIALLY_RECEIVED" },
      { label: "Received", value: "RECEIVED" },
    ],
    columns: [
      { key: "document_number", label: "Purchase Order" },
      { key: "partner_name", label: "Vendor" },
      { key: "order_date", label: "Order Date", kind: "date" },
      { key: "total_amount", label: "Payable Value", kind: "currency" },
      { key: "status", label: "Receive Status", kind: "status" },
    ],
    metrics(rows) {
      return [
        { label: "Bill Candidates", value: rows.length, delta: "Real purchase orders to reconcile", tone: "info" },
        { label: "Fully Received", value: rows.filter((row) => row.status === "RECEIVED").length, delta: "Ready for final billing", tone: "positive" },
        { label: "Partial Receipts", value: rows.filter((row) => row.status === "PARTIALLY_RECEIVED").length, delta: "Match against vendor bills", tone: "warning" },
        { label: "Payables Value", value: formatCurrency(rows.reduce((sum, row) => sum + Number(row.total_amount ?? 0), 0)), delta: "Potential AP exposure", tone: "neutral" },
      ];
    },
    detailPath: (id) => `/purchase-orders/${id}`,
    sourcePath: "/purchase-orders",
  },
};

function isWithinPeriod(dateValue, period) {
  if (!dateValue) return true;
  const target = new Date(dateValue);
  if (Number.isNaN(target.getTime())) return true;
  const now = new Date();

  if (period === "this_month") {
    return target.getFullYear() === now.getFullYear() && target.getMonth() === now.getMonth();
  }

  if (period === "previous_month") {
    const previousMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    return target.getFullYear() === previousMonth.getFullYear() && target.getMonth() === previousMonth.getMonth();
  }

  if (period === "this_year") {
    return target.getFullYear() === now.getFullYear();
  }

  return true;
}

function toDomainRow(record, partnerName, domain) {
  const documentNumber = domain === "sales" ? record.so_number : record.po_number;
  return {
    id: record.id,
    document_number: documentNumber,
    partner_name: partnerName,
    order_date: record.order_date,
    total_amount: record.total_amount,
    status: record.status,
    item_count: record.items?.length ?? 0,
    notes: record.notes,
  };
}

export function WorkflowWorkbenchPage({ pageKey }) {
  const config = pageConfigs[pageKey];
  const [period, setPeriod] = useState("this_month");
  const [state, setState] = useState({ loading: true, error: "", rows: [] });

  useEffect(() => {
    let active = true;

    async function load() {
      setState({ loading: true, error: "", rows: [] });
      try {
        const [recordsResponse, partnersResponse] = await Promise.all([
          api.get(config.domain === "sales" ? "/sales-orders" : "/purchase-orders", { params: { page_size: 100 } }),
          api.get(config.domain === "sales" ? "/customers" : "/vendors", { params: { page_size: 100 } }),
        ]);
        if (!active) return;

        const partnerLookup = new Map(
          (partnersResponse.data.items ?? []).map((item) => [item.id, item.name]),
        );

        const rows = (recordsResponse.data.items ?? [])
          .filter((record) => config.sourceStatuses.includes(record.status))
          .map((record) =>
            toDomainRow(
              record,
              partnerLookup.get(config.domain === "sales" ? record.customer_id : record.vendor_id) ?? "—",
              config.domain,
            ),
          );

        setState({ loading: false, error: "", rows });
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load this workflow surface.",
          rows: [],
        });
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [config]);

  const visibleRows = useMemo(
    () => state.rows.filter((row) => isWithinPeriod(row.order_date, period)),
    [period, state.rows],
  );
  const metrics = config.metrics(visibleRows);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={config.eyebrow}
        title={config.title}
        description={config.description}
        actions={
          <>
            <BackButton fallbackTo={config.sourcePath} />
            <select className="field-input compact-field" value={period} onChange={(event) => setPeriod(event.target.value)}>
              {periodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </>
        }
      />

      <div className="metric-grid">
        {metrics.map((metric) => (
          <MetricCard
            key={metric.label}
            label={metric.label}
            value={typeof metric.value === "number" ? formatNumber(metric.value) : metric.value}
            delta={metric.delta}
            tone={metric.tone}
          />
        ))}
      </div>

      <DataTable
        title={`${config.title} Queue`}
        description="Built from real backend records already available in this workspace."
        rows={visibleRows}
        columns={config.columns}
        filters={config.filters}
        searchPlaceholder={`Search ${config.title.toLowerCase()} by order number or partner`}
        rowLink={config.detailPath}
        isLoading={state.loading}
        emptyState={{
          icon: config.domain === "sales" ? "cart" : "clipboard",
          title: `No ${config.title.toLowerCase()} records in this period`,
          description: "Adjust the date filter or create more operational records to populate this workbench.",
          actionLabel: `Open ${config.domain === "sales" ? "Sales Orders" : "Purchase Orders"}`,
          actionTo: config.sourcePath,
        }}
      />

      {!state.loading && !state.error ? (
        <div className="detail-grid">
          <section className="workspace-card">
            <div className="card-header-row">
              <h3>Operational Note</h3>
            </div>
            <p>
              This screen uses existing order records so your team can work from a real queue now. When dedicated
              {` ${config.title.toLowerCase()} `}
              entities are added later, this layout can evolve without another redesign.
            </p>
          </section>
          <section className="workspace-card">
            <div className="card-header-row">
              <h3>Next Step</h3>
            </div>
            <Link className="button button-primary" to={config.sourcePath}>
              Open Source Orders
            </Link>
          </section>
        </div>
      ) : null}
    </div>
  );
}
