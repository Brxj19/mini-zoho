import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { DashboardWidget } from "../components/DashboardWidget";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";
import { formatCurrency, formatDate, formatDateTime, formatNumber, titleCase } from "../lib/format";
import { ONBOARDING_STATUS_COMPLETED, ONBOARDING_STATUS_PENDING, ONBOARDING_STATUS_SKIPPED, getOnboardingStatus } from "../lib/onboarding";

const periodOptions = [
  { label: "This Month", value: "this_month" },
  { label: "This Quarter", value: "this_quarter" },
  { label: "Previous Month", value: "previous_month" },
  { label: "This Year", value: "this_year" },
];

const homeTabs = [
  { key: "dashboard", label: "Dashboard" },
  { key: "getting-started", label: "Getting Started", requiresOnboarding: true },
  { key: "recent-activities", label: "Recent Activities" },
];

const tenantChecklist = [
  "Update organization profile and workspace preferences",
  "Create or import your first item catalog",
  "Configure warehouses and opening stock",
  "Add vendors and customers",
  "Create purchase and sales orders",
  "Review low stock, reports, and notifications",
];

const superAdminChecklist = [
  "Review new tenant registrations and activation status",
  "Assign subscription plans and monitor usage",
  "Audit platform activity and notifications",
  "Inspect top tenants by catalog and order volume",
  "Review system-wide reports and plan distribution",
  "Coordinate support and governance workflows",
];

function PeriodSelect({ value, onChange }) {
  return (
    <select className="field-input compact-field" value={value} onChange={(event) => onChange(event.target.value)}>
      {periodOptions.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}

function getPeriodRange(period) {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth();

  let start = new Date(currentYear, currentMonth, 1);
  let end = new Date(currentYear, currentMonth + 1, 0);

  if (period === "previous_month") {
    start = new Date(currentYear, currentMonth - 1, 1);
    end = new Date(currentYear, currentMonth, 0);
  }

  if (period === "this_quarter") {
    const quarterStartMonth = Math.floor(currentMonth / 3) * 3;
    start = new Date(currentYear, quarterStartMonth, 1);
    end = new Date(currentYear, quarterStartMonth + 3, 0);
  }

  if (period === "this_year") {
    start = new Date(currentYear, 0, 1);
    end = new Date(currentYear, 11, 31);
  }

  const startDate = start.toISOString().slice(0, 10);
  const endDate = end.toISOString().slice(0, 10);

  return {
    dateFrom: startDate,
    dateTo: endDate,
    dateTimeFrom: `${startDate}T00:00:00`,
    dateTimeTo: `${endDate}T23:59:59`,
  };
}

function getCountByStatus(rows, field, statuses) {
  return rows.filter((row) => statuses.includes(row[field])).length;
}

function sumNumeric(rows, selector) {
  return rows.reduce((total, row) => total + Number(selector(row) ?? 0), 0);
}

function buildTopSellingItems(movementRows) {
  const aggregate = new Map();

  movementRows
    .filter((row) => row.transaction_type === "SALES_DEDUCT")
    .forEach((row) => {
      const current = aggregate.get(row.product_id) ?? {
        product_id: row.product_id,
        product_name: row.product_name,
        sku: row.sku,
        quantity: 0,
      };
      current.quantity += Math.abs(Number(row.quantity ?? 0));
      aggregate.set(row.product_id, current);
    });

  return Array.from(aggregate.values())
    .sort((left, right) => right.quantity - left.quantity)
    .slice(0, 5);
}

function buildProductMix(dashboard, lowStockRows, outOfStockRows) {
  const totalProducts = Number(dashboard?.total_products ?? 0);
  const lowStockCount = lowStockRows.length;
  const outOfStockCount = outOfStockRows.length;
  const healthyCount = Math.max(totalProducts - lowStockCount - outOfStockCount, 0);

  return [
    { label: "Healthy items", count: healthyCount, color: "#7ec8f6" },
    { label: "Low stock", count: lowStockCount, color: "#f5b54c" },
    { label: "Out of stock", count: outOfStockCount, color: "#d5c4f8" },
  ].filter((segment) => segment.count > 0);
}

function buildPlanDistribution(tenantRows, planRows) {
  const distribution = new Map();
  const planNameById = new Map(planRows.map((plan) => [plan.id, plan.name]));

  tenantRows.forEach((tenant) => {
    const planName =
      tenant.subscription_plan?.name ??
      planNameById.get(tenant.subscription_plan_id) ??
      "Unassigned";
    distribution.set(planName, (distribution.get(planName) ?? 0) + 1);
  });

  return Array.from(distribution.entries())
    .map(([label, count]) => ({ label, count }))
    .sort((left, right) => right.count - left.count);
}

function buildTopTenantUsage(usageRows, tenantRows) {
  const tenantMap = new Map(tenantRows.map((tenant) => [tenant.id, tenant]));
  return usageRows
    .map((usage) => {
      const tenant = tenantMap.get(usage.tenant_id);
      return {
        tenant_id: usage.tenant_id,
        company_name: tenant?.company_name ?? `Tenant #${usage.tenant_id}`,
        plan_name: usage.plan_name ?? tenant?.subscription_plan?.name ?? "Unassigned",
        total_orders: usage.total_orders ?? 0,
        total_products: usage.total_products ?? 0,
        total_users: usage.total_users ?? 0,
        total_warehouses: usage.total_warehouses ?? 0,
      };
    })
    .sort((left, right) => {
      if (right.total_orders !== left.total_orders) {
        return right.total_orders - left.total_orders;
      }
      return right.total_products - left.total_products;
    })
    .slice(0, 6);
}

function DashboardLoadingState() {
  return <LoadingState animationKey="appLoading" message="Loading dashboard…" fullPage />;
}

export function DashboardPage() {
  const { user, tenant } = useAuth();
  const [homeTab, setHomeTab] = useState("dashboard");
  const [period, setPeriod] = useState("this_month");
  const [reloadToken, setReloadToken] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: "",
    dashboard: null,
    inventoryRows: [],
    lowStockRows: [],
    outOfStockRows: [],
    salesRows: [],
    purchaseRows: [],
    movementRows: [],
    notifications: [],
    tenantRows: [],
    tenantUsageRows: [],
    planRows: [],
  });

  useEffect(() => {
    if (!tenant?.id || user?.role === "SUPER_ADMIN") {
      return;
    }

    if (getOnboardingStatus(tenant.id) === ONBOARDING_STATUS_SKIPPED) {
      setHomeTab("getting-started");
    }
  }, [tenant?.id, user?.role]);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      const range = getPeriodRange(period);
      setState((current) => ({ ...current, loading: true, error: "" }));

      try {
        if (user?.role === "SUPER_ADMIN") {
          const [dashboardResponse, notificationResponse, tenantsResponse, plansResponse] = await Promise.all([
            api.get("/dashboard/super-admin"),
            api.get("/notifications", { params: { page_size: 8 } }),
            api.get("/tenants", { params: { page_size: 100 } }),
            api.get("/subscription-plans", { params: { page_size: 100 } }),
          ]);

          const tenantRows = tenantsResponse.data.items ?? [];
          const usageResponses = await Promise.all(
            tenantRows.map((tenantItem) => api.get(`/tenants/${tenantItem.id}/usage`)),
          );

          if (!active) {
            return;
          }

          setState({
            loading: false,
            error: "",
            dashboard: dashboardResponse.data,
            inventoryRows: [],
            lowStockRows: [],
            outOfStockRows: [],
            salesRows: [],
            purchaseRows: [],
            movementRows: [],
            notifications: notificationResponse.data.items ?? [],
            tenantRows,
            tenantUsageRows: usageResponses.map((response) => response.data),
            planRows: plansResponse.data.items ?? [],
          });
          return;
        }

        const [dashboardResponse, inventoryResponse, lowStockResponse, outOfStockResponse, salesResponse, purchaseResponse, movementResponse, notificationResponse] =
          await Promise.all([
            api.get("/dashboard/tenant"),
            api.get("/reports/inventory-summary"),
            api.get("/reports/low-stock"),
            api.get("/reports/out-of-stock"),
            api.get("/reports/sales-orders", { params: { date_from: range.dateFrom, date_to: range.dateTo } }),
            api.get("/reports/purchase-orders", { params: { date_from: range.dateFrom, date_to: range.dateTo } }),
            api.get("/reports/stock-movement", {
              params: { date_from: range.dateTimeFrom, date_to: range.dateTimeTo },
            }),
            api.get("/notifications", { params: { page_size: 8 } }),
          ]);

        if (!active) {
          return;
        }

        setState({
          loading: false,
          error: "",
          dashboard: dashboardResponse.data,
          inventoryRows: inventoryResponse.data.rows ?? [],
          lowStockRows: lowStockResponse.data.rows ?? [],
          outOfStockRows: outOfStockResponse.data.rows ?? [],
          salesRows: salesResponse.data.rows ?? [],
          purchaseRows: purchaseResponse.data.rows ?? [],
          movementRows: movementResponse.data.rows ?? [],
          notifications: notificationResponse.data.items ?? [],
          tenantRows: [],
          tenantUsageRows: [],
          planRows: [],
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
          lowStockRows: [],
          outOfStockRows: [],
          salesRows: [],
          purchaseRows: [],
          movementRows: [],
          notifications: [],
          tenantRows: [],
          tenantUsageRows: [],
          planRows: [],
        });
      }
    }

    loadDashboard();
    return () => {
      active = false;
    };
  }, [period, reloadToken, user?.role]);

  const dashboard = state.dashboard;
  const onboardingStatus = tenant?.id ? getOnboardingStatus(tenant.id) : ONBOARDING_STATUS_COMPLETED;
  const shouldShowGetStartedReminder =
    user?.role !== "SUPER_ADMIN" &&
    (onboardingStatus === ONBOARDING_STATUS_PENDING || onboardingStatus === ONBOARDING_STATUS_SKIPPED);
  const visibleHomeTabs = useMemo(
    () =>
      homeTabs.filter((tab) => {
        if (!tab.requiresOnboarding) {
          return true;
        }

        return shouldShowGetStartedReminder;
      }),
    [shouldShowGetStartedReminder],
  );
  const getStartedSecondaryLink =
    user?.role === "TENANT_ADMIN"
      ? { to: "/settings", label: "Review settings" }
      : { to: "/items", label: "Open items" };

  useEffect(() => {
    if (!visibleHomeTabs.some((tab) => tab.key === homeTab)) {
      setHomeTab("dashboard");
    }
  }, [homeTab, visibleHomeTabs]);

  const topStockedItems = useMemo(
    () =>
      [...state.inventoryRows]
        .sort((left, right) => Number(right.total_quantity ?? 0) - Number(left.total_quantity ?? 0))
        .slice(0, 5),
    [state.inventoryRows],
  );
  const topSellingItems = useMemo(() => buildTopSellingItems(state.movementRows), [state.movementRows]);
  const quantityInHand = useMemo(
    () => sumNumeric(state.inventoryRows, (row) => row.total_quantity),
    [state.inventoryRows],
  );
  const quantityAvailable = useMemo(
    () => sumNumeric(state.inventoryRows, (row) => row.available_quantity),
    [state.inventoryRows],
  );
  const totalReserved = useMemo(
    () => sumNumeric(state.inventoryRows, (row) => row.reserved_quantity),
    [state.inventoryRows],
  );
  const salesActivity = useMemo(
    () => ({
      packed: getCountByStatus(state.salesRows, "status", ["CONFIRMED"]),
      shipped: getCountByStatus(state.salesRows, "status", ["PACKED"]),
      delivered: getCountByStatus(state.salesRows, "status", ["SHIPPED"]),
      invoiced: getCountByStatus(state.salesRows, "status", ["DELIVERED"]),
    }),
    [state.salesRows],
  );
  const purchaseActivity = useMemo(
    () => ({
      toReceive: getCountByStatus(state.purchaseRows, "status", ["ISSUED"]),
      partial: getCountByStatus(state.purchaseRows, "status", ["PARTIALLY_RECEIVED"]),
      received: getCountByStatus(state.purchaseRows, "status", ["RECEIVED"]),
      cancelled: getCountByStatus(state.purchaseRows, "status", ["CANCELLED"]),
    }),
    [state.purchaseRows],
  );
  const superAdminDerived = useMemo(() => {
    const tenantRows = state.tenantRows;
    const usageRows = state.tenantUsageRows;
    const planRows = state.planRows;
    const activeTenants = dashboard?.active_tenants ?? 0;
    const totalTenants = dashboard?.total_tenants ?? 0;
    const suspendedTenants = Math.max(totalTenants - activeTenants, 0);
    const createdInLast30Days = tenantRows.filter((item) => {
      const createdAt = new Date(item.created_at);
      return Date.now() - createdAt.getTime() <= 30 * 24 * 60 * 60 * 1000;
    }).length;

    return {
      suspendedTenants,
      createdInLast30Days,
      avgUsersPerTenant: totalTenants ? (dashboard?.total_users ?? 0) / totalTenants : 0,
      avgProductsPerTenant: totalTenants ? (dashboard?.total_products ?? 0) / totalTenants : 0,
      planDistribution: buildPlanDistribution(tenantRows, planRows),
      topTenantUsage: buildTopTenantUsage(usageRows, tenantRows),
    };
  }, [dashboard, state.planRows, state.tenantRows, state.tenantUsageRows]);

  function retryLoad() {
    setReloadToken((current) => current + 1);
  }

  if (state.loading) {
    return <DashboardLoadingState />;
  }

  if (state.error || !dashboard) {
    return (
      <ErrorState
        animationKey="emptyData"
        title="Dashboard data is unavailable."
        description={state.error || "We could not load the latest dashboard metrics."}
        retryLabel="Retry dashboard"
        onRetry={retryLoad}
      />
    );
  }

  const activeTab = visibleHomeTabs.find((item) => item.key === homeTab) ?? visibleHomeTabs[0];
  const productMix = buildProductMix(dashboard, state.lowStockRows, state.outOfStockRows);
  const totalMix = productMix.reduce((total, segment) => total + segment.count, 0);
  const donutStyle =
    totalMix > 0
      ? {
          background: `conic-gradient(${productMix
            .map((segment, index) => {
              const start = productMix
                .slice(0, index)
                .reduce((running, current) => running + (current.count / totalMix) * 360, 0);
              const end = start + (segment.count / totalMix) * 360;
              return `${segment.color} ${start}deg ${end}deg`;
            })
            .join(", ")})`,
        }
      : undefined;

  const dashboardShell = (content, actions = null) => (
    <div className="insights-layout">
      <aside className="insights-side-nav">
        <div className="insights-side-header">
          <p>Insights</p>
          <span>{tenant?.company_name ?? "Northstar Inventory"}</span>
        </div>
        <nav className="insights-side-links" aria-label="Home workspace">
          {visibleHomeTabs.map((item) => (
            <button
              key={item.key}
              type="button"
              className={`insights-side-link ${homeTab === item.key ? "is-active" : ""}`}
              onClick={() => setHomeTab(item.key)}
            >
              <span className="insights-side-link-accent" />
              <div>
                <strong>{item.label}</strong>
                <small>
                  {item.key === "dashboard"
                    ? "Live metrics and signals"
                    : item.key === "getting-started"
                      ? "Set up and operate faster"
                      : "Operational activity feed"}
                </small>
              </div>
            </button>
          ))}
        </nav>
      </aside>
      <div className="insights-main">
        <PageHeader
          eyebrow="Insights"
          title={activeTab.label}
          description={
            homeTab === "dashboard"
              ? user?.role === "SUPER_ADMIN"
                ? "Platform-wide control of tenants, plans, growth, and operational health across Northstar Inventory."
                : `${tenant?.company_name ?? "Northstar Inventory"} is ready for products, warehouses, stock movement, and order operations.`
              : homeTab === "getting-started"
                ? "Use this guided setup lane to configure the workspace and reach a healthy operational baseline."
                : "Track recent admin, stock, sales, and purchasing activity from one place."
          }
          actions={
            <div className="header-action-cluster">
              {actions}
              <button type="button" className="button button-ghost compact-button">
                Filters
              </button>
              <Link className="button button-primary compact-button" to="/reports">
                Add report
              </Link>
            </div>
          }
        />
        {content}
      </div>
    </div>
  );

  if (homeTab === "getting-started") {
    return dashboardShell(
      <div className="detail-grid">
        {shouldShowGetStartedReminder ? (
          <DashboardWidget title="Workspace setup reminder" className="widget-span-2">
            <div className="get-started-dashboard-banner">
              <div className="get-started-dashboard-banner-copy">
                <p className="eyebrow">Home → Get Started</p>
                <h3>
                  {onboardingStatus === ONBOARDING_STATUS_SKIPPED
                    ? "Resume onboarding when you're ready."
                    : "Finish onboarding before you start transacting."}
                </h3>
                <p>
                  {onboardingStatus === ONBOARDING_STATUS_SKIPPED
                    ? "Your team can keep working, but completing setup will finalize your workspace profile and remove this reminder."
                    : "Set up your workspace profile and operating defaults first so the rest of Northstar starts from a clean baseline."}
                </p>
              </div>
              <div className="get-started-dashboard-banner-actions">
                <Link className="button button-primary" to={onboardingStatus === ONBOARDING_STATUS_SKIPPED ? "/onboarding?resume=1" : "/onboarding"}>
                  {onboardingStatus === ONBOARDING_STATUS_SKIPPED ? "Resume onboarding" : "Open onboarding"}
                </Link>
                <Link className="button button-ghost" to={getStartedSecondaryLink.to}>
                  {getStartedSecondaryLink.label}
                </Link>
              </div>
            </div>
          </DashboardWidget>
        ) : null}

        <DashboardWidget title="Getting Started Checklist" className="widget-span-2">
          <div className="checklist-grid">
            {(user?.role === "SUPER_ADMIN" ? superAdminChecklist : tenantChecklist).map((item, index) => (
              <div key={item} className="checklist-item">
                <span>{index + 1}</span>
                <strong>{item}</strong>
              </div>
            ))}
          </div>
        </DashboardWidget>

        <DashboardWidget title="Workspace Context">
          <div className="detail-overview-grid compact">
            <div>
              <span>Workspace</span>
              <strong>{tenant?.company_name ?? "Northstar Platform"}</strong>
            </div>
            <div>
              <span>Role</span>
              <strong>{titleCase(user?.role)}</strong>
            </div>
            <div>
              <span>Unread alerts</span>
              <strong>{state.notifications.filter((item) => !item.is_read).length}</strong>
            </div>
            <div>
              <span>Selected period</span>
              <strong>{periodOptions.find((item) => item.value === period)?.label ?? "This Month"}</strong>
            </div>
          </div>
        </DashboardWidget>

        <DashboardWidget title="Helpful next step">
          <p className="surface-note">
            {user?.role === "SUPER_ADMIN"
              ? "Review plan usage and recent tenant activity before making governance changes."
              : shouldShowGetStartedReminder
                ? "Finish setup first, then create or import items so the rest of the dashboard starts filling with live operational data."
                : "Your setup is complete. Start with items, warehouses, vendors, and customers to light up the rest of the dashboard."}
          </p>
        </DashboardWidget>
      </div>,
      <PeriodSelect value={period} onChange={setPeriod} />,
    );
  }

  if (homeTab === "recent-activities") {
    return dashboardShell(
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
                  <div className="metric-pair">
                    <strong>#{activity.entity_id ?? "—"}</strong>
                    <span>{formatDateTime(activity.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon="activity"
              title="No recent activity yet"
              description="Activity will start appearing here as transactions, approvals, and admin actions accumulate."
            />
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
                  <div className="metric-pair">
                    <StatusBadge value={notification.type} />
                    <span>{formatDateTime(notification.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon="bell"
              title="No notifications yet"
              description="System and workflow alerts will show up here once activity begins."
            />
          )}
        </DashboardWidget>
      </div>,
      <PeriodSelect value={period} onChange={setPeriod} />,
    );
  }

  if (user?.role === "SUPER_ADMIN") {
    return dashboardShell(
      <div className="page-stack">
        <div className="metric-grid">
          <MetricCard label="Total Tenants" value={formatNumber(dashboard.total_tenants)} delta="Active workspaces" tone="neutral" />
          <MetricCard label="Active Tenants" value={formatNumber(dashboard.active_tenants)} delta={`${formatNumber(superAdminDerived.suspendedTenants)} suspended or inactive`} tone="positive" />
          <MetricCard label="Total Users" value={formatNumber(dashboard.total_users)} delta={`${formatNumber(superAdminDerived.avgUsersPerTenant.toFixed(1))} avg users / tenant`} tone="info" />
          <MetricCard label="Total Orders" value={formatNumber((dashboard.total_sales_orders ?? 0) + (dashboard.total_purchase_orders ?? 0))} delta={`${formatNumber(superAdminDerived.createdInLast30Days)} tenants added in 30 days`} tone="warning" />
        </div>

        <div className="dashboard-grid-primary">
          <DashboardWidget
            title="Top Tenants By Usage"
            actions={
              <Link className="button button-ghost compact-button" to="/tenants">
                View tenants
              </Link>
            }
          >
            {superAdminDerived.topTenantUsage.length ? (
              <div className="mini-list">
                {superAdminDerived.topTenantUsage.map((usage) => (
                  <div className="mini-list-row" key={usage.tenant_id}>
                    <div>
                      <strong>{usage.company_name}</strong>
                      <span>{usage.plan_name}</span>
                    </div>
                    <div className="metric-pair">
                      <strong>{formatNumber(usage.total_orders)} orders</strong>
                      <span>
                        {formatNumber(usage.total_products)} items · {formatNumber(usage.total_users)} users
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon="building"
                title="No tenant usage yet"
                description="Top tenants will appear here once workspaces begin creating products and orders."
              />
            )}
          </DashboardWidget>

          <DashboardWidget
            title="Plan Distribution"
            actions={
              <Link className="button button-ghost compact-button" to="/subscription">
                Manage plans
              </Link>
            }
          >
            {superAdminDerived.planDistribution.length ? (
              <div className="dashboard-progress-stack">
                {superAdminDerived.planDistribution.map((plan) => {
                  const percentage = dashboard.total_tenants
                    ? Math.round((plan.count / dashboard.total_tenants) * 100)
                    : 0;
                  return (
                    <div className="dashboard-progress-row" key={plan.label}>
                      <div className="dashboard-progress-labels">
                        <strong>{plan.label}</strong>
                        <span>{formatNumber(plan.count)} tenants</span>
                      </div>
                      <div className="usage-bar">
                        <span className="usage-bar-fill" style={{ width: `${percentage}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <EmptyState
                icon="sparkles"
                title="No plans assigned yet"
                description="As tenants are assigned to plans, the distribution view will show the split here."
              />
            )}
          </DashboardWidget>
        </div>

        <div className="dashboard-grid-secondary">
          <DashboardWidget title="Platform Health">
            <div className="dashboard-stat-grid">
              <div className="dashboard-stat-card">
                <span>Sales Orders</span>
                <strong>{formatNumber(dashboard.total_sales_orders)}</strong>
                <p>Tracked across all tenants</p>
              </div>
              <div className="dashboard-stat-card">
                <span>Purchase Orders</span>
                <strong>{formatNumber(dashboard.total_purchase_orders)}</strong>
                <p>Inbound workflows across the platform</p>
              </div>
              <div className="dashboard-stat-card">
                <span>Products</span>
                <strong>{formatNumber(dashboard.total_products)}</strong>
                <p>{formatNumber(superAdminDerived.avgProductsPerTenant.toFixed(1))} avg products / tenant</p>
              </div>
              <div className="dashboard-stat-card">
                <span>Activation Ratio</span>
                <strong>
                  {dashboard.total_tenants
                    ? `${Math.round((dashboard.active_tenants / dashboard.total_tenants) * 100)}%`
                    : "0%"}
                </strong>
                <p>Tenants currently active</p>
              </div>
            </div>
          </DashboardWidget>
        </div>

        <div className="detail-grid">
          <DashboardWidget title="Recent Tenant Activity" className="widget-span-2">
            {dashboard.recent_tenants?.length ? (
              <div className="mini-list">
                {dashboard.recent_tenants.map((tenantItem) => (
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
            ) : (
              <EmptyState
                icon="building"
                title="No tenant registrations yet"
                description="New workspaces will appear here as organizations start signing up."
              />
            )}
          </DashboardWidget>

          <DashboardWidget title="Recent System Audit Logs">
            {dashboard.recent_activities?.length ? (
              <div className="mini-list">
                {dashboard.recent_activities.slice(0, 6).map((activity) => (
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
              <EmptyState
                icon="shield"
                title="No audit logs yet"
                description="Audit events will appear here once admins and tenants start using the platform."
              />
            )}
          </DashboardWidget>
        </div>
      </div>,
      <PeriodSelect value={period} onChange={setPeriod} />,
    );
  }

  return dashboardShell(
    <div className="page-stack">
      <div className="metric-grid">
        <MetricCard label="Items" value={formatNumber(dashboard.total_products)} delta="Active catalog rows" tone="neutral" />
        <MetricCard label="Sales Orders" value={formatNumber(dashboard.total_sales_orders)} delta={`${formatNumber(salesActivity.packed)} ready for packing`} tone="positive" />
        <MetricCard label="Purchase Orders" value={formatNumber(dashboard.total_purchase_orders)} delta={`${formatNumber(purchaseActivity.toReceive)} still to receive`} tone="info" />
        <MetricCard label="Inventory Value" value={formatCurrency(dashboard.inventory_value)} delta={`${formatNumber(state.lowStockRows.length)} low stock alerts`} tone="warning" />
      </div>

      <div className="insights-dashboard-grid">
        <DashboardWidget
          title="Inventory Balance Report"
          actions={<PeriodSelect value={period} onChange={setPeriod} />}
        >
          {topStockedItems.length ? (
            <div className="insights-bar-chart">
              {topStockedItems.slice(0, 4).map((item) => {
                const maxQuantity = topStockedItems[0]?.total_quantity || 1;
                const barHeight = Math.max(18, Math.round((Number(item.total_quantity ?? 0) / maxQuantity) * 180));
                return (
                  <div className="insights-bar-group" key={item.product_id}>
                    <div className="insights-bar-stack">
                      <span className="insights-bar-label">{formatNumber(item.total_quantity)}</span>
                      <div className="insights-bar" style={{ height: `${barHeight}px` }} />
                    </div>
                    <strong>{item.product_name}</strong>
                    <span>{item.sku}</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState
              icon="box"
              title="No stock balance yet"
              description="Warehouse-backed stock bars will appear here as catalog quantities accumulate."
            />
          )}
        </DashboardWidget>

        <DashboardWidget title="Catalog Mix" actions={<PeriodSelect value={period} onChange={setPeriod} />}>
          {productMix.length ? (
            <div className="insights-donut-block">
              <div className="insights-donut" style={donutStyle}>
                <div className="insights-donut-core">
                  <strong>{formatNumber(dashboard.total_products)}</strong>
                  <span>All items</span>
                </div>
              </div>
              <div className="insights-donut-legend">
                {productMix.map((segment) => (
                  <div className="insights-legend-row" key={segment.label}>
                    <span className="insights-legend-dot" style={{ background: segment.color }} />
                    <div>
                      <strong>{segment.label}</strong>
                      <span>{formatNumber(segment.count)} items</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <EmptyState
              icon="sparkles"
              title="No product mix yet"
              description="Add catalog items and reorder thresholds to unlock this insight."
            />
          )}
        </DashboardWidget>

        <DashboardWidget title="Sales Activity">
          <div className="dashboard-stat-grid">
            <div className="dashboard-stat-card">
              <span>To Be Packed</span>
              <strong>{formatNumber(salesActivity.packed)}</strong>
              <p>Confirmed orders awaiting packaging</p>
            </div>
            <div className="dashboard-stat-card">
              <span>To Be Shipped</span>
              <strong>{formatNumber(salesActivity.shipped)}</strong>
              <p>Packed orders awaiting shipment</p>
            </div>
            <div className="dashboard-stat-card">
              <span>To Be Delivered</span>
              <strong>{formatNumber(salesActivity.delivered)}</strong>
              <p>Shipped orders in transit</p>
            </div>
            <div className="dashboard-stat-card">
              <span>To Be Invoiced</span>
              <strong>{formatNumber(salesActivity.invoiced)}</strong>
              <p>Delivered orders ready for invoicing</p>
            </div>
          </div>
        </DashboardWidget>

        <DashboardWidget title="Pending Actions">
          <div className="queue-section">
            <h4>Sales</h4>
            <div className="queue-row">
              <span>To Be Packed</span>
              <strong>{formatNumber(salesActivity.packed)}</strong>
            </div>
            <div className="queue-row">
              <span>To Be Shipped</span>
              <strong>{formatNumber(salesActivity.shipped)}</strong>
            </div>
            <div className="queue-row">
              <span>To Be Delivered</span>
              <strong>{formatNumber(salesActivity.delivered)}</strong>
            </div>
          </div>
          <div className="queue-section">
            <h4>Purchases</h4>
            <div className="queue-row">
              <span>To Be Received</span>
              <strong>{formatNumber(purchaseActivity.toReceive)}</strong>
            </div>
            <div className="queue-row">
              <span>Receive In Progress</span>
              <strong>{formatNumber(purchaseActivity.partial)}</strong>
            </div>
          </div>
          <div className="queue-section">
            <h4>Inventory</h4>
            <div className="queue-row">
              <span>Low Stock Items</span>
              <strong>{formatNumber(state.lowStockRows.length)}</strong>
            </div>
            <div className="queue-row">
              <span>Out Of Stock Items</span>
              <strong>{formatNumber(state.outOfStockRows.length)}</strong>
            </div>
          </div>
        </DashboardWidget>
      </div>

      <div className="dashboard-grid-secondary">
        <DashboardWidget title="Inventory Summary">
          <div className="dashboard-stat-grid">
            <div className="dashboard-stat-card">
              <span>Quantity In Hand</span>
              <strong>{formatNumber(quantityInHand)}</strong>
              <p>Total physical stock across warehouses</p>
            </div>
            <div className="dashboard-stat-card">
              <span>Available Stock</span>
              <strong>{formatNumber(quantityAvailable)}</strong>
              <p>Ready for allocation or sale</p>
            </div>
            <div className="dashboard-stat-card">
              <span>Reserved Stock</span>
              <strong>{formatNumber(totalReserved)}</strong>
              <p>Allocated against live sales orders</p>
            </div>
            <div className="dashboard-stat-card">
              <span>Warehouses</span>
              <strong>{formatNumber(dashboard.total_warehouses)}</strong>
              <p>Active storage and fulfillment locations</p>
            </div>
          </div>
        </DashboardWidget>

        <DashboardWidget title="Product Details">
          <div className="dashboard-stat-grid">
            <div className="dashboard-stat-card">
              <span>All Items</span>
              <strong>{formatNumber(dashboard.total_products)}</strong>
              <p>Products currently in the catalog</p>
            </div>
            <div className="dashboard-stat-card">
              <span>Low Stock Items</span>
              <strong>{formatNumber(state.lowStockRows.length)}</strong>
              <p>At or below reorder level</p>
            </div>
            <div className="dashboard-stat-card">
              <span>Out Of Stock</span>
              <strong>{formatNumber(state.outOfStockRows.length)}</strong>
              <p>No available quantity remaining</p>
            </div>
            <div className="dashboard-stat-card">
              <span>Customers / Vendors</span>
              <strong>{formatNumber(dashboard.total_customers + dashboard.total_vendors)}</strong>
              <p>{formatNumber(dashboard.total_customers)} customers · {formatNumber(dashboard.total_vendors)} vendors</p>
            </div>
          </div>
        </DashboardWidget>
      </div>

      <div className="dashboard-grid-primary">
        <DashboardWidget
          title="Top Selling Items"
          actions={
            <Link className="button button-ghost compact-button" to="/reports?report=customer-sales">
              Open sales reports
            </Link>
          }
        >
          {topSellingItems.length ? (
            <div className="dashboard-progress-stack">
              {topSellingItems.map((item) => {
                const maxQuantity = topSellingItems[0]?.quantity || 1;
                const width = Math.max(12, Math.round((item.quantity / maxQuantity) * 100));
                return (
                  <div className="dashboard-progress-row" key={item.product_id}>
                    <div className="dashboard-progress-labels">
                      <strong>{item.product_name}</strong>
                      <span>{item.sku}</span>
                    </div>
                    <div className="usage-bar">
                      <span className="usage-bar-fill" style={{ width: `${width}%` }} />
                    </div>
                    <div className="metric-pair">
                      <strong>{formatNumber(item.quantity)}</strong>
                      <span>units sold</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState
              icon="cart"
              title="No top selling items yet"
              description="Sales-driven product movement will appear here once orders are delivered."
            />
          )}
        </DashboardWidget>

        <DashboardWidget title="Top Stocked Items" actions={<PeriodSelect value={period} onChange={setPeriod} />}>
          {topStockedItems.length ? (
            <div className="mini-list">
              {topStockedItems.map((item) => (
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
          ) : (
            <EmptyState
              icon="box"
              title="No stocked items yet"
              description="Warehouse-backed product quantities will populate here once stock is recorded."
            />
          )}
        </DashboardWidget>
      </div>

      <div className="dashboard-grid-secondary">
        <DashboardWidget title="Sales Order Summary" actions={<PeriodSelect value={period} onChange={setPeriod} />}>
          {state.salesRows.length ? (
            <div className="dashboard-progress-stack">
              {[
                { label: "Draft", count: getCountByStatus(state.salesRows, "status", ["DRAFT"]) },
                { label: "Confirmed", count: getCountByStatus(state.salesRows, "status", ["CONFIRMED"]) },
                { label: "Packed", count: getCountByStatus(state.salesRows, "status", ["PACKED"]) },
                { label: "Shipped", count: getCountByStatus(state.salesRows, "status", ["SHIPPED"]) },
                { label: "Delivered", count: getCountByStatus(state.salesRows, "status", ["DELIVERED"]) },
              ].map((item) => {
                const width = state.salesRows.length ? Math.max(10, Math.round((item.count / state.salesRows.length) * 100)) : 0;
                return (
                  <div className="dashboard-progress-row" key={item.label}>
                    <div className="dashboard-progress-labels">
                      <strong>{item.label}</strong>
                      <span>{periodOptions.find((entry) => entry.value === period)?.label}</span>
                    </div>
                    <div className="usage-bar">
                      <span className="usage-bar-fill" style={{ width: `${width}%` }} />
                    </div>
                    <div className="metric-pair">
                      <strong>{formatNumber(item.count)}</strong>
                      <span>orders</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState
              icon="cart"
              title="No sales orders in this period"
              description="Once sales orders are created, their status distribution will appear here."
            />
          )}
        </DashboardWidget>

        <DashboardWidget title="Purchase Order Summary" actions={<PeriodSelect value={period} onChange={setPeriod} />}>
          {state.purchaseRows.length ? (
            <div className="dashboard-progress-stack">
              {[
                { label: "Draft", count: getCountByStatus(state.purchaseRows, "status", ["DRAFT"]) },
                { label: "Issued", count: getCountByStatus(state.purchaseRows, "status", ["ISSUED"]) },
                { label: "Partially Received", count: getCountByStatus(state.purchaseRows, "status", ["PARTIALLY_RECEIVED"]) },
                { label: "Received", count: getCountByStatus(state.purchaseRows, "status", ["RECEIVED"]) },
                { label: "Cancelled", count: getCountByStatus(state.purchaseRows, "status", ["CANCELLED"]) },
              ].map((item) => {
                const width = state.purchaseRows.length
                  ? Math.max(10, Math.round((item.count / state.purchaseRows.length) * 100))
                  : 0;
                return (
                  <div className="dashboard-progress-row" key={item.label}>
                    <div className="dashboard-progress-labels">
                      <strong>{item.label}</strong>
                      <span>{periodOptions.find((entry) => entry.value === period)?.label}</span>
                    </div>
                    <div className="usage-bar">
                      <span className="usage-bar-fill" style={{ width: `${width}%` }} />
                    </div>
                    <div className="metric-pair">
                      <strong>{formatNumber(item.count)}</strong>
                      <span>orders</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState
              icon="briefcase"
              title="No purchase orders in this period"
              description="Purchase order status activity will appear here once inbound procurement starts."
            />
          )}
        </DashboardWidget>
      </div>

    </div>,
    <PeriodSelect value={period} onChange={setPeriod} />,
  );
}
