import { useEffect, useMemo, useState } from "react";

import { DataTable } from "../components/DataTable";
import { BackButton } from "../components/BackButton";
import { PageHeader } from "../components/PageHeader";
import api from "../lib/api";

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

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Inventory Signal"
        title="Low Stock"
        description="Review products below reorder level and jump straight into replenishment or stock corrections."
        actions={<BackButton fallbackTo="/reports?report=low-stock" />}
      />

      <DataTable
        title="Low Stock Queue"
        description="Warehouse-level reorder exceptions pulled from the live inventory service."
        rows={state.items}
        columns={[
          { key: "product_name", label: "Item" },
          { key: "sku", label: "SKU" },
          { key: "warehouse_name", label: "Warehouse" },
          { key: "available_quantity", label: "Available" },
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
