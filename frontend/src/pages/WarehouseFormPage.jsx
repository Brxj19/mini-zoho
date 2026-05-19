import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import api from "../lib/api";

const initialForm = {
  name: "",
  code: "",
  address: "",
  city: "",
  state: "",
  country: "India",
  manager_name: "",
  phone: "",
  is_default: false,
  status: "ACTIVE",
};

export function WarehouseFormPage() {
  const navigate = useNavigate();
  const { warehouseId } = useParams();
  const isEditing = Boolean(warehouseId);
  const [form, setForm] = useState(initialForm);
  const [state, setState] = useState({ loading: isEditing, saving: false, error: "" });

  useEffect(() => {
    if (!isEditing) {
      return;
    }

    let active = true;
    api
      .get(`/warehouses/${warehouseId}`)
      .then(({ data }) => {
        if (!active) return;
        setForm({
          ...initialForm,
          ...Object.fromEntries(Object.entries(data).map(([key, value]) => [key, value ?? ""])),
          is_default: Boolean(data.is_default),
        });
        setState((current) => ({ ...current, loading: false }));
      })
      .catch((error) => {
        if (!active) return;
        setState({
          loading: false,
          saving: false,
          error: error?.response?.data?.detail ?? "Unable to load warehouse details.",
        });
      });

    return () => {
      active = false;
    };
  }, [isEditing, warehouseId]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, saving: true, error: "" }));

    const payload = {
      ...form,
      address: form.address || null,
      city: form.city || null,
      state: form.state || null,
      country: form.country || null,
      manager_name: form.manager_name || null,
      phone: form.phone || null,
      is_default: Boolean(form.is_default),
    };

    try {
      const response = isEditing
        ? await api.patch(`/warehouses/${warehouseId}`, payload)
        : await api.post("/warehouses", payload);
      navigate(`/warehouses/${response.data.id}`);
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to save warehouse.",
      }));
    }
  }

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Inventory Location</p>
          <h2>{isEditing ? "Edit Warehouse" : "Create Warehouse"}</h2>
          <p>Configure fulfillment location details, warehouse ownership, and primary-site behavior.</p>
        </div>
        <BackButton fallbackTo={isEditing ? `/warehouses/${warehouseId}` : "/warehouses"} />
      </section>

      <form className="workspace-card form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading warehouse form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
            <div className="form-grid-wide">
              <label>
                Warehouse name
                <input className="field-input" value={form.name} onChange={(event) => update("name", event.target.value)} required />
              </label>
              <label>
                Code
                <input className="field-input" value={form.code} onChange={(event) => update("code", event.target.value)} required />
              </label>
              <label>
                City
                <input className="field-input" value={form.city} onChange={(event) => update("city", event.target.value)} />
              </label>
              <label>
                State
                <input className="field-input" value={form.state} onChange={(event) => update("state", event.target.value)} />
              </label>
              <label>
                Country
                <input className="field-input" value={form.country} onChange={(event) => update("country", event.target.value)} />
              </label>
              <label>
                Manager name
                <input className="field-input" value={form.manager_name} onChange={(event) => update("manager_name", event.target.value)} />
              </label>
              <label>
                Phone
                <input className="field-input" value={form.phone} onChange={(event) => update("phone", event.target.value)} />
              </label>
              <label>
                Status
                <select className="field-input" value={form.status} onChange={(event) => update("status", event.target.value)}>
                  <option value="ACTIVE">Active</option>
                  <option value="ARCHIVED">Archived</option>
                </select>
              </label>
              <label className="field-span-full">
                Address
                <textarea className="field-input field-textarea" value={form.address} onChange={(event) => update("address", event.target.value)} />
              </label>
              <label className="field-span-full checkbox-row">
                <input type="checkbox" checked={Boolean(form.is_default)} onChange={(event) => update("is_default", event.target.checked)} />
                <span>Set as default warehouse</span>
              </label>
            </div>
            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={state.saving}>
                {state.saving ? "Saving…" : isEditing ? "Save Warehouse" : "Create Warehouse"}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
