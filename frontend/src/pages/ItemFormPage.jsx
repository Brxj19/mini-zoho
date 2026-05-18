import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../lib/api";
import { FormRow } from "../components/FormRow";
import { FormSection } from "../components/FormSection";
import { PageHeader } from "../components/PageHeader";

export function ItemFormPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formState, setFormState] = useState({
    type: "Goods",
    name: "Mysuru Cane Accent Chair",
    sku: "NST-OFC-106",
    unit: "pcs",
    category: "Office Furniture",
    brand: "Northstar",
    returnable: true,
    sellingPrice: "199",
    costPrice: "132",
    salesDescription: "Ergonomic chair with breathable mesh back.",
    purchaseDescription: "Import pack with standard hardware kit.",
    trackInventory: true,
    openingStock: "124",
    reorderPoint: "32",
    barcode: "8901234567001",
    upc: "",
    ean: "",
    mpn: "",
    isbn: "",
    length: "",
    width: "",
    height: "",
    weight: "",
  });

  async function saveItem(shouldReset = false) {
    setError("");
    setIsSubmitting(true);
    try {
      await api.post("/app/items", {
        name: formState.name,
        sku: formState.sku,
        category_name: formState.category,
        brand_name: formState.brand,
        unit: formState.unit,
        barcode: formState.barcode || null,
        selling_price: Number(formState.sellingPrice),
        cost_price: Number(formState.costPrice),
        stock_on_hand: Number(formState.openingStock),
        reorder_level: Number(formState.reorderPoint),
        sales_description: formState.salesDescription,
        purchase_description: formState.purchaseDescription,
      });

      if (shouldReset) {
        setFormState((state) => ({
          ...state,
          name: "",
          sku: "",
          barcode: "",
          sellingPrice: "",
          costPrice: "",
          openingStock: "",
          reorderPoint: "",
          salesDescription: "",
          purchaseDescription: "",
        }));
        return;
      }

      navigate("/items");
    } catch (requestError) {
      setError(requestError.response?.data?.detail ?? "Unable to save the item right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Items"
        title="New Item"
        description="Professional item setup with grouped sections, inventory controls, and future-ready tracking placeholders."
      />

      <form className="form-shell">
        <FormSection title="Primary Details" description="Set the core catalog identity for this item.">
          <FormRow>
            <label>
              Type
              <select value={formState.type} onChange={(event) => setFormState((state) => ({ ...state, type: event.target.value }))}>
                <option>Goods</option>
                <option>Service</option>
              </select>
            </label>
            <label>
              Name
              <input value={formState.name} onChange={(event) => setFormState((state) => ({ ...state, name: event.target.value }))} />
            </label>
          </FormRow>

          <FormRow>
            <label>
              SKU
              <input value={formState.sku} onChange={(event) => setFormState((state) => ({ ...state, sku: event.target.value }))} />
            </label>
            <label>
              Unit
              <input value={formState.unit} onChange={(event) => setFormState((state) => ({ ...state, unit: event.target.value }))} />
            </label>
          </FormRow>

          <FormRow>
            <label>
              Category
              <input value={formState.category} onChange={(event) => setFormState((state) => ({ ...state, category: event.target.value }))} />
            </label>
            <label>
              Brand
              <input value={formState.brand} onChange={(event) => setFormState((state) => ({ ...state, brand: event.target.value }))} />
            </label>
          </FormRow>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={formState.returnable}
              onChange={(event) => setFormState((state) => ({ ...state, returnable: event.target.checked }))}
            />
            Returnable item
          </label>

          <div className="upload-placeholder">Product image placeholder</div>
        </FormSection>

        <FormSection title="Sales and Purchase Information">
          <FormRow>
            <label>
              Selling price
              <input value={formState.sellingPrice} onChange={(event) => setFormState((state) => ({ ...state, sellingPrice: event.target.value }))} />
            </label>
            <label>
              Cost price
              <input value={formState.costPrice} onChange={(event) => setFormState((state) => ({ ...state, costPrice: event.target.value }))} />
            </label>
          </FormRow>

          <label>
            Sales description
            <textarea value={formState.salesDescription} onChange={(event) => setFormState((state) => ({ ...state, salesDescription: event.target.value }))} />
          </label>

          <label>
            Purchase description
            <textarea value={formState.purchaseDescription} onChange={(event) => setFormState((state) => ({ ...state, purchaseDescription: event.target.value }))} />
          </label>

          <label>
            Tax preference
            <input value="Placeholder until tax module exists" readOnly />
          </label>
        </FormSection>

        <FormSection title="Inventory Tracking">
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={formState.trackInventory}
              onChange={(event) => setFormState((state) => ({ ...state, trackInventory: event.target.checked }))}
            />
            Track inventory
          </label>

          <FormRow>
            <label>
              Warehouse opening stock
              <input value={formState.openingStock} onChange={(event) => setFormState((state) => ({ ...state, openingStock: event.target.value }))} />
            </label>
            <label>
              Reorder point
              <input value={formState.reorderPoint} onChange={(event) => setFormState((state) => ({ ...state, reorderPoint: event.target.value }))} />
            </label>
          </FormRow>

          <FormRow>
            <label>
              Barcode
              <input value={formState.barcode} onChange={(event) => setFormState((state) => ({ ...state, barcode: event.target.value }))} />
            </label>
            <label>
              Serial / batch tracking
              <input value="Placeholder until advanced inventory tracking exists" readOnly />
            </label>
          </FormRow>
        </FormSection>

        <FormSection title="Dimensions and Codes Placeholder">
          <FormRow columns={4}>
            <label>
              UPC
              <input value={formState.upc} onChange={(event) => setFormState((state) => ({ ...state, upc: event.target.value }))} />
            </label>
            <label>
              EAN
              <input value={formState.ean} onChange={(event) => setFormState((state) => ({ ...state, ean: event.target.value }))} />
            </label>
            <label>
              MPN
              <input value={formState.mpn} onChange={(event) => setFormState((state) => ({ ...state, mpn: event.target.value }))} />
            </label>
            <label>
              ISBN
              <input value={formState.isbn} onChange={(event) => setFormState((state) => ({ ...state, isbn: event.target.value }))} />
            </label>
          </FormRow>

          <FormRow columns={4}>
            <label>
              Length
              <input value={formState.length} onChange={(event) => setFormState((state) => ({ ...state, length: event.target.value }))} />
            </label>
            <label>
              Width
              <input value={formState.width} onChange={(event) => setFormState((state) => ({ ...state, width: event.target.value }))} />
            </label>
            <label>
              Height
              <input value={formState.height} onChange={(event) => setFormState((state) => ({ ...state, height: event.target.value }))} />
            </label>
            <label>
              Weight
              <input value={formState.weight} onChange={(event) => setFormState((state) => ({ ...state, weight: event.target.value }))} />
            </label>
          </FormRow>
        </FormSection>

        <div className="sticky-form-bar">
          <div className="sticky-form-actions">
            {error ? <div className="form-error">{error}</div> : null}
            <button className="button button-primary" type="button" disabled={isSubmitting} onClick={() => saveItem(false)}>
              Save
            </button>
            <button className="button button-secondary" type="button" disabled={isSubmitting} onClick={() => saveItem(true)}>
              Save and New
            </button>
            <Link className="button button-ghost" to="/items">
              Cancel
            </Link>
          </div>
        </div>
      </form>
    </div>
  );
}
