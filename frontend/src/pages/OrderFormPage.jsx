import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../lib/api";
import { formatCurrency } from "../lib/format";

function emptyPurchaseItem() {
  return { product_id: "", warehouse_id: "", quantity_ordered: "1", unit_price: "0", tax_rate: "0" };
}

function emptySalesItem() {
  return { product_id: "", warehouse_id: "", quantity: "1", unit_price: "0", tax_rate: "0", discount: "0" };
}

export function OrderFormPage({ kind }) {
  const isPurchase = kind === "purchase";
  const { purchaseOrderId, salesOrderId } = useParams();
  const recordId = purchaseOrderId ?? salesOrderId;
  const isEditing = Boolean(recordId);
  const navigate = useNavigate();
  const [catalog, setCatalog] = useState({ products: [], warehouses: [], partners: [] });
  const [state, setState] = useState({ loading: true, saving: false, error: "" });
  const [form, setForm] = useState(
    isPurchase
      ? { vendor_id: "", po_number: "", order_date: "", expected_delivery_date: "", notes: "", items: [emptyPurchaseItem()] }
      : { customer_id: "", so_number: "", order_date: "", notes: "", items: [emptySalesItem()] },
  );

  useEffect(() => {
    let active = true;
    Promise.all([
      api.get("/products", { params: { page_size: 100 } }),
      api.get("/warehouses", { params: { page_size: 100 } }),
      api.get(isPurchase ? "/vendors" : "/customers", { params: { page_size: 100 } }),
      isEditing ? api.get(isPurchase ? `/purchase-orders/${recordId}` : `/sales-orders/${recordId}`) : Promise.resolve({ data: null }),
    ])
      .then(([products, warehouses, partners, record]) => {
        if (!active) return;
        setCatalog({
          products: products.data.items ?? [],
          warehouses: warehouses.data.items ?? [],
          partners: partners.data.items ?? [],
        });
        if (record.data) {
          setForm({
            ...record.data,
            vendor_id: record.data.vendor_id ?? "",
            customer_id: record.data.customer_id ?? "",
            expected_delivery_date: record.data.expected_delivery_date ?? "",
            items: record.data.items?.length ? record.data.items.map((item) => ({ ...item })) : [isPurchase ? emptyPurchaseItem() : emptySalesItem()],
          });
        } else {
          setForm((current) => ({
            ...current,
            order_date: new Date().toISOString().slice(0, 10),
          }));
        }
        setState((current) => ({ ...current, loading: false }));
      })
      .catch((error) => {
        if (!active) return;
        setState({ loading: false, saving: false, error: error?.response?.data?.detail ?? "Unable to prepare the order builder." });
      });
    return () => {
      active = false;
    };
  }, [isEditing, isPurchase, recordId]);

  const totals = useMemo(() => {
    return form.items.reduce(
      (accumulator, item) => {
        const quantity = Number(isPurchase ? item.quantity_ordered : item.quantity);
        const price = Number(item.unit_price);
        const taxRate = Number(item.tax_rate);
        const discount = Number(item.discount ?? 0);
        const subtotal = quantity * price;
        const tax = subtotal * (taxRate / 100);
        accumulator.subtotal += subtotal;
        accumulator.tax += tax;
        accumulator.discount += discount;
        accumulator.total += subtotal + tax - discount;
        return accumulator;
      },
      { subtotal: 0, tax: 0, discount: 0, total: 0 },
    );
  }, [form.items, isPurchase]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function updateItem(index, field, value) {
    setForm((current) => ({
      ...current,
      items: current.items.map((item, itemIndex) => (itemIndex === index ? { ...item, [field]: value } : item)),
    }));
  }

  function addItem() {
    setForm((current) => ({
      ...current,
      items: [...current.items, isPurchase ? emptyPurchaseItem() : emptySalesItem()],
    }));
  }

  function removeItem(index) {
    setForm((current) => ({
      ...current,
      items: current.items.filter((_, itemIndex) => itemIndex !== index),
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, saving: true, error: "" }));
    const payload = isPurchase
      ? {
          vendor_id: Number(form.vendor_id),
          po_number: form.po_number,
          order_date: form.order_date,
          expected_delivery_date: form.expected_delivery_date || null,
          notes: form.notes || null,
          items: form.items.map((item) => ({
            product_id: Number(item.product_id),
            warehouse_id: Number(item.warehouse_id),
            quantity_ordered: Number(item.quantity_ordered),
            unit_price: Number(item.unit_price),
            tax_rate: Number(item.tax_rate),
          })),
        }
      : {
          customer_id: Number(form.customer_id),
          so_number: form.so_number,
          order_date: form.order_date,
          notes: form.notes || null,
          items: form.items.map((item) => ({
            product_id: Number(item.product_id),
            warehouse_id: Number(item.warehouse_id),
            quantity: Number(item.quantity),
            unit_price: Number(item.unit_price),
            tax_rate: Number(item.tax_rate),
            discount: Number(item.discount),
          })),
        };

    try {
      const response = isEditing
        ? await api.patch(isPurchase ? `/purchase-orders/${recordId}` : `/sales-orders/${recordId}`, payload)
        : await api.post(isPurchase ? "/purchase-orders" : "/sales-orders", payload);
      navigate(isPurchase ? `/purchase-orders/${response.data.id}` : `/sales-orders/${response.data.id}`);
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to save this order.",
      }));
    }
  }

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">{isPurchase ? "Inbound Workflow" : "Sales Workflow"}</p>
          <h2>{isEditing ? `Edit ${isPurchase ? "Purchase" : "Sales"} Order` : `Create ${isPurchase ? "Purchase" : "Sales"} Order`}</h2>
          <p>Build line items with a lightweight SaaS editor designed for daily operations.</p>
        </div>
      </section>

      <form className="workspace-card form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading order form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
            <div className="form-grid-wide">
              <label>
                {isPurchase ? "Vendor" : "Customer"}
                <select
                  className="field-input"
                  value={isPurchase ? form.vendor_id : form.customer_id}
                  onChange={(event) => update(isPurchase ? "vendor_id" : "customer_id", event.target.value)}
                  required
                >
                  <option value="">Select {isPurchase ? "vendor" : "customer"}</option>
                  {catalog.partners.map((option) => (
                    <option key={option.id} value={option.id}>
                      {option.name}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                {isPurchase ? "PO number" : "SO number"}
                <input
                  className="field-input"
                  value={isPurchase ? form.po_number : form.so_number}
                  onChange={(event) => update(isPurchase ? "po_number" : "so_number", event.target.value)}
                  required
                />
              </label>

              <label>
                Order date
                <input className="field-input" type="date" value={form.order_date} onChange={(event) => update("order_date", event.target.value)} required />
              </label>

              {isPurchase ? (
                <label>
                  Expected delivery
                  <input className="field-input" type="date" value={form.expected_delivery_date} onChange={(event) => update("expected_delivery_date", event.target.value)} />
                </label>
              ) : null}

              <label className="field-span-full">
                Notes
                <textarea className="field-input field-textarea" value={form.notes ?? ""} onChange={(event) => update("notes", event.target.value)} />
              </label>
            </div>

            <div className="card-header-row">
              <h3>Line items</h3>
              <button className="ghost-button" type="button" onClick={addItem}>
                Add Row
              </button>
            </div>

            <div className="line-items-stack">
              {form.items.map((item, index) => (
                <div className="line-item-card" key={`${index}-${item.product_id}-${item.warehouse_id}`}>
                  <div className="line-item-grid">
                    <label>
                      Product
                      <select className="field-input" value={item.product_id} onChange={(event) => updateItem(index, "product_id", event.target.value)} required>
                        <option value="">Select product</option>
                        {catalog.products.map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Warehouse
                      <select className="field-input" value={item.warehouse_id} onChange={(event) => updateItem(index, "warehouse_id", event.target.value)} required>
                        <option value="">Select warehouse</option>
                        {catalog.warehouses.map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Quantity
                      <input
                        className="field-input"
                        type="number"
                        min="1"
                        step="1"
                        value={isPurchase ? item.quantity_ordered : item.quantity}
                        onChange={(event) => updateItem(index, isPurchase ? "quantity_ordered" : "quantity", event.target.value)}
                        required
                      />
                    </label>
                    <label>
                      Unit price
                      <input className="field-input" type="number" min="0" step="0.01" value={item.unit_price} onChange={(event) => updateItem(index, "unit_price", event.target.value)} required />
                    </label>
                    <label>
                      Tax %
                      <input className="field-input" type="number" min="0" step="0.01" value={item.tax_rate} onChange={(event) => updateItem(index, "tax_rate", event.target.value)} />
                    </label>
                    {!isPurchase ? (
                      <label>
                        Discount
                        <input className="field-input" type="number" min="0" step="0.01" value={item.discount} onChange={(event) => updateItem(index, "discount", event.target.value)} />
                      </label>
                    ) : null}
                  </div>
                  {form.items.length > 1 ? (
                    <button className="inline-link danger-link" type="button" onClick={() => removeItem(index)}>
                      Remove row
                    </button>
                  ) : null}
                </div>
              ))}
            </div>

            <div className="totals-strip">
              <span>Subtotal {formatCurrency(totals.subtotal)}</span>
              <span>Tax {formatCurrency(totals.tax)}</span>
              {!isPurchase ? <span>Discount {formatCurrency(totals.discount)}</span> : null}
              <strong>Total {formatCurrency(totals.total)}</strong>
            </div>

            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={state.saving}>
                {state.saving ? "Saving…" : isEditing ? "Save Order" : "Create Order"}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
