import { useDeferredValue, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../lib/api";
import { formatCurrency, formatDateTime, normalizeItems } from "../lib/format";
import { resourceConfigs } from "../lib/uiConfig";
import { StatusBadge } from "../components/StatusBadge";

function renderValue(column, value) {
  if (column.kind === "status") {
    return <StatusBadge value={value} />;
  }
  if (column.kind === "boolean") {
    return value ? "Yes" : "No";
  }
  if (column.kind === "date") {
    return formatDateTime(value);
  }
  if (column.key.includes("amount") || column.key.includes("price")) {
    return formatCurrency(value);
  }
  return value ?? "—";
}

export function ResourceListPage({ resourceKey }) {
  const config = resourceConfigs[resourceKey];
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const deferredQuery = useDeferredValue(query);
  const [state, setState] = useState({
    loading: true,
    error: "",
    items: [],
  });

  useEffect(() => {
    let active = true;
    setState((current) => ({ ...current, loading: true, error: "" }));

    api
      .get(config.endpoint, {
        params: {
          search: deferredQuery || undefined,
          status: statusFilter || undefined,
          page_size: 50,
        },
      })
      .then((response) => {
        if (!active) return;
        setState({
          loading: false,
          error: "",
          items: normalizeItems(response.data),
        });
      })
      .catch((error) => {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load this workspace view.",
          items: [],
        });
      });

    return () => {
      active = false;
    };
  }, [config.endpoint, deferredQuery, statusFilter]);

  const rows = useMemo(() => state.items, [state.items]);

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Operations</p>
          <h2>{config.title}</h2>
          <p>{config.description}</p>
        </div>
        {config.createPath ? (
          <Link className="primary-button" to={config.createPath}>
            Create
          </Link>
        ) : null}
      </section>

      <section className="workspace-card">
        <div className="toolbar-row">
          <input
            className="shell-search shell-search-light"
            placeholder={config.searchPlaceholder}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <select className="field-input compact-field" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="">All statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="DRAFT">Draft</option>
            <option value="CONFIRMED">Confirmed</option>
            <option value="RECEIVED">Received</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>

        {state.loading ? <div className="surface-placeholder">Loading {config.title.toLowerCase()}…</div> : null}
        {!state.loading && state.error ? <div className="surface-error">{state.error}</div> : null}
        {!state.loading && !state.error && rows.length === 0 ? (
          <div className="surface-empty">
            <h3>No records yet</h3>
            <p>This module is ready for live data. Add a record or adjust your filters.</p>
          </div>
        ) : null}

        {!state.loading && !state.error && rows.length > 0 ? (
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  {config.columns.map((column) => (
                    <th key={column.key}>{column.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.id}
                    className={config.detailPath ? "data-row-clickable" : ""}
                    onClick={() => {
                      if (config.detailPath) {
                        navigate(config.detailPath(row.id));
                      }
                    }}
                  >
                    {config.columns.map((column) => (
                      <td key={column.key}>{renderValue(column, row[column.key])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </div>
  );
}
