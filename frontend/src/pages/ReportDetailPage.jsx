import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import api from "../lib/api";
import { DashboardWidget } from "../components/DashboardWidget";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { formatLabel } from "../lib/format";

export function ReportDetailPage() {
  const { reportKey } = useParams();
  const [rows, setRows] = useState([]);
  const [filters, setFilters] = useState({
    period: "This Month",
    warehouse: "All Warehouses",
    product: "All Products",
  });

  useEffect(() => {
    api.get(`/app/reports/${reportKey}`).then(({ data }) => setRows(data.rows ?? []));
  }, [reportKey]);

  const columns = useMemo(() => (rows.length ? Object.keys(rows[0]) : []), [rows]);

  if (!reportKey) {
    return (
      <EmptyState
        icon="chart"
        title="Report not found"
        description="This report definition is not available."
        actionLabel="Back to reports"
        actionTo="/reports"
      />
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Report Detail"
        title={formatLabel(reportKey)}
        description="Report rows are loaded from the backend and filtered visually from this workspace."
        actions={
          <div className="header-inline-chips">
            <button className="button button-primary" type="button">Run Report</button>
            <button className="button button-secondary" type="button">Export CSV</button>
            <button className="button button-ghost" type="button" onClick={() => window.print()}>
              Print / PDF
            </button>
          </div>
        }
      />

      <DashboardWidget title="Filters">
        <div className="report-filter-grid">
          <label>
            Date Range
            <select value={filters.period} onChange={(event) => setFilters((state) => ({ ...state, period: event.target.value }))}>
              <option>This Month</option>
              <option>This Quarter</option>
              <option>This Year</option>
              <option>Previous Month</option>
            </select>
          </label>
          <label>
            Warehouse
            <select value={filters.warehouse} onChange={(event) => setFilters((state) => ({ ...state, warehouse: event.target.value }))}>
              <option>All Warehouses</option>
              <option>Central Warehouse</option>
              <option>North Hub</option>
            </select>
          </label>
          <label>
            Product / Category
            <select value={filters.product} onChange={(event) => setFilters((state) => ({ ...state, product: event.target.value }))}>
              <option>All Products</option>
              <option>Sheesham Study Table</option>
              <option>Ergonomic Mesh Kursi</option>
            </select>
          </label>
          <label>
            Configure Columns
            <select defaultValue="standard">
              <option value="standard">Standard Layout</option>
              <option value="compact">Compact Layout</option>
            </select>
          </label>
        </div>
      </DashboardWidget>

      <DashboardWidget title="Report Output">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{formatLabel(column)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={row.id ?? row.metric ?? row.order ?? rowIndex}>
                  {columns.map((column) => (
                    <td key={column}>{row[column]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DashboardWidget>
    </div>
  );
}
