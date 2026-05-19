import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import { PageHeader } from "../components/PageHeader";
import api from "../lib/api";

const initialForm = {
  name: "",
  sku: "",
  barcode: "",
  category_id: "",
  brand_id: "",
  vendor_id: "",
  description: "",
  unit: "unit",
  cost_price: "0",
  selling_price: "0",
  reorder_level: "0",
  serial_tracking_enabled: false,
  batch_tracking_enabled: false,
  expiry_tracking_enabled: false,
  warranty_tracking_enabled: false,
  status: "ACTIVE",
};

export function ProductFormPage() {
  const navigate = useNavigate();
  const { productId } = useParams();
  const isEditing = Boolean(productId);
  const [form, setForm] = useState(initialForm);
  const [catalog, setCatalog] = useState({ categories: [], brands: [], vendors: [] });
  const [state, setState] = useState({ loading: isEditing, saving: false, error: "" });

  useEffect(() => {
    let active = true;
    Promise.all([
      api.get("/categories", { params: { page_size: 100 } }),
      api.get("/brands", { params: { page_size: 100 } }),
      api.get("/vendors", { params: { page_size: 100 } }),
      isEditing ? api.get(`/products/${productId}`) : Promise.resolve({ data: null }),
    ])
      .then(([categories, brands, vendors, product]) => {
        if (!active) return;
        setCatalog({
          categories: categories.data.items ?? [],
          brands: brands.data.items ?? [],
          vendors: vendors.data.items ?? [],
        });
        if (product.data) {
          setForm({
            ...initialForm,
            ...Object.fromEntries(Object.entries(product.data).map(([key, value]) => [key, value ?? ""])),
          });
        }
        setState((current) => ({ ...current, loading: false }));
      })
      .catch((error) => {
        if (!active) return;
        setState({ loading: false, saving: false, error: error?.response?.data?.detail ?? "Unable to prepare the form." });
      });

    return () => {
      active = false;
    };
  }, [isEditing, productId]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, saving: true, error: "" }));
    const payload = {
      ...form,
      category_id: form.category_id ? Number(form.category_id) : null,
      brand_id: form.brand_id ? Number(form.brand_id) : null,
      vendor_id: form.vendor_id ? Number(form.vendor_id) : null,
      cost_price: Number(form.cost_price),
      selling_price: Number(form.selling_price),
      reorder_level: Number(form.reorder_level),
      serial_tracking_enabled: Boolean(form.serial_tracking_enabled),
      batch_tracking_enabled: Boolean(form.batch_tracking_enabled),
      expiry_tracking_enabled: Boolean(form.expiry_tracking_enabled),
      warranty_tracking_enabled: Boolean(form.warranty_tracking_enabled),
      barcode: form.barcode || null,
      description: form.description || null,
    };

    try {
      const response = isEditing ? await api.patch(`/products/${productId}`, payload) : await api.post("/products", payload);
      navigate(`/items/${response.data.id}`);
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to save product.",
      }));
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Inventory Catalog"
        title={isEditing ? "Edit Item" : "Create Item"}
        description="Capture item identity, pricing, purchasing context, and tracking controls in one structured workflow."
        backTo={isEditing ? `/items/${productId}` : "/items"}
      />

      <form className="form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading product form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
            <section className="workspace-card form-section">
              <div className="form-section-heading">
                <h3>Primary Details</h3>
                <p>Define the core identity and catalog structure for this item.</p>
              </div>
              <div className="form-grid-wide">
                <label>
                  Item name
                  <input className="field-input" value={form.name} onChange={(event) => update("name", event.target.value)} required />
                </label>
                <label>
                  SKU
                  <input className="field-input" value={form.sku} onChange={(event) => update("sku", event.target.value)} required />
                </label>
                <label>
                  Barcode
                  <div className="stacked-inline">
                    <input className="field-input" value={form.barcode} onChange={(event) => update("barcode", event.target.value)} />
                    <button
                      className="ghost-button compact-button"
                      type="button"
                      onClick={async () => {
                        try {
                          const response = await api.get("/inventory/barcode/generate");
                          update("barcode", response.data.barcode);
                          setState((current) => ({ ...current, error: "" }));
                        } catch (error) {
                          setState((current) => ({
                            ...current,
                            error: error?.response?.data?.detail ?? "Unable to generate a barcode.",
                          }));
                        }
                      }}
                    >
                      Generate
                    </button>
                  </div>
                </label>
                <label>
                  Unit
                  <input className="field-input" value={form.unit} onChange={(event) => update("unit", event.target.value)} />
                </label>
                <label>
                  Category
                  <select className="field-input" value={form.category_id} onChange={(event) => update("category_id", event.target.value)}>
                    <option value="">Select category</option>
                    {catalog.categories.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Brand
                  <select className="field-input" value={form.brand_id} onChange={(event) => update("brand_id", event.target.value)}>
                    <option value="">Select brand</option>
                    {catalog.brands.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="field-span-full">
                  Product image
                  <div className="surface-placeholder">Image upload is reserved for a future media enhancement without changing the item form structure again.</div>
                </label>
              </div>
            </section>

            <section className="workspace-card form-section">
              <div className="form-section-heading">
                <h3>Sales and Purchase Information</h3>
                <p>Set pricing and supplier context used across sales and procurement workflows.</p>
              </div>
              <div className="form-grid-wide">
                <label>
                  Selling price
                  <input className="field-input" type="number" min="0" step="0.01" value={form.selling_price} onChange={(event) => update("selling_price", event.target.value)} />
                </label>
                <label>
                  Cost price
                  <input className="field-input" type="number" min="0" step="0.01" value={form.cost_price} onChange={(event) => update("cost_price", event.target.value)} />
                </label>
                <label>
                  Preferred vendor
                  <select className="field-input" value={form.vendor_id} onChange={(event) => update("vendor_id", event.target.value)}>
                    <option value="">Select vendor</option>
                    {catalog.vendors.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Status
                  <select className="field-input" value={form.status} onChange={(event) => update("status", event.target.value)}>
                    <option value="ACTIVE">Active</option>
                    <option value="ARCHIVED">Archived</option>
                  </select>
                </label>
                <label className="field-span-full">
                  Description
                  <textarea className="field-input field-textarea" value={form.description} onChange={(event) => update("description", event.target.value)} />
                </label>
              </div>
            </section>

            <section className="workspace-card form-section">
              <div className="form-section-heading">
                <h3>Inventory Tracking</h3>
                <p>Control replenishment thresholds and advanced tracking modes for operational traceability.</p>
              </div>
              <div className="form-grid-wide">
                <label>
                  Reorder level
                  <input className="field-input" type="number" min="0" step="1" value={form.reorder_level} onChange={(event) => update("reorder_level", event.target.value)} />
                </label>
                <label>
                  Opening stock
                  <div className="surface-placeholder">Opening stock is posted through stock-in after the item is created so every movement remains auditable.</div>
                </label>
                <label className="checkbox-row">
                  <input type="checkbox" checked={form.serial_tracking_enabled} onChange={(event) => update("serial_tracking_enabled", event.target.checked)} />
                  Enable serial tracking
                </label>
                <label className="checkbox-row">
                  <input type="checkbox" checked={form.batch_tracking_enabled} onChange={(event) => update("batch_tracking_enabled", event.target.checked)} />
                  Enable batch tracking
                </label>
                <label className="checkbox-row">
                  <input type="checkbox" checked={form.expiry_tracking_enabled} onChange={(event) => update("expiry_tracking_enabled", event.target.checked)} />
                  Track expiry dates
                </label>
                <label className="checkbox-row">
                  <input type="checkbox" checked={form.warranty_tracking_enabled} onChange={(event) => update("warranty_tracking_enabled", event.target.checked)} />
                  Track warranty dates
                </label>
              </div>
            </section>

            <section className="workspace-card form-section">
              <div className="form-section-heading">
                <h3>Dimensions and Codes</h3>
                <p>Reserved for richer catalog metadata such as UPC, EAN, MPN, and dimensional data.</p>
              </div>
              <div className="surface-placeholder">Additional dimensions, tax preferences, and code systems can plug into this section without disrupting the core inventory form.</div>
            </section>

            <div className="workspace-card sticky-form-actions">
              <BackButton fallbackTo={isEditing ? `/items/${productId}` : "/items"} />
              <button className="ghost-button" type="button" onClick={() => navigate(isEditing ? `/items/${productId}` : "/items")}>
                Cancel
              </button>
              <button className="primary-button" type="submit" disabled={state.saving}>
                {state.saving ? "Saving…" : isEditing ? "Save Item" : "Create Item"}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
