import { useEffect, useMemo, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";
import { formatCurrency, formatNumber } from "../lib/format";

const blankPlan = {
  code: "",
  name: "",
  description: "",
  monthly_price: "0",
  annual_price: "0",
  max_users: "",
  max_products: "",
  max_warehouses: "",
  max_monthly_sales_orders: "",
  max_monthly_purchase_orders: "",
  max_monthly_stock_transfers: "",
  barcode_enabled: true,
  advanced_inventory_enabled: false,
  integrations_enabled: false,
  ai_assistant_enabled: false,
};

function planPayload(form) {
  return {
    code: form.code,
    name: form.name,
    description: form.description || null,
    monthly_price: Number(form.monthly_price || 0),
    annual_price: Number(form.annual_price || 0),
    max_users: form.max_users ? Number(form.max_users) : null,
    max_products: form.max_products ? Number(form.max_products) : null,
    max_warehouses: form.max_warehouses ? Number(form.max_warehouses) : null,
    max_monthly_sales_orders: form.max_monthly_sales_orders ? Number(form.max_monthly_sales_orders) : null,
    max_monthly_purchase_orders: form.max_monthly_purchase_orders ? Number(form.max_monthly_purchase_orders) : null,
    max_monthly_stock_transfers: form.max_monthly_stock_transfers ? Number(form.max_monthly_stock_transfers) : null,
    barcode_enabled: form.barcode_enabled,
    advanced_inventory_enabled: form.advanced_inventory_enabled,
    integrations_enabled: form.integrations_enabled,
    ai_assistant_enabled: form.ai_assistant_enabled,
  };
}

export function SubscriptionPage() {
  const { user, tenant } = useAuth();
  const isSuperAdmin = user?.role === "SUPER_ADMIN";
  const [reloadKey, setReloadKey] = useState(0);
  const [tenantSelection, setTenantSelection] = useState(String(tenant?.id ?? ""));
  const [plans, setPlans] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [usage, setUsage] = useState(null);
  const [selectedPlanId, setSelectedPlanId] = useState("");
  const [planForm, setPlanForm] = useState(blankPlan);
  const [state, setState] = useState({ loading: true, saving: false, error: "", success: "" });

  useEffect(() => {
    if (!tenant?.id || isSuperAdmin) {
      return;
    }
    setTenantSelection(String(tenant.id));
  }, [tenant?.id, isSuperAdmin]);

  useEffect(() => {
    let active = true;

    async function load() {
      setState((current) => ({ ...current, loading: true, error: "", success: "" }));

      try {
        const requests = [api.get("/subscription-plans", { params: { page_size: 20 } })];
        if (isSuperAdmin) {
          requests.push(api.get("/tenants", { params: { page_size: 100 } }));
        }
        const [plansResponse, tenantsResponse] = await Promise.all(requests);
        if (!active) return;

        const planItems = plansResponse.data.items ?? [];
        const tenantItems = isSuperAdmin ? tenantsResponse?.data?.items ?? [] : tenant ? [tenant] : [];
        const effectiveTenantId = isSuperAdmin ? Number(tenantSelection || tenantItems[0]?.id || 0) : tenant?.id;

        setPlans(planItems);
        setTenants(tenantItems);
        if (!selectedPlanId && planItems[0]?.id) {
          setSelectedPlanId(String(planItems[0].id));
          setPlanForm({
            ...blankPlan,
            ...Object.fromEntries(Object.entries(planItems[0]).map(([key, value]) => [key, value ?? ""])),
          });
        }

        if (effectiveTenantId) {
          const usageResponse = await api.get(`/tenants/${effectiveTenantId}/usage`);
          if (!active) return;
          setUsage(usageResponse.data);
        } else {
          setUsage(null);
        }

        setState({ loading: false, saving: false, error: "", success: "" });
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          saving: false,
          error: error?.response?.data?.detail ?? "Unable to load subscription governance data.",
          success: "",
        });
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [isSuperAdmin, reloadKey, selectedPlanId, tenant?.id, tenant, tenantSelection]);

  const selectedTenant = useMemo(
    () => tenants.find((item) => String(item.id) === String(tenantSelection)) ?? null,
    [tenantSelection, tenants],
  );

  const selectedPlan = useMemo(
    () => plans.find((item) => String(item.id) === String(selectedPlanId)) ?? null,
    [plans, selectedPlanId],
  );

  function updatePlanField(field, value) {
    setPlanForm((current) => ({ ...current, [field]: value }));
  }

  function choosePlan(plan) {
    setSelectedPlanId(String(plan.id));
    setPlanForm({
      code: plan.code ?? "",
      name: plan.name ?? "",
      description: plan.description ?? "",
      monthly_price: String(plan.monthly_price ?? 0),
      annual_price: String(plan.annual_price ?? 0),
      max_users: plan.max_users ?? "",
      max_products: plan.max_products ?? "",
      max_warehouses: plan.max_warehouses ?? "",
      max_monthly_sales_orders: plan.max_monthly_sales_orders ?? "",
      max_monthly_purchase_orders: plan.max_monthly_purchase_orders ?? "",
      max_monthly_stock_transfers: plan.max_monthly_stock_transfers ?? "",
      barcode_enabled: Boolean(plan.barcode_enabled),
      advanced_inventory_enabled: Boolean(plan.advanced_inventory_enabled),
      integrations_enabled: Boolean(plan.integrations_enabled),
      ai_assistant_enabled: Boolean(plan.ai_assistant_enabled),
    });
  }

  async function handlePlanSave(event) {
    event.preventDefault();
    setState((current) => ({ ...current, saving: true, error: "", success: "" }));
    try {
      if (selectedPlanId) {
        await api.patch(`/subscription-plans/${selectedPlanId}`, planPayload(planForm));
      } else {
        const response = await api.post("/subscription-plans", planPayload(planForm));
        setSelectedPlanId(String(response.data.id));
      }
      setState({ loading: false, saving: false, error: "", success: "Subscription plan saved successfully." });
      setReloadKey((value) => value + 1);
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to save this subscription plan.",
      }));
    }
  }

  async function assignPlan() {
    if (!selectedTenant || !selectedPlanId) {
      return;
    }
    setState((current) => ({ ...current, saving: true, error: "", success: "" }));
    try {
      await api.patch(`/tenants/${selectedTenant.id}/plan`, { subscription_plan_id: Number(selectedPlanId) });
      setState({ loading: false, saving: false, error: "", success: "Tenant plan assignment updated." });
      setReloadKey((value) => value + 1);
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to assign this plan.",
      }));
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="SaaS Governance"
        title="Subscription And Usage"
        description="Track tenant plan limits, feature access, and operational usage across the workspace."
        backTo="/"
        actions={
          isSuperAdmin ? (
            <button
              className="ghost-button"
              type="button"
              onClick={() => {
                setSelectedPlanId("");
                setPlanForm(blankPlan);
              }}
            >
              New Plan
            </button>
          ) : null
        }
      />

      {state.success ? <div className="surface-success">{state.success}</div> : null}
      {state.error ? <div className="surface-error">{state.error}</div> : null}

      {state.loading ? <div className="workspace-card surface-placeholder">Loading subscription governance…</div> : null}

      {!state.loading && !plans.length ? (
        <EmptyState
          icon="sparkles"
          title="No subscription plans configured"
          description="Create a plan catalog to start governing tenant usage and feature access."
        />
      ) : null}

      {!state.loading && plans.length ? (
        <>
          <section className="detail-grid">
            <article className="workspace-card">
              <div className="card-header-row">
                <div>
                  <h3>Plan Catalog</h3>
                  <span className="helper-note">Select a plan to review limits and configure tenant assignment.</span>
                </div>
              </div>
              <div className="metric-grid">
                {plans.map((plan) => (
                  <button
                    className={`metric-card metric-card-button ${String(plan.id) === String(selectedPlanId) ? "is-selected" : ""}`}
                    key={plan.id}
                    type="button"
                    onClick={() => choosePlan(plan)}
                  >
                    <span className="metric-label">{plan.code}</span>
                    <strong>{plan.name}</strong>
                    <span className="metric-value">{formatCurrency(plan.monthly_price)}/mo</span>
                  </button>
                ))}
              </div>
            </article>

            <article className="workspace-card">
              <div className="card-header-row">
                <h3>{isSuperAdmin ? "Plan Editor" : "Selected Plan"}</h3>
              </div>
              {isSuperAdmin ? (
                <form className="form-shell" onSubmit={handlePlanSave}>
                  <div className="form-grid-wide">
                    <label>
                      Plan code
                      <input className="field-input" value={planForm.code} onChange={(event) => updatePlanField("code", event.target.value)} required />
                    </label>
                    <label>
                      Plan name
                      <input className="field-input" value={planForm.name} onChange={(event) => updatePlanField("name", event.target.value)} required />
                    </label>
                    <label>
                      Monthly price
                      <input className="field-input" type="number" min="0" step="0.01" value={planForm.monthly_price} onChange={(event) => updatePlanField("monthly_price", event.target.value)} />
                    </label>
                    <label>
                      Annual price
                      <input className="field-input" type="number" min="0" step="0.01" value={planForm.annual_price} onChange={(event) => updatePlanField("annual_price", event.target.value)} />
                    </label>
                    <label>
                      Max users
                      <input className="field-input" type="number" min="1" value={planForm.max_users} onChange={(event) => updatePlanField("max_users", event.target.value)} />
                    </label>
                    <label>
                      Max products
                      <input className="field-input" type="number" min="1" value={planForm.max_products} onChange={(event) => updatePlanField("max_products", event.target.value)} />
                    </label>
                    <label>
                      Max warehouses
                      <input className="field-input" type="number" min="1" value={planForm.max_warehouses} onChange={(event) => updatePlanField("max_warehouses", event.target.value)} />
                    </label>
                    <label>
                      Monthly sales orders
                      <input className="field-input" type="number" min="1" value={planForm.max_monthly_sales_orders} onChange={(event) => updatePlanField("max_monthly_sales_orders", event.target.value)} />
                    </label>
                    <label>
                      Monthly purchase orders
                      <input className="field-input" type="number" min="1" value={planForm.max_monthly_purchase_orders} onChange={(event) => updatePlanField("max_monthly_purchase_orders", event.target.value)} />
                    </label>
                    <label>
                      Monthly stock transfers
                      <input className="field-input" type="number" min="1" value={planForm.max_monthly_stock_transfers} onChange={(event) => updatePlanField("max_monthly_stock_transfers", event.target.value)} />
                    </label>
                    <label className="field-span-full">
                      Description
                      <textarea className="field-input field-textarea" value={planForm.description} onChange={(event) => updatePlanField("description", event.target.value)} />
                    </label>
                    <label className="checkbox-row">
                      <input type="checkbox" checked={planForm.barcode_enabled} onChange={(event) => updatePlanField("barcode_enabled", event.target.checked)} />
                      Barcode tools enabled
                    </label>
                    <label className="checkbox-row">
                      <input type="checkbox" checked={planForm.advanced_inventory_enabled} onChange={(event) => updatePlanField("advanced_inventory_enabled", event.target.checked)} />
                      Advanced inventory enabled
                    </label>
                    <label className="checkbox-row">
                      <input type="checkbox" checked={planForm.integrations_enabled} onChange={(event) => updatePlanField("integrations_enabled", event.target.checked)} />
                      Integrations enabled
                    </label>
                    <label className="checkbox-row">
                      <input type="checkbox" checked={planForm.ai_assistant_enabled} onChange={(event) => updatePlanField("ai_assistant_enabled", event.target.checked)} />
                      AI assistant enabled
                    </label>
                  </div>
                  <div className="form-actions">
                    <button className="primary-button" type="submit" disabled={state.saving}>
                      {state.saving ? "Saving…" : selectedPlanId ? "Save Plan" : "Create Plan"}
                    </button>
                  </div>
                </form>
              ) : selectedPlan ? (
                <div className="kv-grid">
                  <div className="kv-item">
                    <span>Plan</span>
                    <strong>{selectedPlan.name}</strong>
                  </div>
                  <div className="kv-item">
                    <span>Monthly price</span>
                    <strong>{formatCurrency(selectedPlan.monthly_price)}</strong>
                  </div>
                  <div className="kv-item">
                    <span>Advanced inventory</span>
                    <strong>{selectedPlan.advanced_inventory_enabled ? "Enabled" : "Disabled"}</strong>
                  </div>
                  <div className="kv-item">
                    <span>Integrations</span>
                    <strong>{selectedPlan.integrations_enabled ? "Enabled" : "Disabled"}</strong>
                  </div>
                </div>
              ) : null}
            </article>
          </section>

          <section className="detail-grid">
            <article className="workspace-card">
              <div className="card-header-row">
                <h3>Tenant Plan Usage</h3>
              </div>
              {isSuperAdmin ? (
                <div className="table-toolbar">
                  <select className="field-input compact-field" value={tenantSelection} onChange={(event) => setTenantSelection(event.target.value)}>
                    {tenants.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.company_name}
                      </option>
                    ))}
                  </select>
                  <select className="field-input compact-field" value={selectedPlanId} onChange={(event) => setSelectedPlanId(event.target.value)}>
                    {plans.map((plan) => (
                      <option key={plan.id} value={plan.id}>
                        {plan.name}
                      </option>
                    ))}
                  </select>
                  <button className="button button-primary" type="button" onClick={assignPlan} disabled={state.saving || !selectedTenant || !selectedPlanId}>
                    Assign Plan
                  </button>
                </div>
              ) : null}

              {usage ? (
                <div className="usage-stack">
                  <div className="kv-grid">
                    <div className="kv-item">
                      <span>Tenant</span>
                      <strong>{selectedTenant?.company_name ?? tenant?.company_name ?? "Current Tenant"}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Assigned plan</span>
                      <strong>{usage.plan_name ?? "Unassigned"}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Users</span>
                      <strong>{formatNumber(usage.total_users)}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Products</span>
                      <strong>{formatNumber(usage.total_products)}</strong>
                    </div>
                  </div>

                  <div className="usage-grid">
                    {Object.entries(usage.limits ?? {}).map(([key, metric]) => (
                      <div className="usage-card" key={key}>
                        <div className="card-header-row">
                          <strong>{metric.label}</strong>
                          <span>{metric.limit == null ? "Unlimited" : `${metric.current}/${metric.limit}`}</span>
                        </div>
                        <div className="usage-bar">
                          <span
                            className={`usage-bar-fill ${metric.limit_reached ? "is-danger" : ""}`}
                            style={{ width: `${Math.min(metric.percentage ?? 0, 100)}%` }}
                          />
                        </div>
                        <p>
                          {metric.limit == null
                            ? "No plan limit applied."
                            : `${metric.remaining} remaining before this plan reaches its cap.`}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="surface-placeholder">Choose a tenant to inspect plan usage.</div>
              )}
            </article>
          </section>
        </>
      ) : null}
    </div>
  );
}
