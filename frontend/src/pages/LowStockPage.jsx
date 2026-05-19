import { useEffect, useMemo, useState } from "react";

import { DataTable } from "../components/DataTable";
import { BackButton } from "../components/BackButton";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import api from "../lib/api";
import { formatNumber } from "../lib/format";

export function LowStockPage() {
  const [reloadKey, setReloadKey] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: "",
    items: [],
  });

  useEffect(() => {
    let active = true;

    api
      .get("/inventory/low-stock", { params: { page_size: 100 } })
      .then(({ data }) => {
        if (!active) return;
        const rows = (data.items ?? []).map((item) => ({
          ...item,
          id: `${item.product_id}-${item.warehouse_id}`,
        }));
        setState({ loading: false, error: "", items: rows });
      })
      .catch((error) => {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load low-stock items.",
          items: [],
        });
      });

    return () => {
      active = false;
    };
  }, [reloadKey]);

  const sourceNote = useMemo(() => {
    if (!state.items.length) return "No low-stock alerts are active for the current tenant.";
    return `${state.items.length} warehouse item position${state.items.length === 1 ? "" : "s"} currently need replenishment attention.`;
  }, [state.items]);
  const warehouseCount = useMemo(() => new Set(state.items.map((item) => item.warehouse_id)).size, [state.items]);
  const productCount = useMemo(() => new Set(state.items.map((item) => item.product_id)).size, [state.items]);
  const mostCritical = useMemo(() => {
    if (!state.items.length) return null;
    return [...state.items].sort((left, right) => left.available_quantity - right.available_quantity)[0];
  }, [state.items]);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Inventory Signal"
        title="Low Stock"
        description="Review products below reorder level and jump straight into replenishment or stock corrections."
        actions={<BackButton fallbackTo="/reports?report=low-stock" />}
      />

      <div className="metric-grid">
        <MetricCard label="Alert Rows" value={formatNumber(state.items.length)} delta="Warehouse-product exceptions" tone="warning" />
        <MetricCard label="Affected Items" value={formatNumber(productCount)} delta="Distinct products below threshold" tone="neutral" />
        <MetricCard label="Affected Warehouses" value={formatNumber(warehouseCount)} delta="Locations needing replenishment" tone="info" />
        <MetricCard
          label="Most Critical"
          value={mostCritical ? formatNumber(mostCritical.available_quantity) : "—"}
          delta={mostCritical ? `${mostCritical.product_name} at ${mostCritical.warehouse_name}` : "No active shortage"}
          tone="warning"
        />
      </div>

      <DataTable
        title="Low Stock Queue"
        description="Warehouse-level reorder exceptions pulled from the live inventory service."
        rows={state.items}
        columns={[
          { key: "product_name", label: "Item" },
          { key: "sku", label: "SKU" },
          { key: "warehouse_name", label: "Warehouse" },
          {
            key: "available_quantity",
            label: "Available",
            render: (value) => <span className="inventory-quantity inventory-quantity-negative">{formatNumber(value)}</span>,
          },
          { key: "reorder_level", label: "Reorder Level" },
        ]}
        filters={[{ label: "All Low Stock Items", value: "all" }]}
        createLabel="Record Stock In"
        createTo="/inventory/stock-in"
        searchPlaceholder="Search item name, SKU, or warehouse"
        rowLink={(_, row) => `/items/${row.product_id}`}
        isLoading={state.loading}
        error={state.error}
        onRetry={() => setReloadKey((value) => value + 1)}
        sourceNote={sourceNote}
        emptyState={{
          icon: "alert",
          title: "No low stock items",
          description: "Current stock posture is healthy. This page will surface items automatically when they fall below reorder level.",
          actionLabel: "Review Inventory Reports",
          actionTo: "/reports?report=inventory-summary",
        }}
      />
    </div>
  );
}
