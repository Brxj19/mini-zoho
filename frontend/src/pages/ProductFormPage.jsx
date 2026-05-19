import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
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
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Catalog</p>
          <h2>{isEditing ? "Edit Item" : "Create Item"}</h2>
          <p>Set up item details, pricing, and replenishment controls in one clean workflow.</p>
        </div>
        <BackButton fallbackTo={isEditing ? `/items/${productId}` : "/items"} />
      </section>

      <form className="workspace-card form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading product form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
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
                <input className="field-input" value={form.barcode} onChange={(event) => update("barcode", event.target.value)} />
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
              <label>
                Vendor
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
              <label>
                Cost price
                <input className="field-input" type="number" min="0" step="0.01" value={form.cost_price} onChange={(event) => update("cost_price", event.target.value)} />
              </label>
              <label>
                Selling price
                <input className="field-input" type="number" min="0" step="0.01" value={form.selling_price} onChange={(event) => update("selling_price", event.target.value)} />
              </label>
              <label>
                Reorder level
                <input className="field-input" type="number" min="0" step="1" value={form.reorder_level} onChange={(event) => update("reorder_level", event.target.value)} />
              </label>
              <label className="field-span-full">
                Description
                <textarea className="field-input field-textarea" value={form.description} onChange={(event) => update("description", event.target.value)} />
              </label>
            </div>
            <div className="form-actions">
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
