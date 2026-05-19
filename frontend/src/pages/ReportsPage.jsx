import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import api from "../lib/api";
import { PageHeader } from "../components/PageHeader";
import { formatCurrency, formatDate, formatDateTime } from "../lib/format";
import { reportCatalog } from "../lib/uiConfig";

const defaultFilters = {
  date_from: "",
  date_to: "",
  warehouse_id: "",
  product_id: "",
  category_id: "",
  status: "",
  vendor_id: "",
  customer_id: "",
  action: "",
  entity_type: "",
};

function renderCell(key, value) {
  if (key.includes("amount") || key.includes("value")) return formatCurrency(value);
  if (key.includes("date") || key.includes("_at")) {
    return String(value ?? "").includes("T") ? formatDateTime(value) : formatDate(value);
  }
  return value ?? "—";
}

function buildFilterState(searchParams) {
  return {
    ...defaultFilters,
    ...Object.fromEntries(Object.keys(defaultFilters).map((key) => [key, searchParams.get(key) ?? ""])),
  };
}

function buildApiParams(activeReport, filters) {
  const params = {};

  activeReport.filters?.forEach((key) => {
    const value = filters[key];
    if (!value) return;

    if ((key === "date_from" || key === "date_to") && activeReport.dateMode === "datetime") {
      params[key] = key === "date_from" ? `${value}T00:00:00` : `${value}T23:59:59`;
      return;
    }

    params[key] = value;
  });

  return params;
}

function optionLabelForFilter(key) {
  if (key === "warehouse_id") return "Warehouse";
  if (key === "product_id") return "Product";
  if (key === "category_id") return "Category";
  if (key === "vendor_id") return "Vendor";
  if (key === "customer_id") return "Customer";
  if (key === "status") return "Status";
  if (key === "action") return "Action";
  if (key === "entity_type") return "Entity Type";
  if (key === "date_from") return "Date From";
  if (key === "date_to") return "Date To";
  return key.replaceAll("_", " ");
}

export function ReportsPage() {
  const [params, setParams] = useSearchParams();
  const [state, setState] = useState({ loading: true, error: "", data: null });
  const [catalogState, setCatalogState] = useState({
    loading: true,
    error: "",
    warehouses: [],
    products: [],
    categories: [],
    vendors: [],
    customers: [],
  });
  const reportKey = params.get("report") ?? "inventory-summary";
  const activeReport = reportCatalog.find((report) => report.key === reportKey) ?? reportCatalog[0];
  const appliedFilters = useMemo(() => buildFilterState(params), [params]);
  const [filters, setFilters] = useState(() => buildFilterState(params));

  useEffect(() => {
    setFilters(appliedFilters);
  }, [appliedFilters]);

  useEffect(() => {
    let active = true;

    Promise.all([
      api.get("/warehouses", { params: { page_size: 100 } }),
      api.get("/products", { params: { page_size: 100 } }),
      api.get("/categories", { params: { page_size: 100 } }),
      api.get("/vendors", { params: { page_size: 100 } }),
      api.get("/customers", { params: { page_size: 100 } }),
    ])
      .then(([warehouses, products, categories, vendors, customers]) => {
        if (!active) return;
        setCatalogState({
          loading: false,
          error: "",
          warehouses: warehouses.data.items ?? [],
          products: products.data.items ?? [],
          categories: categories.data.items ?? [],
          vendors: vendors.data.items ?? [],
          customers: customers.data.items ?? [],
        });
      })
      .catch((error) => {
        if (!active) return;
        setCatalogState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load report filters.",
          warehouses: [],
          products: [],
          categories: [],
          vendors: [],
          customers: [],
        });
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    setState({ loading: true, error: "", data: null });
    api
      .get(activeReport.endpoint, { params: buildApiParams(activeReport, appliedFilters) })
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
  }, [activeReport, appliedFilters]);

  const rows = useMemo(() => state.data?.rows ?? [], [state.data]);

  function updateFilter(key, value) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  function runReport(event) {
    event.preventDefault();
    const nextParams = new URLSearchParams();
    nextParams.set("report", activeReport.key);
    activeReport.filters?.forEach((key) => {
      if (filters[key]) {
        nextParams.set(key, filters[key]);
      }
    });
    setParams(nextParams);
  }

  function clearFilters() {
    setFilters(defaultFilters);
    setParams({ report: activeReport.key });
  }

  async function exportCsv() {
    const response = await api.get(activeReport.endpoint, {
      params: { ...buildApiParams(activeReport, appliedFilters), export: "csv" },
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(response.data);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${activeReport.key}.csv`;
    anchor.click();
    window.URL.revokeObjectURL(url);
  }

  function renderFilterControl(key) {
    if (key === "date_from" || key === "date_to") {
      return (
        <label className="report-filter-field" key={key}>
          <span>{optionLabelForFilter(key)}</span>
          <input className="field-input" type="date" value={filters[key]} onChange={(event) => updateFilter(key, event.target.value)} />
        </label>
      );
    }

    if (key === "warehouse_id") {
      return (
        <label className="report-filter-field" key={key}>
          <span>Warehouse</span>
          <select className="field-input" value={filters[key]} onChange={(event) => updateFilter(key, event.target.value)}>
            <option value="">All Warehouses</option>
            {catalogState.warehouses.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
        </label>
      );
    }

    if (key === "product_id") {
      return (
        <label className="report-filter-field" key={key}>
          <span>Product</span>
          <select className="field-input" value={filters[key]} onChange={(event) => updateFilter(key, event.target.value)}>
            <option value="">All Products</option>
            {catalogState.products.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
        </label>
      );
    }

    if (key === "category_id") {
      return (
        <label className="report-filter-field" key={key}>
          <span>Category</span>
          <select className="field-input" value={filters[key]} onChange={(event) => updateFilter(key, event.target.value)}>
            <option value="">All Categories</option>
            {catalogState.categories.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
        </label>
      );
    }

    if (key === "vendor_id") {
      return (
        <label className="report-filter-field" key={key}>
          <span>Vendor</span>
          <select className="field-input" value={filters[key]} onChange={(event) => updateFilter(key, event.target.value)}>
            <option value="">All Vendors</option>
            {catalogState.vendors.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
        </label>
      );
    }

    if (key === "customer_id") {
      return (
        <label className="report-filter-field" key={key}>
          <span>Customer</span>
          <select className="field-input" value={filters[key]} onChange={(event) => updateFilter(key, event.target.value)}>
            <option value="">All Customers</option>
            {catalogState.customers.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
        </label>
      );
    }

    if (key === "status") {
      return (
        <label className="report-filter-field" key={key}>
          <span>Status</span>
          <select className="field-input" value={filters[key]} onChange={(event) => updateFilter(key, event.target.value)}>
            <option value="">All Statuses</option>
            {activeReport.statusOptions?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      );
    }

    return (
      <label className="report-filter-field" key={key}>
        <span>{optionLabelForFilter(key)}</span>
        <input className="field-input" value={filters[key]} onChange={(event) => updateFilter(key, event.target.value)} />
      </label>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Analytics"
        title="Reports"
        description="Run inventory, warehouse, purchase, sales, and audit reports from one reporting surface."
        backTo="/"
        actions={
          <>
            {activeReport.key === "low-stock" ? (
              <Link className="ghost-button" to="/inventory/low-stock">
                Open Low Stock Queue
              </Link>
            ) : null}
            <button className="ghost-button" type="button" onClick={exportCsv}>
              Export CSV
            </button>
          </>
        }
      />

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

        <form className="report-filter-grid" onSubmit={runReport}>
          {activeReport.filters?.map((key) => renderFilterControl(key))}
          <div className="report-filter-actions">
            <button className="primary-button" type="submit">
              Run Report
            </button>
            <button className="ghost-button" type="button" onClick={clearFilters}>
              Clear
            </button>
          </div>
        </form>

        {catalogState.error ? <div className="surface-error">{catalogState.error}</div> : null}
        {state.data?.generated_at ? (
          <div className="helper-note">Generated {formatDateTime(state.data.generated_at)} for {rows.length} rows.</div>
        ) : null}

        {state.loading ? <div className="surface-placeholder">Loading report…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}
        {!state.loading && !state.error && rows.length === 0 ? (
          <div className="surface-empty">
            <h3>No rows returned</h3>
            <p>This report is live. Broaden the filters or choose a different date window to populate results.</p>
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
                {rows.slice(0, 100).map((row, rowIndex) => (
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
