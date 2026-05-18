import { useEffect, useMemo, useState } from "react";

import api from "../lib/api";
import { DashboardWidget } from "../components/DashboardWidget";
import { EmptyState } from "../components/EmptyState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { Tabs } from "../components/Tabs";

const periodOptions = ["This Month", "This Quarter", "This Year", "Previous Month"];

export function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [homeTab, setHomeTab] = useState("dashboard");
  const [activityTab, setActivityTab] = useState("pending");
  const [period, setPeriod] = useState("This Month");

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    api
      .get("/app/dashboard")
      .then(({ data }) => {
        if (active) {
          setDashboard(data);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const homeTabs = useMemo(
    () => [
      { key: "dashboard", label: "Dashboard" },
      { key: "getting-started", label: "Getting Started" },
      { key: "recent-activities", label: "Recent Activities" },
    ],
    [],
  );

  if (isLoading) {
    return <div className="panel-card">Loading dashboard...</div>;
  }

  if (!dashboard) {
    return <EmptyState icon="dashboard" title="Dashboard unavailable" description="The dashboard data could not be loaded." />;
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Home"
        title={dashboard.role === "SUPER_ADMIN" ? "Platform Overview" : "Inventory Dashboard"}
        description="Live overview from the backend data set with seeded Indian tenants, operators, products, and orders."
        actions={
          <select value={period} onChange={(event) => setPeriod(event.target.value)}>
            {periodOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        }
      />

      <div className="home-tabs">
        {homeTabs.map((tab) => (
          <button
            key={tab.key}
            className={`home-tab ${homeTab === tab.key ? "is-active" : ""}`}
            type="button"
            onClick={() => setHomeTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {homeTab === "getting-started" ? (
        <section className="panel-card">
          <h2>Getting Started</h2>
          <ul className="checklist">
            <li>Review organization settings and preferences</li>
            <li>Import additional items or create new products</li>
            <li>Create purchase orders for low-stock items</li>
            <li>Track sales order fulfillment from the Home dashboard</li>
          </ul>
        </section>
      ) : null}

      {homeTab === "recent-activities" ? (
        <DashboardWidget title="Recent Activities">
          <ul className="activity-list">
            {dashboard.recent_activities.map((activity) => (
              <li key={activity.id}>
                <strong>{activity.action}</strong>
                <p>{activity.module}</p>
                <span>{activity.createdAt}</span>
              </li>
            ))}
          </ul>
        </DashboardWidget>
      ) : null}

      {homeTab === "dashboard" ? (
        <>
          <section className="metrics-grid">
            {dashboard.metrics.map((metric) => (
              <MetricCard key={metric.label} {...metric} />
            ))}
          </section>

          <section className="dashboard-main-grid">
            <DashboardWidget
              title="Top Selling Items"
              actions={
                <select value={period} onChange={(event) => setPeriod(event.target.value)}>
                  {periodOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              }
              className="widget-span-2"
            >
              <ul className="ranked-list">
                {dashboard.top_selling_items?.map((item) => (
                  <li key={item.sku}>
                    <div>
                      <strong>{item.name}</strong>
                      <span>{item.sku}</span>
                    </div>
                    <div className="ranked-list-meta">
                      <span>{item.units} units</span>
                      <strong>{item.revenue}</strong>
                    </div>
                  </li>
                ))}
              </ul>
            </DashboardWidget>

            <DashboardWidget title="Pending Actions">
              <Tabs
                items={[
                  { key: "pending", label: "Pending Actions" },
                  { key: "recent", label: "Recent Activities" },
                ]}
                activeKey={activityTab}
                onChange={setActivityTab}
              />

              {activityTab === "pending" ? (
                <div className="queue-sections">
                  {Object.entries(dashboard.pending_actions ?? {}).map(([section, items]) => (
                    <div className="queue-group" key={section}>
                      <h3>{section}</h3>
                      {items.map((item) => (
                        <div className="queue-row" key={item.label}>
                          <span>{item.label}</span>
                          <strong>{item.value}</strong>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              ) : (
                <ul className="activity-list">
                  {dashboard.recent_activities.map((activity) => (
                    <li key={activity.id}>
                      <strong>{activity.action}</strong>
                      <p>{activity.module}</p>
                      <span>{activity.createdAt}</span>
                    </li>
                  ))}
                </ul>
              )}
            </DashboardWidget>

            <DashboardWidget
              title="Top Stocked Items"
              actions={
                <select value={period} onChange={(event) => setPeriod(event.target.value)}>
                  {periodOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              }
            >
              <ul className="compact-stat-list">
                {dashboard.top_stocked_items?.map((item) => (
                  <li key={item.name}>
                    <div>
                      <strong>{item.name}</strong>
                      <span>{item.quantity} units</span>
                    </div>
                    <strong>{item.value}</strong>
                  </li>
                ))}
              </ul>
            </DashboardWidget>

            <DashboardWidget
              title="Sales Activity"
              actions={
                <select value={period} onChange={(event) => setPeriod(event.target.value)}>
                  {periodOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              }
            >
              <div className="mini-bar-chart">
                {(dashboard.sales_activity ?? []).map((item) => (
                  <div key={item.label} className="mini-bar-column">
                    <span style={{ height: `${Math.max(item.value * 10, 14)}px` }} />
                    <small>{item.label}</small>
                  </div>
                ))}
              </div>
            </DashboardWidget>
          </section>

          <section className="dashboard-secondary-grid">
            <DashboardWidget title="Sales Activity">
              <div className="mini-metrics-grid">
                {(dashboard.sales_activity ?? []).map((item) => (
                  <article key={item.label} className="mini-metric-card">
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                  </article>
                ))}
              </div>
            </DashboardWidget>

            <DashboardWidget title="Product Details">
              <div className="mini-metrics-grid">
                {(dashboard.product_details ?? []).map((item) => (
                  <article key={item.label} className="mini-metric-card">
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                  </article>
                ))}
              </div>
            </DashboardWidget>

            <DashboardWidget title="Notifications">
              <ul className="notification-list">
                {(dashboard.notifications ?? []).map((item) => (
                  <li key={item.id ?? item.title} className="notification-row">
                    <strong>{item.title}</strong>
                  </li>
                ))}
              </ul>
            </DashboardWidget>
          </section>
        </>
      ) : null}
    </div>
  );
}
