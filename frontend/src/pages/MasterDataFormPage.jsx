import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import api from "../lib/api";

const formConfigs = {
  category: {
    singular: "Category",
    eyebrow: "Inventory Taxonomy",
    description: "Organize items into commercial categories so downstream inventory and reporting screens stay structured.",
    endpoint: "/categories",
    listPath: "/categories",
    detailPath: (id) => `/categories/${id}`,
    primaryFields: [
      { key: "name", label: "Category name", required: true },
      { key: "status", label: "Status", type: "select", options: ["ACTIVE", "ARCHIVED"] },
    ],
    secondaryFields: [{ key: "description", label: "Description", type: "textarea", full: true }],
    initialForm: { name: "", status: "ACTIVE", description: "" },
  },
  brand: {
    singular: "Brand",
    eyebrow: "Inventory Taxonomy",
    description: "Keep the catalog brand-aware so stock, purchasing, and selling views can stay consistent.",
    endpoint: "/brands",
    listPath: "/brands",
    detailPath: (id) => `/brands/${id}`,
    primaryFields: [
      { key: "name", label: "Brand name", required: true },
      { key: "status", label: "Status", type: "select", options: ["ACTIVE", "ARCHIVED"] },
    ],
    secondaryFields: [{ key: "description", label: "Description", type: "textarea", full: true }],
    initialForm: { name: "", status: "ACTIVE", description: "" },
  },
  vendor: {
    singular: "Vendor",
    eyebrow: "Purchase Directory",
    description: "Maintain procurement-ready vendor profiles with tax, contact, and payable-friendly details.",
    endpoint: "/vendors",
    listPath: "/vendors",
    detailPath: (id) => `/vendors/${id}`,
    primaryFields: [
      { key: "name", label: "Vendor name", required: true },
      { key: "email", label: "Email", type: "email" },
      { key: "phone", label: "Phone" },
      { key: "status", label: "Status", type: "select", options: ["ACTIVE", "ARCHIVED"] },
    ],
    secondaryFields: [
      { key: "gst_number", label: "GST number" },
      { key: "opening_balance", label: "Opening balance", type: "number", step: "0.01" },
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
    eyebrow: "Sales Directory",
    description: "Build customer records that can flow directly into orders, invoices, returns, and delivery operations.",
    endpoint: "/customers",
    listPath: "/customers",
    detailPath: (id) => `/customers/${id}`,
    primaryFields: [
      { key: "name", label: "Customer name", required: true },
      { key: "email", label: "Email", type: "email" },
      { key: "phone", label: "Phone" },
      { key: "status", label: "Status", type: "select", options: ["ACTIVE", "ARCHIVED"] },
    ],
    secondaryFields: [
      { key: "gst_number", label: "GST number" },
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

function renderField(field, value, update) {
  if (field.type === "textarea") {
    return (
      <textarea
        className="field-input field-textarea"
        value={value ?? ""}
        onChange={(event) => update(field.key, event.target.value)}
        required={field.required}
      />
    );
  }

  if (field.type === "select") {
    return (
      <select className="field-input" value={value ?? ""} onChange={(event) => update(field.key, event.target.value)} required={field.required}>
        {field.options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    );
  }

  return (
    <input
      className="field-input"
      type={field.type ?? "text"}
      step={field.step}
      value={value ?? ""}
      onChange={(event) => update(field.key, event.target.value)}
      required={field.required}
    />
  );
}

export function MasterDataFormPage({ entityKey, paramKey }) {
  const navigate = useNavigate();
  const params = useParams();
  const config = formConfigs[entityKey];
  const recordId = params[paramKey];
  const isEditing = Boolean(recordId);
  const [form, setForm] = useState(config.initialForm);
  const [state, setState] = useState({ loading: isEditing, saving: false, error: "" });

  useEffect(() => {
    if (!isEditing) return;

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
      description: "description" in form ? form.description || null : undefined,
      address: "address" in form ? form.address || null : undefined,
      billing_address: "billing_address" in form ? form.billing_address || null : undefined,
      shipping_address: "shipping_address" in form ? form.shipping_address || null : undefined,
    };

    try {
      const response = isEditing ? await api.patch(`${config.endpoint}/${recordId}`, payload) : await api.post(config.endpoint, payload);
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
    <div className="page-stack">
      <PageHeader
        eyebrow={config.eyebrow}
        title={isEditing ? `Edit ${config.singular}` : `Create ${config.singular}`}
        description={config.description}
        backTo={isEditing ? config.detailPath(recordId) : config.listPath}
      />

      <form className="form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="workspace-card surface-placeholder">Loading form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
            <section className="form-section">
              <div className="form-section-heading">
                <h3>Primary details</h3>
                <p>Capture the core operational identity and active status for this record.</p>
              </div>
              <div className="form-grid-wide">
                {config.primaryFields.map((field) => (
                  <label key={field.key} className={field.full ? "field-span-full" : ""}>
                    {field.label}
                    {renderField(field, form[field.key], update)}
                  </label>
                ))}
              </div>
            </section>

            <section className="form-section">
              <div className="form-section-heading">
                <h3>{entityKey === "vendor" || entityKey === "customer" ? "Commercial and address details" : "Additional context"}</h3>
                <p>{entityKey === "vendor" || entityKey === "customer" ? "Keep tax, address, and balance context ready for downstream workflows." : "Add helpful descriptive context for inventory organization and search."}</p>
              </div>
              <div className="form-grid-wide">
                {config.secondaryFields.map((field) => (
                  <label key={field.key} className={field.full ? "field-span-full" : ""}>
                    {field.label}
                    {renderField(field, form[field.key], update)}
                  </label>
                ))}
              </div>
            </section>

            <div className="sticky-form-actions">
              <button className="button button-ghost" type="button" onClick={() => navigate(isEditing ? config.detailPath(recordId) : config.listPath)}>
                Cancel
              </button>
              <button className="button button-primary" type="submit" disabled={state.saving}>
                {state.saving ? "Saving…" : isEditing ? `Save ${config.singular}` : `Create ${config.singular}`}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
