import { useEffect, useState } from "react";

import api from "../lib/api";
import { dashboardData } from "../lib/demoData";
import { DashboardWidget } from "../components/DashboardWidget";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { Tabs } from "../components/Tabs";
import { useAuthStore } from "../stores/authStore";

export function DashboardPage() {
  const role = useAuthStore((state) => state.user?.role);
  const [health, setHealth] = useState({ status: "checking" });
  const [activityTab, setActivityTab] = useState("pending");
  const metrics = role === "SUPER_ADMIN" ? dashboardData.superAdminMetrics : dashboardData.tenantMetrics;

  useEffect(() => {
    let active = true;

    api
      .get("/health/")
      .then(({ data }) => {
        if (active) {
          setHealth({ status: data.status });
        }
      })
      .catch(() => {
        if (active) {
          setHealth({ status: "offline" });
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Operations Dashboard"
        title={role === "SUPER_ADMIN" ? "Platform Overview" : "Inventory Dashboard"}
        description="A compact, card-based control room for the most important inventory, sales, purchasing, and platform signals."
        actions={
          <div className="header-inline-chips">
            <span className={`status-pill ${health.status === "ok" ? "is-success" : "is-warning"}`}>
              API health: {health.status}
            </span>
            <select defaultValue="this-month">
              <option value="this-month">This Month</option>
              <option value="this-year">This Year</option>
              <option value="previous-month">Previous Month</option>
            </select>
          </div>
        }
      />

      <section className="metrics-grid">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </section>

      <section className="dashboard-main-grid">
        <DashboardWidget
          title="Top Selling Items"
          actions={<span className="widget-helper">This Month</span>}
          className="widget-span-2"
        >
          <ul className="ranked-list">
            {dashboardData.topSellingItems.map((item) => (
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
              {Object.entries(dashboardData.pendingActions).map(([section, items]) => (
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
              {dashboardData.recentActivities.map((activity) => (
                <li key={activity.title}>
                  <strong>{activity.title}</strong>
                  <p>{activity.detail}</p>
                  <span>{activity.time}</span>
                </li>
              ))}
            </ul>
          )}
        </DashboardWidget>

        <DashboardWidget title="Top Stocked Items">
          <ul className="compact-stat-list">
            {dashboardData.topStockedItems.map((item) => (
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

        <DashboardWidget title="Sales by Channel">
          <div className="empty-chart">
            <div className="mini-bar-chart">
              {dashboardData.salesSummary.map((item) => (
                <div key={item.label} className="mini-bar-column">
                  <span style={{ height: `${Math.max(item.value * 8, 16)}px` }} />
                  <small>{item.label}</small>
                </div>
              ))}
            </div>
          </div>
        </DashboardWidget>
      </section>

      <section className="dashboard-secondary-grid">
        <DashboardWidget title="Sales Activity">
          <div className="mini-metrics-grid">
            {dashboardData.salesActivity.map((item) => (
              <article key={item.label} className="mini-metric-card">
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </article>
            ))}
          </div>
        </DashboardWidget>

        <DashboardWidget title="Product Details">
          <div className="mini-metrics-grid">
            {dashboardData.productDetails.map((item) => (
              <article key={item.label} className="mini-metric-card">
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </article>
            ))}
          </div>
        </DashboardWidget>

        <DashboardWidget title="Notifications">
          <ul className="notification-list">
            {dashboardData.notifications.map((item) => (
              <li key={item.title} className={`notification-row tone-${item.kind}`}>
                <strong>{item.title}</strong>
              </li>
            ))}
          </ul>
        </DashboardWidget>
      </section>
    </div>
  );
}
