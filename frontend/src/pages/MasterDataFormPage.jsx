import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import api from "../lib/api";

const formConfigs = {
  vendor: {
    singular: "Vendor",
    endpoint: "/vendors",
    listPath: "/vendors",
    detailPath: (id) => `/vendors/${id}`,
    fields: [
      { key: "name", label: "Vendor name", required: true },
      { key: "email", label: "Email", type: "email" },
      { key: "phone", label: "Phone" },
      { key: "gst_number", label: "GST number" },
      { key: "opening_balance", label: "Opening balance", type: "number", step: "0.01" },
      { key: "status", label: "Status", type: "select", options: ["ACTIVE", "ARCHIVED"] },
      { key: "address", label: "Address", type: "textarea", full: true },
    ],
    initialForm: {
      name: "",
      email: "",
      phone: "",
      gst_number: "",
      opening_balance: "",
      status: "ACTIVE",
      address: "",
    },
  },
  customer: {
    singular: "Customer",
    endpoint: "/customers",
    listPath: "/customers",
    detailPath: (id) => `/customers/${id}`,
    fields: [
      { key: "name", label: "Customer name", required: true },
      { key: "email", label: "Email", type: "email" },
      { key: "phone", label: "Phone" },
      { key: "gst_number", label: "GST number" },
      { key: "status", label: "Status", type: "select", options: ["ACTIVE", "ARCHIVED"] },
      { key: "billing_address", label: "Billing address", type: "textarea", full: true },
      { key: "shipping_address", label: "Shipping address", type: "textarea", full: true },
    ],
    initialForm: {
      name: "",
      email: "",
      phone: "",
      gst_number: "",
      status: "ACTIVE",
      billing_address: "",
      shipping_address: "",
    },
  },
};

export function MasterDataFormPage({ entityKey, paramKey }) {
  const navigate = useNavigate();
  const params = useParams();
  const config = formConfigs[entityKey];
  const recordId = params[paramKey];
  const isEditing = Boolean(recordId);
  const [form, setForm] = useState(config.initialForm);
  const [state, setState] = useState({ loading: isEditing, saving: false, error: "" });

  useEffect(() => {
    if (!isEditing) {
      return;
    }

    let active = true;
    api
      .get(`${config.endpoint}/${recordId}`)
      .then(({ data }) => {
        if (!active) return;
        setForm({
          ...config.initialForm,
          ...Object.fromEntries(Object.entries(data).map(([key, value]) => [key, value ?? ""])),
        });
        setState((current) => ({ ...current, loading: false }));
      })
      .catch((error) => {
        if (!active) return;
        setState({
          loading: false,
          saving: false,
          error: error?.response?.data?.detail ?? `Unable to load ${config.singular.toLowerCase()} details.`,
        });
      });

    return () => {
      active = false;
    };
  }, [config, isEditing, recordId]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, saving: true, error: "" }));

    const payload = {
      ...form,
      email: form.email || null,
      phone: form.phone || null,
      gst_number: form.gst_number || null,
      opening_balance: "opening_balance" in form ? (form.opening_balance === "" ? null : Number(form.opening_balance)) : undefined,
      address: "address" in form ? form.address || null : undefined,
      billing_address: "billing_address" in form ? form.billing_address || null : undefined,
      shipping_address: "shipping_address" in form ? form.shipping_address || null : undefined,
    };

    try {
      const response = isEditing
        ? await api.patch(`${config.endpoint}/${recordId}`, payload)
        : await api.post(config.endpoint, payload);
      navigate(config.detailPath(response.data.id));
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? `Unable to save ${config.singular.toLowerCase()}.`,
      }));
    }
  }

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Directory</p>
          <h2>{isEditing ? `Edit ${config.singular}` : `Create ${config.singular}`}</h2>
          <p>Manage core contact data and operational profile details for this record.</p>
        </div>
        <BackButton fallbackTo={config.listPath} />
      </section>

      <form className="workspace-card form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
            <div className="form-grid-wide">
              {config.fields.map((field) => (
                <label key={field.key} className={field.full ? "field-span-full" : ""}>
                  {field.label}
                  {field.type === "textarea" ? (
                    <textarea
                      className="field-input field-textarea"
                      value={form[field.key] ?? ""}
                      onChange={(event) => update(field.key, event.target.value)}
                      required={field.required}
                    />
                  ) : field.type === "select" ? (
                    <select
                      className="field-input"
                      value={form[field.key] ?? ""}
                      onChange={(event) => update(field.key, event.target.value)}
                      required={field.required}
                    >
                      {field.options.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      className="field-input"
                      type={field.type ?? "text"}
                      step={field.step}
                      value={form[field.key] ?? ""}
                      onChange={(event) => update(field.key, event.target.value)}
                      required={field.required}
                    />
                  )}
                </label>
              ))}
            </div>
            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={state.saving}>
                {state.saving ? "Saving…" : isEditing ? `Save ${config.singular}` : `Create ${config.singular}`}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
