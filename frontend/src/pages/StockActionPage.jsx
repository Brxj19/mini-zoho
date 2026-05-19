import { useEffect, useMemo, useState } from "react";

import { BackButton } from "../components/BackButton";
import { EmptyState } from "../components/EmptyState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";
import { hasAnyRole } from "../lib/permissions";
import { formatNumber } from "../lib/format";

const actionConfig = {
  "stock-in": {
    title: "Stock In",
    description: "Record inbound stock against a warehouse and create a transaction log entry.",
    endpoint: "/inventory/stock-in",
    fields: { quantityLabel: "Quantity", quantityKey: "quantity", noteRequired: false },
    roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"],
  },
  "stock-out": {
    title: "Stock Out",
    description: "Ship inventory out while preserving a complete stock movement record.",
    endpoint: "/inventory/stock-out",
    fields: { quantityLabel: "Quantity", quantityKey: "quantity", noteRequired: false },
    roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"],
  },
  adjustment: {
    title: "Stock Adjustment",
    description: "Apply a counted correction with a required operational note.",
    endpoint: "/inventory/adjust",
    fields: { quantityLabel: "Quantity Delta", quantityKey: "quantity_delta", noteRequired: true },
    roles: ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"],
  },
};

export function StockActionPage({ actionKey }) {
  const config = actionConfig[actionKey];
  const { user } = useAuth();
  const canSubmit = hasAnyRole(user, config.roles);
  const [reloadKey, setReloadKey] = useState(0);
  const [options, setOptions] = useState({ products: [], warehouses: [] });
  const [stockSnapshot, setStockSnapshot] = useState({ loading: false, current: null });
  const [form, setForm] = useState({
    product_id: "",
    warehouse_id: "",
    quantity: "1",
    quantity_delta: "0",
    note: "",
    reference_type: "",
    reference_id: "",
    batch_number: "",
    expiry_date: "",
    warranty_until: "",
    serial_numbers: "",
  });
  const [state, setState] = useState({ loading: true, saving: false, error: "", success: "" });

  useEffect(() => {
    let active = true;
    Promise.all([
      api.get("/products", { params: { page_size: 100 } }),
      api.get("/warehouses", { params: { page_size: 100 } }),
    ])
      .then(([products, warehouses]) => {
        if (!active) return;
        setOptions({ products: products.data.items ?? [], warehouses: warehouses.data.items ?? [] });
        setState((current) => ({ ...current, loading: false }));
      })
      .catch((error) => {
        if (!active) return;
        setState({ loading: false, saving: false, error: error?.response?.data?.detail ?? "Unable to load stock action options.", success: "" });
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  useEffect(() => {
    let active = true;

    async function loadStockSnapshot() {
      if (!form.product_id || !form.warehouse_id) {
        setStockSnapshot({ loading: false, current: null });
        return;
      }

      setStockSnapshot((current) => ({ ...current, loading: true }));

      try {
        const response = await api.get(`/products/${form.product_id}/stock`);
        if (!active) return;
        const current = (response.data.warehouses ?? []).find(
          (warehouse) => String(warehouse.warehouse_id) === String(form.warehouse_id),
        );
        setStockSnapshot({ loading: false, current: current ?? null });
      } catch {
        if (!active) return;
        setStockSnapshot({ loading: false, current: null });
      }
    }

    loadStockSnapshot();
    return () => {
      active = false;
    };
  }, [form.product_id, form.warehouse_id]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  const selectedProduct = options.products.find((product) => String(product.id) === String(form.product_id));
  const currentAvailable = Number(stockSnapshot.current?.available_quantity ?? 0);
  const currentQuantity = Number(stockSnapshot.current?.quantity ?? 0);
  const deltaValue = Number(form[config.fields.quantityKey] ?? 0);
  const resultingAvailable = useMemo(() => {
    if (actionKey === "stock-in") return currentAvailable + deltaValue;
    if (actionKey === "stock-out") return currentAvailable - deltaValue;
    return currentAvailable + deltaValue;
  }, [actionKey, currentAvailable, deltaValue]);

  async function handleSubmit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, saving: true, error: "", success: "" }));

    const payload = {
      product_id: Number(form.product_id),
      warehouse_id: Number(form.warehouse_id),
      note: form.note || null,
      reference_type: form.reference_type || null,
      reference_id: form.reference_id ? Number(form.reference_id) : null,
      [config.fields.quantityKey]: Number(form[config.fields.quantityKey]),
    };

    const serialNumbers = form.serial_numbers
      .split(/[\n,]+/)
      .map((value) => value.trim())
      .filter(Boolean);

    if (actionKey === "stock-in") {
      payload.serial_numbers = serialNumbers;
      if (selectedProduct?.batch_tracking_enabled) {
        payload.batch = {
          batch_number: form.batch_number,
          expiry_date: form.expiry_date || null,
          warranty_until: form.warranty_until || null,
        };
      }
    }

    if (actionKey === "stock-out" || actionKey === "adjustment") {
      payload.serial_numbers = serialNumbers;
      payload.batch_number = form.batch_number || null;
    }

    try {
      await api.post(config.endpoint, payload);
      setState({ loading: false, saving: false, error: "", success: `${config.title} saved successfully.` });
      setForm((current) => ({
        ...current,
        quantity: "1",
        quantity_delta: "0",
        note: "",
        reference_type: "",
        reference_id: "",
        batch_number: "",
        expiry_date: "",
        warranty_until: "",
        serial_numbers: "",
      }));
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? `Unable to submit ${config.title.toLowerCase()}.`,
      }));
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Inventory Action"
        title={config.title}
        description={config.description}
        backTo="/inventory/transactions"
      />

      <div className="metric-grid">
        <MetricCard label="Current On Hand" value={formatNumber(currentQuantity)} delta="Selected warehouse quantity" tone="neutral" />
        <MetricCard label="Current Available" value={formatNumber(currentAvailable)} delta="Ready for allocation" tone="info" />
        <MetricCard label="Requested Change" value={formatNumber(deltaValue)} delta={config.fields.quantityLabel} tone={actionKey === "stock-out" ? "warning" : "positive"} />
        <MetricCard label="Resulting Available" value={formatNumber(resultingAvailable)} delta="Post-action projection" tone={resultingAvailable < 0 ? "warning" : "positive"} />
      </div>

      <form className="form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading action form…</div> : null}
        {state.success ? <div className="surface-success">{state.success}</div> : null}
        {!state.loading && state.error ? (
          <EmptyState
            icon="alert"
            title="Unable to load stock action options"
            description={state.error}
            actionLabel="Try Again"
            onAction={() => setReloadKey((value) => value + 1)}
            actionTone="ghost"
          />
        ) : null}

        {!state.loading && !state.error ? (
          <>
            {!canSubmit ? (
              <div className="surface-placeholder">
                You can review this form, but only inventory operators can submit stock movements.
              </div>
            ) : null}
            <section className="workspace-card form-section">
              <div className="form-section-heading">
                <h3>Movement details</h3>
                <p>Select the item and warehouse first so the form can preview the current stock position.</p>
              </div>
              <div className="form-grid-wide">
                <label>
                  Product
                  <select className="field-input" value={form.product_id} onChange={(event) => update("product_id", event.target.value)} required>
                    <option value="">Select product</option>
                    {options.products.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Warehouse
                  <select className="field-input" value={form.warehouse_id} onChange={(event) => update("warehouse_id", event.target.value)} required>
                    <option value="">Select warehouse</option>
                    {options.warehouses.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  {config.fields.quantityLabel}
                  <input
                    className="field-input"
                    type="number"
                    step="1"
                    value={form[config.fields.quantityKey]}
                    onChange={(event) => update(config.fields.quantityKey, event.target.value)}
                    required
                  />
                </label>
                <div className="inventory-preview-card">
                  <span>Stock preview</span>
                  <strong>{stockSnapshot.loading ? "Loading…" : `${formatNumber(currentAvailable)} available now`}</strong>
                  <p>{`Projected availability after submit: ${formatNumber(resultingAvailable)}`}</p>
                </div>
              </div>
            </section>

            <section className="workspace-card form-section">
              <div className="form-section-heading">
                <h3>Tracking and reference</h3>
                <p>Attach the operational context that explains why this stock movement is being recorded.</p>
              </div>
              <div className="form-grid-wide">
                <label>
                  Reference type
                  <input className="field-input" value={form.reference_type} onChange={(event) => update("reference_type", event.target.value)} />
                </label>
                <label>
                  Reference ID
                  <input className="field-input" type="number" min="0" value={form.reference_id} onChange={(event) => update("reference_id", event.target.value)} />
                </label>
                {selectedProduct?.batch_tracking_enabled ? (
                  <label>
                    Batch number
                    <input className="field-input" value={form.batch_number} onChange={(event) => update("batch_number", event.target.value)} required={actionKey !== "adjustment"} />
                  </label>
                ) : null}
                {actionKey === "stock-in" && selectedProduct?.expiry_tracking_enabled ? (
                  <label>
                    Expiry date
                    <input className="field-input" type="date" value={form.expiry_date} onChange={(event) => update("expiry_date", event.target.value)} />
                  </label>
                ) : null}
                {actionKey === "stock-in" && selectedProduct?.warranty_tracking_enabled ? (
                  <label>
                    Warranty until
                    <input className="field-input" type="date" value={form.warranty_until} onChange={(event) => update("warranty_until", event.target.value)} />
                  </label>
                ) : null}
                {selectedProduct?.serial_tracking_enabled ? (
                  <label className="field-span-full">
                    Serial numbers
                    <textarea
                      className="field-input field-textarea"
                      value={form.serial_numbers}
                      onChange={(event) => update("serial_numbers", event.target.value)}
                      placeholder="Enter one serial per line or comma separated"
                    />
                  </label>
                ) : null}
                <label className="field-span-full">
                  Note
                  <textarea className="field-input field-textarea" value={form.note} onChange={(event) => update("note", event.target.value)} required={config.fields.noteRequired} />
                </label>
              </div>
            </section>

            <div className="workspace-card sticky-form-actions">
              <BackButton fallbackTo="/inventory/transactions" />
              <button className="ghost-button" type="button" onClick={() => setReloadKey((value) => value + 1)}>
                Refresh data
              </button>
              <button className="primary-button" type="submit" disabled={state.saving || !canSubmit}>
                {state.saving ? "Submitting…" : `Submit ${config.title}`}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
