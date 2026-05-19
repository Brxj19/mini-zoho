import { useEffect, useMemo, useState } from "react";

import { DashboardWidget } from "../components/DashboardWidget";
import { EmptyState } from "../components/EmptyState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { Tabs } from "../components/Tabs";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";
import { formatCurrency, formatDateTime, formatNumber, titleCase } from "../lib/format";

const periodOptions = [
  { label: "This Month", value: "this_month" },
  { label: "Previous Month", value: "previous_month" },
  { label: "This Year", value: "this_year" },
];

const homeTabs = [
  { key: "dashboard", label: "Dashboard" },
  { key: "getting-started", label: "Getting Started" },
  { key: "recent-activities", label: "Recent Activities" },
];

const checklist = [
  "Update organization profile and users",
  "Add or import your items",
  "Create warehouses and default stock positions",
  "Issue a purchase order",
  "Create and confirm a sales order",
  "Review low-stock and movement reports",
];

export function DashboardPage() {
  const { user, tenant } = useAuth();
  const [homeTab, setHomeTab] = useState("dashboard");
  const [period, setPeriod] = useState("this_month");
  const [state, setState] = useState({
    loading: true,
    error: "",
    dashboard: null,
    inventoryRows: [],
    salesRows: [],
    purchaseRows: [],
    notifications: [],
  });

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      const dashboardEndpoint = user?.role === "SUPER_ADMIN" ? "/dashboard/super-admin" : "/dashboard/tenant";
      setState((current) => ({ ...current, loading: true, error: "" }));

      try {
        const requests =
          user?.role === "SUPER_ADMIN"
            ? [
                api.get(dashboardEndpoint),
                api.get("/notifications", { params: { page_size: 6 } }),
              ]
            : [
                api.get(dashboardEndpoint),
                api.get("/reports/inventory-summary"),
                api.get("/reports/sales-orders"),
                api.get("/reports/purchase-orders"),
                api.get("/notifications", { params: { page_size: 6 } }),
              ];

        const responses = await Promise.all(requests);
        if (!active) {
          return;
        }

        if (user?.role === "SUPER_ADMIN") {
          const [dashboardResponse, notificationResponse] = responses;
          setState({
            loading: false,
            error: "",
            dashboard: dashboardResponse.data,
            inventoryRows: [],
            salesRows: [],
            purchaseRows: [],
            notifications: notificationResponse.data.items ?? [],
          });
          return;
        }

        const [dashboardResponse, inventoryResponse, salesResponse, purchaseResponse, notificationResponse] = responses;
        setState({
          loading: false,
          error: "",
          dashboard: dashboardResponse.data,
          inventoryRows: inventoryResponse.data.rows ?? [],
          salesRows: salesResponse.data.rows ?? [],
          purchaseRows: purchaseResponse.data.rows ?? [],
          notifications: notificationResponse.data.items ?? [],
        });
      } catch (error) {
        if (!active) {
          return;
        }
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load the dashboard right now.",
          dashboard: null,
          inventoryRows: [],
          salesRows: [],
          purchaseRows: [],
          notifications: [],
        });
      }
    }

    loadDashboard();
    return () => {
      active = false;
    };
  }, [period, user?.role]);

  const inventoryTop = useMemo(() => state.inventoryRows.slice(0, 5), [state.inventoryRows]);
  const dashboard = state.dashboard;

  if (state.loading) {
    return <div className="workspace-card surface-placeholder">Loading dashboard…</div>;
  }

  if (state.error || !dashboard) {
    return <div className="workspace-card surface-error">{state.error || "Dashboard data is unavailable."}</div>;
  }

  if (homeTab === "getting-started") {
    return (
      <div className="page-stack">
        <PageHeader
          eyebrow="Home"
          title={`Hello, ${user?.name?.split(" ")[0] ?? "Team"}`}
          description={`${tenant?.company_name ?? "Northstar Inventory"} is ready for catalog, warehouse, and order operations.`}
          actions={
            <select className="field-input compact-field" value={period} onChange={(event) => setPeriod(event.target.value)}>
              {periodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          }
        />
        <div className="home-tabs">
          {homeTabs.map((tab) => (
            <button key={tab.key} className={`home-tab ${homeTab === tab.key ? "is-active" : ""}`} type="button" onClick={() => setHomeTab(tab.key)}>
              {tab.label}
            </button>
          ))}
        </div>
        <div className="detail-grid">
          <DashboardWidget title="Getting Started Checklist" className="widget-span-2">
            <div className="checklist-grid">
              {checklist.map((item, index) => (
                <div key={item} className="checklist-item">
                  <span>{index + 1}</span>
                  <strong>{item}</strong>
                </div>
              ))}
            </div>
          </DashboardWidget>
          <DashboardWidget title="Workspace Context">
            <div className="detail-overview-grid compact">
              <div><span>Company</span><strong>{tenant?.company_name ?? "Platform"}</strong></div>
              <div><span>Contact</span><strong>{tenant?.contact_email ?? user?.email ?? "—"}</strong></div>
              <div><span>Role</span><strong>{titleCase(user?.role)}</strong></div>
              <div><span>Unread alerts</span><strong>{state.notifications.filter((item) => !item.is_read).length}</strong></div>
            </div>
          </DashboardWidget>
        </div>
      </div>
    );
  }

  if (homeTab === "recent-activities") {
    return (
      <div className="page-stack">
        <PageHeader
          eyebrow="Home"
          title="Recent Activities"
          description="A compact feed of order, inventory, and admin events in your current workspace."
          actions={
            <select className="field-input compact-field" value={period} onChange={(event) => setPeriod(event.target.value)}>
              {periodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          }
        />
        <div className="home-tabs">
          {homeTabs.map((tab) => (
            <button key={tab.key} className={`home-tab ${homeTab === tab.key ? "is-active" : ""}`} type="button" onClick={() => setHomeTab(tab.key)}>
              {tab.label}
            </button>
          ))}
        </div>
        <DashboardWidget title="Recent Activities">
          {dashboard.recent_activities?.length ? (
            <div className="mini-list">
              {dashboard.recent_activities.map((activity) => (
                <div className="mini-list-row" key={activity.id}>
                  <div>
                    <strong>{titleCase(activity.action)}</strong>
                    <span>{activity.entity_type ? titleCase(activity.entity_type) : "System event"}</span>
                  </div>
                  <div className="metric-pair">
                    <strong>#{activity.entity_id ?? "—"}</strong>
                    <span>{formatDateTime(activity.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon="activity" title="No recent activity yet" description="The activity feed will populate as your team starts using the workspace." />
          )}
        </DashboardWidget>
      </div>
    );
  }

  if (user?.role === "SUPER_ADMIN") {
    return (
      <div className="page-stack">
        <PageHeader
          eyebrow="Home"
          title={`Hello, ${user?.name?.split(" ")[0] ?? "Admin"}`}
          description="Platform-wide tenant, user, and order visibility for the Northstar Inventory control plane."
          actions={
            <select className="field-input compact-field" value={period} onChange={(event) => setPeriod(event.target.value)}>
              {periodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          }
        />
        <div className="home-tabs">
          {homeTabs.map((tab) => (
            <button key={tab.key} className={`home-tab ${homeTab === tab.key ? "is-active" : ""}`} type="button" onClick={() => setHomeTab(tab.key)}>
              {tab.label}
            </button>
          ))}
        </div>
        <div className="metric-grid">
          <MetricCard label="Total Tenants" value={formatNumber(dashboard.total_tenants)} delta="Platform workspaces" tone="neutral" />
          <MetricCard label="Active Tenants" value={formatNumber(dashboard.active_tenants)} delta="Healthy accounts" tone="positive" />
          <MetricCard label="Total Users" value={formatNumber(dashboard.total_users)} delta="Across all tenants" tone="info" />
          <MetricCard label="Total Products" value={formatNumber(dashboard.total_products)} delta={`${formatNumber(dashboard.total_sales_orders)} sales orders tracked`} tone="warning" />
        </div>
        <div className="detail-grid">
          <DashboardWidget title="Recent Tenant Activity" className="widget-span-2">
            <div className="mini-list">
              {dashboard.recent_tenants?.map((tenantItem) => (
                <div className="mini-list-row" key={tenantItem.id}>
                  <div>
                    <strong>{tenantItem.company_name}</strong>
                    <span>{tenantItem.contact_email}</span>
                  </div>
                  <div className="metric-pair">
                    <StatusBadge value={tenantItem.status} />
                    <span>{formatDateTime(tenantItem.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          </DashboardWidget>
          <DashboardWidget title="Notifications">
            {state.notifications.length ? (
              <div className="mini-list">
                {state.notifications.map((notification) => (
                  <div className="mini-list-row" key={notification.id}>
                    <div>
                      <strong>{notification.title}</strong>
                      <span>{notification.message}</span>
                    </div>
                    <StatusBadge value={notification.type} />
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState icon="bell" title="No platform notifications" description="System notifications will appear here as tenant events accumulate." />
            )}
          </DashboardWidget>
        </div>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Home"
        title={`Hello, ${user?.name?.split(" ")[0] ?? "Team"}`}
        description={`${tenant?.company_name ?? "Northstar Inventory"} is ready for product, order, and warehouse operations.`}
        actions={
          <select className="field-input compact-field" value={period} onChange={(event) => setPeriod(event.target.value)}>
            {periodOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        }
      />

      <div className="home-tabs">
        {homeTabs.map((tab) => (
          <button key={tab.key} className={`home-tab ${homeTab === tab.key ? "is-active" : ""}`} type="button" onClick={() => setHomeTab(tab.key)}>
            {tab.label}
          </button>
        ))}
      </div>

      <div className="metric-grid">
        <MetricCard label="Items" value={formatNumber(dashboard.total_products)} delta="Active catalog rows" tone="neutral" />
        <MetricCard label="Warehouses" value={formatNumber(dashboard.total_warehouses)} delta="Fulfillment locations" tone="info" />
        <MetricCard label="Sales Orders" value={formatNumber(dashboard.total_sales_orders)} delta="Current order pipeline" tone="positive" />
        <MetricCard label="Inventory Value" value={formatCurrency(dashboard.inventory_value)} delta={`${formatNumber(dashboard.low_stock_items)} low stock alerts`} tone="warning" />
      </div>

      <div className="dashboard-grid-primary">
        <DashboardWidget
          title="Top Stocked Items"
          actions={
            <select className="field-input compact-field" value={period} onChange={(event) => setPeriod(event.target.value)}>
              {periodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          }
        >
          {inventoryTop.length ? (
            <div className="mini-list">
              {inventoryTop.map((item, index) => (
                <div className="mini-list-row" key={`${item.product_id}-${index}`}>
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
          ) : (
            <EmptyState icon="box" title="No stocked items yet" description="Your top stocked items will appear here once warehouse stock is recorded." />
          )}
        </DashboardWidget>

        <DashboardWidget title="Pending Actions">
          <div className="queue-section">
            <h4>Sales</h4>
            <div className="queue-row"><span>To Be Packed</span><strong>{state.salesRows.filter((row) => row.status === "CONFIRMED").length}</strong></div>
            <div className="queue-row"><span>To Be Shipped</span><strong>{state.salesRows.filter((row) => row.status === "PACKED").length}</strong></div>
            <div className="queue-row"><span>To Be Delivered</span><strong>{state.salesRows.filter((row) => row.status === "SHIPPED").length}</strong></div>
            <div className="queue-row"><span>To Be Invoiced</span><strong>{state.salesRows.filter((row) => ["CONFIRMED", "PACKED"].includes(row.status)).length}</strong></div>
          </div>
          <div className="queue-section">
            <h4>Purchases</h4>
            <div className="queue-row"><span>To Be Received</span><strong>{state.purchaseRows.filter((row) => row.status === "ISSUED").length}</strong></div>
            <div className="queue-row"><span>Receive In Progress</span><strong>{state.purchaseRows.filter((row) => row.status === "PARTIALLY_RECEIVED").length}</strong></div>
          </div>
          <div className="queue-section">
            <h4>Inventory</h4>
            <div className="queue-row"><span>Below Reorder Level</span><strong>{formatNumber(dashboard.low_stock_items)}</strong></div>
          </div>
        </DashboardWidget>
      </div>

      <div className="dashboard-grid-secondary">
        <DashboardWidget
          title="Sales Order Summary"
          actions={
            <select className="field-input compact-field" value={period} onChange={(event) => setPeriod(event.target.value)}>
              {periodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          }
        >
          {state.salesRows.length ? (
            <div className="mini-list">
              {state.salesRows.slice(0, 5).map((row, index) => (
                <div className="mini-list-row" key={`${row.so_number}-${index}`}>
                  <div>
                    <strong>{row.so_number}</strong>
                    <span>{row.customer_name ?? `Customer #${row.customer_id}`}</span>
                  </div>
                  <div className="metric-pair">
                    <StatusBadge value={row.status} />
                    <span>{formatCurrency(row.total_amount)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon="cart" title="No sales orders yet" description="Your live sales pipeline will appear here as orders are created." />
          )}
        </DashboardWidget>

        <DashboardWidget
          title="Purchase Order Summary"
          actions={
            <select className="field-input compact-field" value={period} onChange={(event) => setPeriod(event.target.value)}>
              {periodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          }
        >
          {state.purchaseRows.length ? (
            <div className="mini-list">
              {state.purchaseRows.slice(0, 5).map((row, index) => (
                <div className="mini-list-row" key={`${row.po_number}-${index}`}>
                  <div>
                    <strong>{row.po_number}</strong>
                    <span>{row.vendor_name ?? `Vendor #${row.vendor_id}`}</span>
                  </div>
                  <div className="metric-pair">
                    <StatusBadge value={row.status} />
                    <span>{formatCurrency(row.total_amount)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon="briefcase" title="No purchase orders yet" description="Inbound procurement activity will show here as soon as POs are issued." />
          )}
        </DashboardWidget>
      </div>

      <div className="detail-grid">
        <DashboardWidget title="Recent Activities" className="widget-span-2">
          {dashboard.recent_activities?.length ? (
            <div className="mini-list">
              {dashboard.recent_activities.map((activity) => (
                <div className="mini-list-row" key={activity.id}>
                  <div>
                    <strong>{titleCase(activity.action)}</strong>
                    <span>{activity.entity_type ? titleCase(activity.entity_type) : "System event"}</span>
                  </div>
                  <span>{formatDateTime(activity.created_at)}</span>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon="activity" title="No recent activity yet" description="Audit activity will appear here once your team starts transacting." />
          )}
        </DashboardWidget>

        <DashboardWidget title="Notifications">
          {state.notifications.length ? (
            <div className="mini-list">
              {state.notifications.map((notification) => (
                <div className="mini-list-row" key={notification.id}>
                  <div>
                    <strong>{notification.title}</strong>
                    <span>{notification.message}</span>
                  </div>
                  <StatusBadge value={notification.type} />
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon="bell" title="No notifications yet" description="Warehouse, order, and stock alerts will appear here." />
          )}
        </DashboardWidget>
      </div>
    </div>
  );
}
