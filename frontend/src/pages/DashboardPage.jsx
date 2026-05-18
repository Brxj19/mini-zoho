import { useEffect, useState } from "react";

import api from "../lib/api";
import { formatCurrency, formatNumber } from "../lib/format";
import { useAuth } from "../contexts/AuthContext";

function QueueRow({ label, value }) {
  return (
    <div className="queue-row">
      <span>{label}</span>
      <strong>{formatNumber(value)}</strong>
    </div>
  );
}

export function DashboardPage() {
  const { user, tenant } = useAuth();
  const [state, setState] = useState({
    loading: true,
    error: "",
    dashboard: null,
    inventorySummary: [],
    salesOrders: [],
  });

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const dashboardEndpoint = user?.role === "SUPER_ADMIN" ? "/dashboard/super-admin" : "/dashboard/tenant";
        const [dashboardResponse, inventoryResponse, salesResponse] = await Promise.all([
          api.get(dashboardEndpoint),
          api.get("/reports/inventory-summary"),
          api.get("/reports/sales-orders"),
        ]);
        if (!active) return;
        setState({
          loading: false,
          error: "",
          dashboard: dashboardResponse.data,
          inventorySummary: inventoryResponse.data.rows ?? [],
          salesOrders: salesResponse.data.rows ?? [],
        });
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load the dashboard.",
          dashboard: null,
          inventorySummary: [],
          salesOrders: [],
        });
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [user?.role]);

  const dashboard = state.dashboard;
  const topStocked = state.inventorySummary.slice(0, 5);

  return (
    <div className="dashboard-layout">
      <section className="page-banner">
        <div className="page-banner-icon">⟡</div>
        <div>
          <h2>Hello, {user?.name?.split(" ")[0] ?? "Operator"}</h2>
          <p>{tenant?.company_name ?? "Platform console"} is ready for product, order, and stock operations.</p>
        </div>
      </section>

      {state.loading ? <div className="workspace-card surface-placeholder">Loading dashboard…</div> : null}
      {state.error ? <div className="workspace-card surface-error">{state.error}</div> : null}

      {!state.loading && dashboard ? (
        <>
          <section className="metric-strip">
            <article className="metric-tile">
              <span>Products</span>
              <strong>{formatNumber(dashboard.total_products)}</strong>
            </article>
            <article className="metric-tile">
              <span>Warehouses</span>
              <strong>{formatNumber(dashboard.total_warehouses ?? dashboard.active_tenants)}</strong>
            </article>
            <article className="metric-tile">
              <span>Open Sales Flow</span>
              <strong>{formatNumber(dashboard.total_sales_orders)}</strong>
            </article>
            <article className="metric-tile">
              <span>Inventory Value</span>
              <strong>{formatCurrency(dashboard.inventory_value ?? 0)}</strong>
            </article>
          </section>

          <section className="dashboard-grid-xl">
            <article className="workspace-card feature-card">
              <div className="card-header-row">
                <h3>Top Stocked Items</h3>
                <span className="micro-tag">This month</span>
              </div>
              {topStocked.length === 0 ? (
                <div className="soft-empty-card">
                  <p>No stocked items are visible yet. Inventory summaries will populate here as catalog activity grows.</p>
                </div>
              ) : (
                <div className="mini-list">
                  {topStocked.map((item) => (
                    <div className="mini-list-row" key={item.product_id}>
                      <div>
                        <strong>{item.product_name}</strong>
                        <span>{item.sku}</span>
                      </div>
                      <div className="metric-pair">
                        <strong>{formatNumber(item.total_quantity)}</strong>
                        <span>{formatCurrency(item.inventory_value)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <aside className="workspace-card queue-card">
              <div className="segmented-toggle">
                <button className="segment-active" type="button">
                  Pending Actions
                </button>
                <button type="button">Recent Activity</button>
              </div>

              <div className="queue-section">
                <h4>Sales</h4>
                <QueueRow label="To Be Packed" value={state.salesOrders.filter((item) => item.status === "CONFIRMED").length} />
                <QueueRow label="To Be Shipped" value={state.salesOrders.filter((item) => item.status === "PACKED").length} />
                <QueueRow label="To Be Delivered" value={state.salesOrders.filter((item) => item.status === "SHIPPED").length} />
              </div>

              <div className="queue-section">
                <h4>Purchases</h4>
                <QueueRow label="To Be Received" value={formatNumber(dashboard.total_purchase_orders ?? 0)} />
                <QueueRow label="Unread Alerts" value={dashboard.unread_notifications ?? 0} />
              </div>

              <div className="queue-section">
                <h4>Inventory</h4>
                <QueueRow label="Below Reorder Level" value={dashboard.low_stock_items ?? 0} />
                <QueueRow label="Customers" value={dashboard.total_customers ?? dashboard.total_users ?? 0} />
              </div>
            </aside>
          </section>

          <section className="dashboard-grid-duo">
            <article className="workspace-card">
              <div className="card-header-row">
                <h3>Sales Pulse</h3>
                <span className="micro-tag">Recent orders</span>
              </div>
              {state.salesOrders.length === 0 ? (
                <div className="soft-empty-card">
                  <p>No sales data has landed yet. Confirmed and shipped orders will show here first.</p>
                </div>
              ) : (
                <div className="mini-list">
                  {state.salesOrders.slice(0, 5).map((item) => (
                    <div className="mini-list-row" key={item.sales_order_id}>
                      <div>
                        <strong>{item.so_number}</strong>
                        <span>{item.customer_name}</span>
                      </div>
                      <div className="metric-pair">
                        <strong>{formatCurrency(item.total_amount)}</strong>
                        <span>{item.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article className="workspace-card">
              <div className="card-header-row">
                <h3>Operations Snapshot</h3>
                <span className="micro-tag">Live workspace</span>
              </div>
              <ul className="notes-list">
                <li>Role access is active for {user?.role?.replaceAll("_", " ").toLowerCase()}.</li>
                <li>Notifications: {dashboard.unread_notifications ?? 0} unread.</li>
                <li>Low stock watchlist: {dashboard.low_stock_items ?? 0} flagged lines.</li>
                <li>Current workspace email: {tenant?.contact_email ?? user?.email ?? "Unavailable"}.</li>
              </ul>
            </article>
          </section>
        </>
      ) : null}
    </div>
  );
}
