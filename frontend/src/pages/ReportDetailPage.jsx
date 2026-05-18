import { useParams } from "react-router-dom";

import { DashboardWidget } from "../components/DashboardWidget";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { getReportRows, reportGroups } from "../lib/demoData";

export function ReportDetailPage() {
  const { reportKey } = useParams();
  const report = reportGroups.flatMap((group) => group.reports).find((item) => item.key === reportKey);
  const rows = getReportRows(reportKey);

  if (!report) {
    return (
      <EmptyState
        icon="chart"
        title="Report not found"
        description="This report definition is not available in the current UI catalog."
        actionLabel="Back to reports"
        actionTo="/reports"
      />
    );
  }

  const columns = rows.length ? Object.keys(rows[0]) : [];

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Report Detail"
        title={report.title}
        description={report.description}
        actions={
          <div className="header-inline-chips">
            <button className="button button-primary" type="button">Run Report</button>
            <button className="button button-secondary" type="button">Export CSV</button>
            <button className="button button-ghost" type="button">Print / PDF</button>
          </div>
        }
      />

      <DashboardWidget title="Filters">
        <div className="report-filter-grid">
          <label>
            Date Range
            <select defaultValue="this-month">
              <option value="this-month">This Month</option>
              <option value="this-year">This Year</option>
              <option value="previous-month">Previous Month</option>
            </select>
          </label>
          <label>
            Warehouse
            <select defaultValue="all">
              <option value="all">All Warehouses</option>
              <option value="central">Central Warehouse</option>
              <option value="north">North Hub</option>
            </select>
          </label>
          <label>
            Product / Category
            <input defaultValue="All products" />
          </label>
          <label>
            Configure Columns
            <input value="Placeholder control" readOnly />
          </label>
        </div>
      </DashboardWidget>

      <DashboardWidget title="Report Output">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column.replaceAll(/([A-Z])/g, " $1")}</th>
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
