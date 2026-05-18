import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import api from "../lib/api";
import { formatCurrency, formatDateTime } from "../lib/format";
import { reportCatalog } from "../lib/uiConfig";

function renderCell(key, value) {
  if (key.includes("amount") || key.includes("value")) return formatCurrency(value);
  if (key.includes("date") || key.includes("_at")) return formatDateTime(value);
  return value ?? "—";
}

export function ReportsPage() {
  const [params, setParams] = useSearchParams();
  const [state, setState] = useState({ loading: true, error: "", data: null });
  const reportKey = params.get("report") ?? "inventory-summary";
  const activeReport = reportCatalog.find((report) => report.key === reportKey) ?? reportCatalog[0];

  useEffect(() => {
    let active = true;
    setState({ loading: true, error: "", data: null });
    api
      .get(activeReport.endpoint)
      .then((response) => {
        if (!active) return;
        setState({ loading: false, error: "", data: response.data });
      })
      .catch((error) => {
        if (!active) return;
        setState({ loading: false, error: error?.response?.data?.detail ?? "Unable to load this report.", data: null });
      });
    return () => {
      active = false;
    };
  }, [activeReport.endpoint]);

  const rows = useMemo(() => state.data?.rows ?? [], [state.data]);

  async function exportCsv() {
    const response = await api.get(activeReport.endpoint, { params: { export: "csv" }, responseType: "blob" });
    const url = window.URL.createObjectURL(response.data);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${activeReport.key}.csv`;
    anchor.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Reporting</p>
          <h2>Operations Reports</h2>
          <p>A light, fast reporting hub for inventory, order flow, and warehouse oversight.</p>
        </div>
        <button className="ghost-button" type="button" onClick={exportCsv}>
          Export CSV
        </button>
      </section>

      <section className="workspace-card">
        <div className="report-pill-row">
          {reportCatalog.map((report) => (
            <button
              key={report.key}
              className={`report-pill ${report.key === activeReport.key ? "report-pill-active" : ""}`}
              type="button"
              onClick={() => setParams({ report: report.key })}
            >
              {report.label}
            </button>
          ))}
        </div>

        {state.loading ? <div className="surface-placeholder">Loading report…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}
        {!state.loading && !state.error && rows.length === 0 ? (
          <div className="surface-empty">
            <h3>No rows returned</h3>
            <p>This report is ready, but your current tenant data does not yet populate it.</p>
          </div>
        ) : null}
        {!state.loading && !state.error && rows.length > 0 ? (
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  {Object.keys(rows[0]).map((key) => (
                    <th key={key}>{key.replaceAll("_", " ")}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.slice(0, 50).map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {Object.entries(row).map(([key, value]) => (
                      <td key={key}>{renderCell(key, value)}</td>
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
