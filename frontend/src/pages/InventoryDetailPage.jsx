import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import { EmptyState } from "../components/EmptyState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { Tabs } from "../components/Tabs";
import api from "../lib/api";
import { formatCurrency, formatDate, formatDateTime, formatNumber } from "../lib/format";

const detailTabs = {
  product: [
    { key: "overview", label: "Overview" },
    { key: "stock", label: "Stock" },
    { key: "transactions", label: "Transactions" },
    { key: "purchases", label: "Purchases" },
    { key: "audit", label: "Audit" },
  ],
  warehouse: [
    { key: "overview", label: "Overview" },
    { key: "stock", label: "Stock" },
    { key: "transactions", label: "Transactions" },
    { key: "permissions", label: "Users / Permissions" },
  ],
};

function buildMap(items) {
  return new Map(items.map((item) => [item.id, item]));
}

export function InventoryDetailPage({ kind }) {
  const params = useParams();
  const entityId = kind === "product" ? params.productId : params.warehouseId;
  const [activeTab, setActiveTab] = useState("overview");
  const [reloadKey, setReloadKey] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: "",
    record: null,
    stockRows: [],
    transactionRows: [],
    categories: [],
    brands: [],
    vendors: [],
    warehouses: [],
    products: [],
  });

  useEffect(() => {
    let active = true;

    async function load() {
      setState((current) => ({ ...current, loading: true, error: "" }));

      try {
        if (kind === "product") {
          const [
            productResponse,
            stockResponse,
            transactionResponse,
            warehousesResponse,
            categoriesResponse,
            brandsResponse,
            vendorsResponse,
          ] = await Promise.all([
            api.get(`/products/${entityId}`),
            api.get(`/products/${entityId}/stock`),
            api.get(`/products/${entityId}/transactions`, { params: { page_size: 50 } }),
            api.get("/warehouses", { params: { page_size: 200 } }),
            api.get("/categories", { params: { page_size: 200 } }),
            api.get("/brands", { params: { page_size: 200 } }),
            api.get("/vendors", { params: { page_size: 200 } }),
          ]);

          if (!active) return;

          setState({
            loading: false,
            error: "",
            record: productResponse.data,
            stockRows: (stockResponse.data.warehouses ?? []).map((row) => ({
              ...row,
              warehouse_name:
                (warehousesResponse.data.items ?? []).find((warehouse) => warehouse.id === row.warehouse_id)?.name ??
                `Warehouse #${row.warehouse_id}`,
            })),
            transactionRows: transactionResponse.data.items ?? [],
            categories: categoriesResponse.data.items ?? [],
            brands: brandsResponse.data.items ?? [],
            vendors: vendorsResponse.data.items ?? [],
            warehouses: warehousesResponse.data.items ?? [],
            products: [],
          });
          return;
        }

        const [warehouseResponse, stockResponse, transactionResponse, productsResponse] = await Promise.all([
          api.get(`/warehouses/${entityId}`),
          api.get("/reports/warehouse-stock", { params: { warehouse_id: entityId } }),
          api.get("/inventory/transactions", { params: { warehouse_id: entityId, page_size: 50 } }),
          api.get("/products", { params: { page_size: 200 } }),
        ]);

        if (!active) return;

        setState({
          loading: false,
          error: "",
          record: warehouseResponse.data,
          stockRows: stockResponse.data.rows ?? [],
          transactionRows: transactionResponse.data.items ?? [],
          categories: [],
          brands: [],
          vendors: [],
          warehouses: [],
          products: productsResponse.data.items ?? [],
        });
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load this inventory record.",
          record: null,
          stockRows: [],
          transactionRows: [],
          categories: [],
          brands: [],
          vendors: [],
          warehouses: [],
          products: [],
        });
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [entityId, kind, reloadKey]);

  const categoryMap = useMemo(() => buildMap(state.categories), [state.categories]);
  const brandMap = useMemo(() => buildMap(state.brands), [state.brands]);
  const vendorMap = useMemo(() => buildMap(state.vendors), [state.vendors]);
  const productMap = useMemo(() => buildMap(state.products), [state.products]);

  const record = state.record;
  const title = kind === "product" ? record?.name ?? "Item Detail" : record?.name ?? "Warehouse Detail";
  const statusValue = kind === "warehouse" && record?.is_default ? "PRIMARY" : record?.status;

  const metrics = useMemo(() => {
    if (!record) return [];

    if (kind === "product") {
      const totalQuantity = state.stockRows.reduce((sum, row) => sum + Number(row.quantity ?? 0), 0);
      const availableQuantity = state.stockRows.reduce((sum, row) => sum + Number(row.available_quantity ?? 0), 0);
      return [
        { label: "Stock On Hand", value: formatNumber(totalQuantity), delta: "Across all warehouses", tone: "neutral" },
        { label: "Available Stock", value: formatNumber(availableQuantity), delta: "Unreserved quantity", tone: "positive" },
        { label: "Reorder Level", value: formatNumber(record.reorder_level), delta: "Default replenishment trigger", tone: "warning" },
        { label: "Selling Price", value: formatCurrency(record.selling_price), delta: `Cost ${formatCurrency(record.cost_price)}`, tone: "info" },
      ];
    }

    const productCount = state.stockRows.length;
    const totalQuantity = state.stockRows.reduce((sum, row) => sum + Number(row.quantity ?? 0), 0);
    const availableQuantity = state.stockRows.reduce((sum, row) => sum + Number(row.available_quantity ?? 0), 0);
    return [
      { label: "Products", value: formatNumber(productCount), delta: "Distinct stocked items", tone: "neutral" },
      { label: "Quantity On Hand", value: formatNumber(totalQuantity), delta: "All units in this warehouse", tone: "info" },
      { label: "Available Quantity", value: formatNumber(availableQuantity), delta: "Ready for reservation or transfer", tone: "positive" },
      { label: "Warehouse Code", value: record.code ?? "—", delta: record.is_default ? "Primary warehouse" : "Secondary location", tone: "warning" },
    ];
  }, [kind, record, state.stockRows]);

  if (state.loading) {
    return <div className="workspace-card surface-placeholder">Loading inventory detail…</div>;
  }

  if (state.error || !record) {
    return (
      <EmptyState
        icon="alert"
        title="Unable to load this record"
        description={state.error || "Inventory record is unavailable."}
        actionLabel="Try Again"
        onAction={() => setReloadKey((current) => current + 1)}
        actionTone="ghost"
      />
    );
  }

  const overviewContent =
    kind === "product" ? (
      <div className="detail-grid">
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Primary Details</h3>
          </div>
          <div className="kv-grid">
            <div className="kv-item">
              <span>SKU</span>
              <strong>{record.sku}</strong>
            </div>
            <div className="kv-item">
              <span>Barcode</span>
              <strong>{record.barcode ?? "—"}</strong>
            </div>
            <div className="kv-item">
              <span>Category</span>
              <strong>{categoryMap.get(record.category_id)?.name ?? "Uncategorized"}</strong>
            </div>
            <div className="kv-item">
              <span>Brand</span>
              <strong>{brandMap.get(record.brand_id)?.name ?? "Unbranded"}</strong>
            </div>
            <div className="kv-item">
              <span>Preferred Vendor</span>
              <strong>{vendorMap.get(record.vendor_id)?.name ?? "—"}</strong>
            </div>
            <div className="kv-item">
              <span>Unit</span>
              <strong>{record.unit}</strong>
            </div>
          </div>
        </section>

        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Tracking Controls</h3>
          </div>
          <div className="inventory-badge-grid">
            <div className={`inventory-badge-card ${record.serial_tracking_enabled ? "is-enabled" : ""}`}>
              <span>Serial Tracking</span>
              <strong>{record.serial_tracking_enabled ? "Enabled" : "Off"}</strong>
            </div>
            <div className={`inventory-badge-card ${record.batch_tracking_enabled ? "is-enabled" : ""}`}>
              <span>Batch Tracking</span>
              <strong>{record.batch_tracking_enabled ? "Enabled" : "Off"}</strong>
            </div>
            <div className={`inventory-badge-card ${record.expiry_tracking_enabled ? "is-enabled" : ""}`}>
              <span>Expiry Tracking</span>
              <strong>{record.expiry_tracking_enabled ? "Enabled" : "Off"}</strong>
            </div>
            <div className={`inventory-badge-card ${record.warranty_tracking_enabled ? "is-enabled" : ""}`}>
              <span>Warranty Tracking</span>
              <strong>{record.warranty_tracking_enabled ? "Enabled" : "Off"}</strong>
            </div>
          </div>
          <p className="surface-note">
            {record.description || "No item description has been added yet. Use the edit screen to capture selling and purchasing notes."}
          </p>
        </section>
      </div>
    ) : (
      <div className="detail-grid">
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Location Summary</h3>
          </div>
          <div className="kv-grid">
            <div className="kv-item">
              <span>Code</span>
              <strong>{record.code}</strong>
            </div>
            <div className="kv-item">
              <span>Manager</span>
              <strong>{record.manager_name ?? "—"}</strong>
            </div>
            <div className="kv-item">
              <span>Phone</span>
              <strong>{record.phone ?? "—"}</strong>
            </div>
            <div className="kv-item">
              <span>Primary Warehouse</span>
              <strong>{record.is_default ? "Yes" : "No"}</strong>
            </div>
            <div className="kv-item field-span-full">
              <span>Address</span>
              <strong>{[record.address, record.city, record.state, record.country].filter(Boolean).join(", ") || "—"}</strong>
            </div>
          </div>
        </section>

        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Warehouse Controls</h3>
          </div>
          <div className="inventory-badge-grid">
            <div className={`inventory-badge-card ${record.status === "ACTIVE" ? "is-enabled" : ""}`}>
              <span>Status</span>
              <strong>{record.status}</strong>
            </div>
            <div className={`inventory-badge-card ${record.is_default ? "is-enabled" : ""}`}>
              <span>Primary</span>
              <strong>{record.is_default ? "Yes" : "No"}</strong>
            </div>
          </div>
          <p className="surface-note">
            Active warehouses can participate in stock transactions and transfers. Archived warehouses remain visible for historical traceability.
          </p>
        </section>
      </div>
    );

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={kind === "product" ? "Inventory Item" : "Warehouse"}
        title={title}
        description={
          kind === "product"
            ? "Product profile, stock distribution, and recent movement in one operational workspace."
            : "Warehouse summary, stocked items, and movement history for this location."
        }
        actions={
          <>
            <BackButton fallbackTo={kind === "product" ? "/items" : "/warehouses"} />
            <StatusBadge value={statusValue} />
            <Link className="button button-ghost" to={kind === "product" ? `/items/${entityId}/edit` : `/warehouses/${entityId}/edit`}>
              Edit
            </Link>
            {kind === "product" ? (
              <>
                <Link className="button button-secondary" to="/inventory/adjustment">
                  Adjust Stock
                </Link>
                <Link className="button button-primary" to="/inventory/transfers/new">
                  Transfer Stock
                </Link>
              </>
            ) : (
              <Link className="button button-primary" to="/inventory/transfers/new">
                Transfer Stock
              </Link>
            )}
          </>
        }
      />

      <div className="metric-grid">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} delta={metric.delta} tone={metric.tone} />
        ))}
      </div>

      <Tabs items={detailTabs[kind]} activeKey={activeTab} onChange={setActiveTab} />

      {activeTab === "overview" ? overviewContent : null}

      {activeTab === "stock" ? (
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>{kind === "product" ? "Warehouse Stock Breakdown" : "Stock By Item"}</h3>
          </div>
          {state.stockRows.length ? (
            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    {kind === "product" ? (
                      <>
                        <th>Warehouse</th>
                        <th>Quantity</th>
                        <th>Reserved</th>
                        <th>Available</th>
                        <th>Reorder Level</th>
                      </>
                    ) : (
                      <>
                        <th>Item</th>
                        <th>SKU</th>
                        <th>Quantity</th>
                        <th>Reserved</th>
                        <th>Available</th>
                      </>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {state.stockRows.map((row, index) => (
                    <tr key={`${row.warehouse_id ?? row.product_id}-${index}`}>
                      {kind === "product" ? (
                        <>
                          <td>{row.warehouse_name}</td>
                          <td>{formatNumber(row.quantity)}</td>
                          <td>{formatNumber(row.reserved_quantity)}</td>
                          <td>{formatNumber(row.available_quantity)}</td>
                          <td>{formatNumber(row.reorder_level)}</td>
                        </>
                      ) : (
                        <>
                          <td>{row.product_name ?? productMap.get(row.product_id)?.name ?? `Item #${row.product_id}`}</td>
                          <td>{row.sku ?? productMap.get(row.product_id)?.sku ?? "—"}</td>
                          <td>{formatNumber(row.quantity)}</td>
                          <td>{formatNumber(row.reserved_quantity)}</td>
                          <td>{formatNumber(row.available_quantity)}</td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState
              icon={kind === "product" ? "box" : "warehouse"}
              title={kind === "product" ? "No stock footprint yet" : "No stock recorded yet"}
              description={
                kind === "product"
                  ? "This item has not been stocked into any warehouse yet."
                  : "No item quantities have been recorded for this warehouse yet."
              }
            />
          )}
        </section>
      ) : null}

      {activeTab === "transactions" ? (
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Recent Transactions</h3>
          </div>
          {state.transactionRows.length ? (
            <div className="mini-list">
              {state.transactionRows.map((row) => (
                <div className="mini-list-row" key={row.id}>
                  <div>
                    <strong>{row.transaction_type.replaceAll("_", " ")}</strong>
                    <span>
                      {kind === "product"
                        ? `Warehouse #${row.warehouse_id}`
                        : productMap.get(row.product_id)?.name ?? `Item #${row.product_id}`}
                    </span>
                  </div>
                  <div className="metric-pair">
                    <strong>{formatNumber(row.quantity)}</strong>
                    <span>{formatDateTime(row.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon="activity"
              title="No recent transactions"
              description="Inventory movement will appear here as soon as stock starts moving through this record."
            />
          )}
        </section>
      ) : null}

      {activeTab === "purchases" && kind === "product" ? (
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Purchasing Context</h3>
          </div>
          <div className="kv-grid">
            <div className="kv-item">
              <span>Preferred Vendor</span>
              <strong>{vendorMap.get(record.vendor_id)?.name ?? "Not assigned"}</strong>
            </div>
            <div className="kv-item">
              <span>Cost Price</span>
              <strong>{formatCurrency(record.cost_price)}</strong>
            </div>
            <div className="kv-item">
              <span>Selling Price</span>
              <strong>{formatCurrency(record.selling_price)}</strong>
            </div>
            <div className="kv-item">
              <span>Last Updated</span>
              <strong>{formatDateTime(record.updated_at)}</strong>
            </div>
          </div>
          <p className="surface-note">
            This section anchors purchasing context for the item. Deeper purchase-linked activity can continue to expand here without redesigning the inventory detail shell.
          </p>
        </section>
      ) : null}

      {activeTab === "audit" && kind === "product" ? (
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Audit Snapshot</h3>
          </div>
          {state.transactionRows.length ? (
            <div className="mini-list">
              {state.transactionRows.slice(0, 8).map((row) => (
                <div className="mini-list-row" key={row.id}>
                  <div>
                    <strong>{row.transaction_type.replaceAll("_", " ")}</strong>
                    <span>{row.reference_type ? `${row.reference_type} #${row.reference_id ?? "—"}` : "Manual entry"}</span>
                  </div>
                  <div className="metric-pair">
                    <strong>{formatDate(row.created_at)}</strong>
                    <span>User #{row.created_by}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon="shield" title="No audit trace yet" description="Audit and movement history will accumulate here as the item is transacted." />
          )}
        </section>
      ) : null}

      {activeTab === "permissions" && kind === "warehouse" ? (
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Warehouse Permissions</h3>
          </div>
          <p className="surface-note">
            Warehouse-specific user permissions are not yet modeled as a first-class backend feature, but this tab is reserved for warehouse operators, access rules, and transfer controls.
          </p>
        </section>
      ) : null}
    </div>
  );
}
