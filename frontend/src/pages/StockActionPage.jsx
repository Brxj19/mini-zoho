import { useEffect, useState } from "react";

import { BackButton } from "../components/BackButton";
import api from "../lib/api";

const actionConfig = {
  "stock-in": {
    title: "Stock In",
    description: "Record inbound stock against a warehouse and create a transaction log entry.",
    endpoint: "/inventory/stock-in",
    fields: { quantityLabel: "Quantity", quantityKey: "quantity", noteRequired: false },
  },
  "stock-out": {
    title: "Stock Out",
    description: "Ship inventory out while preserving a complete stock movement record.",
    endpoint: "/inventory/stock-out",
    fields: { quantityLabel: "Quantity", quantityKey: "quantity", noteRequired: false },
  },
  adjustment: {
    title: "Stock Adjustment",
    description: "Apply a counted correction with a required operational note.",
    endpoint: "/inventory/adjust",
    fields: { quantityLabel: "Quantity Delta", quantityKey: "quantity_delta", noteRequired: true },
  },
};

export function StockActionPage({ actionKey }) {
  const config = actionConfig[actionKey];
  const [options, setOptions] = useState({ products: [], warehouses: [] });
  const [form, setForm] = useState({
    product_id: "",
    warehouse_id: "",
    quantity: "1",
    quantity_delta: "0",
    note: "",
    reference_type: "",
    reference_id: "",
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
  }, []);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

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
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Inventory Action</p>
          <h2>{config.title}</h2>
          <p>{config.description}</p>
        </div>
        <BackButton fallbackTo="/inventory/transactions" />
      </section>
      <form className="workspace-card form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading action form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}
        {state.success ? <div className="surface-success">{state.success}</div> : null}

        {!state.loading ? (
          <>
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
              <label>
                Reference type
                <input className="field-input" value={form.reference_type} onChange={(event) => update("reference_type", event.target.value)} />
              </label>
              <label>
                Reference ID
                <input className="field-input" type="number" min="0" value={form.reference_id} onChange={(event) => update("reference_id", event.target.value)} />
              </label>
              <label className="field-span-full">
                Note
                <textarea className="field-input field-textarea" value={form.note} onChange={(event) => update("note", event.target.value)} required={config.fields.noteRequired} />
              </label>
            </div>
            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={state.saving}>
                {state.saving ? "Submitting…" : `Submit ${config.title}`}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
