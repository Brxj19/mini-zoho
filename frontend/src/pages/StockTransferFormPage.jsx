import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import { StatusBadge } from "../components/StatusBadge";
import api from "../lib/api";

function emptyTransferItem() {
  return { product_id: "", quantity: "1" };
}

const initialForm = {
  source_warehouse_id: "",
  destination_warehouse_id: "",
  notes: "",
  items: [emptyTransferItem()],
};

export function StockTransferFormPage() {
  const navigate = useNavigate();
  const { transferId } = useParams();
  const isEditing = Boolean(transferId);
  const [catalog, setCatalog] = useState({ products: [], warehouses: [] });
  const [form, setForm] = useState(initialForm);
  const [recordStatus, setRecordStatus] = useState("");
  const [state, setState] = useState({
    loading: true,
    saving: false,
    error: "",
  });

  useEffect(() => {
    let active = true;

    Promise.all([
      api.get("/products", { params: { page_size: 100 } }),
      api.get("/warehouses", { params: { page_size: 100 } }),
      isEditing ? api.get(`/inventory/transfers/${transferId}`) : Promise.resolve({ data: null }),
    ])
      .then(([products, warehouses, record]) => {
        if (!active) return;

        setCatalog({
          products: products.data.items ?? [],
          warehouses: warehouses.data.items ?? [],
        });

        if (record.data) {
          setForm({
            source_warehouse_id: String(record.data.source_warehouse_id ?? ""),
            destination_warehouse_id: String(record.data.destination_warehouse_id ?? ""),
            notes: record.data.notes ?? "",
            items: record.data.items?.length
              ? record.data.items.map((item) => ({
                  product_id: String(item.product_id ?? ""),
                  quantity: String(item.quantity ?? 1),
                }))
              : [emptyTransferItem()],
          });
          setRecordStatus(record.data.status ?? "");
        }

        setState({ loading: false, saving: false, error: "" });
      })
      .catch((error) => {
        if (!active) return;
        setState({
          loading: false,
          saving: false,
          error: error?.response?.data?.detail ?? "Unable to prepare the transfer form.",
        });
      });

    return () => {
      active = false;
    };
  }, [isEditing, transferId]);

  const isDraftRecord = !isEditing || recordStatus === "DRAFT";
  const warehouseConflict = useMemo(() => {
    return Boolean(form.source_warehouse_id && form.destination_warehouse_id && form.source_warehouse_id === form.destination_warehouse_id);
  }, [form.destination_warehouse_id, form.source_warehouse_id]);

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
      items: [...current.items, emptyTransferItem()],
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
    if (warehouseConflict) {
      setState((current) => ({
        ...current,
        error: "Source and destination warehouses must be different.",
      }));
      return;
    }

    setState((current) => ({ ...current, saving: true, error: "" }));

    const payload = {
      source_warehouse_id: Number(form.source_warehouse_id),
      destination_warehouse_id: Number(form.destination_warehouse_id),
      notes: form.notes || null,
      items: form.items.map((item) => ({
        product_id: Number(item.product_id),
        quantity: Number(item.quantity),
      })),
    };

    try {
      const response = isEditing
        ? await api.patch(`/inventory/transfers/${transferId}`, payload)
        : await api.post("/inventory/transfers", payload);
      navigate(`/inventory/transfers/${response.data.id}`);
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to save this stock transfer.",
      }));
    }
  }

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Inter-Warehouse Flow</p>
          <h2>{isEditing ? "Edit Stock Transfer" : "Create Stock Transfer"}</h2>
          <p>Move stock between warehouses with draft validation before the operational handoff starts.</p>
        </div>
        <div className="page-header-actions">
          {recordStatus ? <StatusBadge value={recordStatus} /> : null}
          <BackButton fallbackTo={isEditing ? `/inventory/transfers/${transferId}` : "/inventory/transfers"} />
        </div>
      </section>

      <form className="workspace-card form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading transfer form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}
        {!state.loading && isEditing && !isDraftRecord ? (
          <div className="surface-placeholder">Only draft transfers can be edited. Use the detail screen for status changes.</div>
        ) : null}

        {!state.loading ? (
          <>
            <div className="form-grid-wide">
              <label>
                Source warehouse
                <select
                  className="field-input"
                  value={form.source_warehouse_id}
                  onChange={(event) => update("source_warehouse_id", event.target.value)}
                  required
                  disabled={!isDraftRecord}
                >
                  <option value="">Select source warehouse</option>
                  {catalog.warehouses.map((option) => (
                    <option key={option.id} value={option.id}>
                      {option.name}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Destination warehouse
                <select
                  className="field-input"
                  value={form.destination_warehouse_id}
                  onChange={(event) => update("destination_warehouse_id", event.target.value)}
                  required
                  disabled={!isDraftRecord}
                >
                  <option value="">Select destination warehouse</option>
                  {catalog.warehouses.map((option) => (
                    <option key={option.id} value={option.id}>
                      {option.name}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field-span-full">
                Notes
                <textarea
                  className="field-input field-textarea"
                  value={form.notes}
                  onChange={(event) => update("notes", event.target.value)}
                  disabled={!isDraftRecord}
                />
              </label>
            </div>

            <div className="card-header-row">
              <h3>Transfer items</h3>
              <button className="ghost-button" type="button" onClick={addItem} disabled={!isDraftRecord}>
                Add Row
              </button>
            </div>

            <div className="line-items-stack">
              {form.items.map((item, index) => (
                <div className="line-item-card" key={`${index}-${item.product_id}`}>
                  <div className="line-item-grid">
                    <label>
                      Product
                      <select
                        className="field-input"
                        value={item.product_id}
                        onChange={(event) => updateItem(index, "product_id", event.target.value)}
                        required
                        disabled={!isDraftRecord}
                      >
                        <option value="">Select product</option>
                        {catalog.products.map((option) => (
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
                        value={item.quantity}
                        onChange={(event) => updateItem(index, "quantity", event.target.value)}
                        required
                        disabled={!isDraftRecord}
                      />
                    </label>
                  </div>
                  {form.items.length > 1 ? (
                    <button className="inline-link danger-link" type="button" onClick={() => removeItem(index)} disabled={!isDraftRecord}>
                      Remove row
                    </button>
                  ) : null}
                </div>
              ))}
            </div>

            {warehouseConflict ? <div className="surface-error">Source and destination warehouses must be different.</div> : null}

            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={state.saving || !isDraftRecord || warehouseConflict}>
                {state.saving ? "Saving…" : isEditing ? "Save Transfer" : "Create Transfer"}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
