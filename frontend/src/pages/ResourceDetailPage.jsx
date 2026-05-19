import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import api from "../lib/api";
import { formatCurrency, formatDate, formatDateTime } from "../lib/format";
import { StatusBadge } from "../components/StatusBadge";

const detailConfigs = {
  product: {
    title: "Item Detail",
    endpoint: (id) => `/products/${id}`,
    editPath: (id) => `/items/${id}/edit`,
    supplementary: (id) => [
      { key: "stock", endpoint: `/products/${id}/stock` },
      { key: "transactions", endpoint: `/products/${id}/transactions` },
    ],
  },
  warehouse: {
    title: "Warehouse Detail",
    endpoint: (id) => `/warehouses/${id}`,
  },
  vendor: {
    title: "Vendor Detail",
    endpoint: (id) => `/vendors/${id}`,
    editPath: (id) => `/vendors/${id}/edit`,
  },
  customer: {
    title: "Customer Detail",
    endpoint: (id) => `/customers/${id}`,
    editPath: (id) => `/customers/${id}/edit`,
  },
  stockTransfer: {
    title: "Stock Transfer Detail",
    endpoint: (id) => `/inventory/transfers/${id}`,
  },
  purchaseOrder: {
    title: "Purchase Order Detail",
    endpoint: (id) => `/purchase-orders/${id}`,
    editPath: (id) => `/purchase-orders/${id}/edit`,
  },
  salesOrder: {
    title: "Sales Order Detail",
    endpoint: (id) => `/sales-orders/${id}`,
    editPath: (id) => `/sales-orders/${id}/edit`,
  },
};

function keyValueEntries(record) {
  return Object.entries(record ?? {}).filter(([key, value]) => !Array.isArray(value) && typeof value !== "object" && key !== "id");
}

function formatValue(key, value) {
  if (key.includes("amount") || key.includes("price")) return formatCurrency(value);
  if (key.includes("date") || key.endsWith("_at")) return key.endsWith("_at") ? formatDateTime(value) : formatDate(value);
  if (key === "status") return <StatusBadge value={value} />;
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return value ?? "—";
}

export function ResourceDetailPage({ detailKey, paramKey }) {
  const { [paramKey]: entityId } = useParams();
  const config = detailConfigs[detailKey];
  const [state, setState] = useState({
    loading: true,
    error: "",
    record: null,
    supplementary: {},
  });

  useEffect(() => {
    let active = true;

    async function load() {
      setState({ loading: true, error: "", record: null, supplementary: {} });
      try {
        const primaryResponse = await api.get(config.endpoint(entityId));
        const extraEntries = {};
        if (config.supplementary) {
          const results = await Promise.all(
            config.supplementary(entityId).map(async (entry) => {
              const response = await api.get(entry.endpoint);
              return [entry.key, response.data];
            }),
          );
          results.forEach(([key, value]) => {
            extraEntries[key] = value;
          });
        }

        if (!active) return;
        setState({
          loading: false,
          error: "",
          record: primaryResponse.data,
          supplementary: extraEntries,
        });
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load record details.",
          record: null,
          supplementary: {},
        });
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [config, entityId]);

  const entries = useMemo(() => keyValueEntries(state.record), [state.record]);
  const itemRows = state.record?.items ?? [];
  const stockRows = state.supplementary.stock?.warehouses ?? [];
  const transactionRows = state.supplementary.transactions?.items ?? [];

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Workspace Detail</p>
          <h2>{config.title}</h2>
          <p>Key record details, line items, and related operational activity.</p>
        </div>
        <div className="page-header-actions">
          <BackButton fallbackTo="/" />
          {config.editPath ? (
            <Link className="ghost-button" to={config.editPath(entityId)}>
              Edit
            </Link>
          ) : null}
        </div>
      </section>

      {state.loading ? <div className="workspace-card surface-placeholder">Loading detail…</div> : null}
      {!state.loading && state.error ? <div className="workspace-card surface-error">{state.error}</div> : null}

      {!state.loading && state.record ? (
        <>
          <section className="detail-grid">
            <article className="workspace-card">
              <div className="card-header-row">
                <h3>Summary</h3>
              </div>
              <div className="kv-grid">
                {entries.map(([key, value]) => (
                  <div className="kv-item" key={key}>
                    <span>{key.replaceAll("_", " ")}</span>
                    <strong>{formatValue(key, value)}</strong>
                  </div>
                ))}
              </div>
            </article>

            {stockRows.length > 0 ? (
              <article className="workspace-card">
                <div className="card-header-row">
                  <h3>Stock Footprint</h3>
                </div>
                <div className="mini-list">
                  {stockRows.map((item) => (
                    <div className="mini-list-row" key={item.warehouse_id}>
                      <div>
                        <strong>Warehouse #{item.warehouse_id}</strong>
                        <span>Available {item.available_quantity}</span>
                      </div>
                      <StatusBadge value={item.available_quantity <= item.reorder_level ? "LOW_STOCK" : "ACTIVE"} />
                    </div>
                  ))}
                </div>
              </article>
            ) : null}
          </section>

          {itemRows.length > 0 ? (
            <section className="workspace-card">
              <div className="card-header-row">
                <h3>Line Items</h3>
              </div>
              <div className="data-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      {Object.keys(itemRows[0]).map((key) => (
                        <th key={key}>{key.replaceAll("_", " ")}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {itemRows.map((row) => (
                      <tr key={row.id}>
                        {Object.entries(row).map(([key, value]) => (
                          <td key={key}>{formatValue(key, value)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}

          {transactionRows.length > 0 ? (
            <section className="workspace-card">
              <div className="card-header-row">
                <h3>Recent Movement</h3>
              </div>
              <div className="mini-list">
                {transactionRows.slice(0, 6).map((row) => (
                  <div className="mini-list-row" key={row.id}>
                    <div>
                      <strong>{row.transaction_type.replaceAll("_", " ")}</strong>
                      <span>{formatDateTime(row.created_at)}</span>
                    </div>
                    <span>{row.quantity}</span>
                  </div>
                ))}
              </div>
            </section>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
