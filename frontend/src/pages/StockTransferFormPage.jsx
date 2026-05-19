import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import api from "../lib/api";
import { formatNumber } from "../lib/format";

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
  const [sourceStock, setSourceStock] = useState([]);
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

  useEffect(() => {
    let active = true;

    async function loadSourceStock() {
      if (!form.source_warehouse_id) {
        setSourceStock([]);
        return;
      }

      try {
        const response = await api.get("/reports/warehouse-stock", {
          params: { warehouse_id: form.source_warehouse_id },
        });
        if (!active) return;
        setSourceStock(response.data.rows ?? []);
      } catch {
        if (!active) return;
        setSourceStock([]);
      }
    }

    loadSourceStock();
    return () => {
      active = false;
    };
  }, [form.source_warehouse_id]);

  const isDraftRecord = !isEditing || recordStatus === "DRAFT";
  const warehouseConflict = useMemo(() => {
    return Boolean(form.source_warehouse_id && form.destination_warehouse_id && form.source_warehouse_id === form.destination_warehouse_id);
  }, [form.destination_warehouse_id, form.source_warehouse_id]);
  const sourceStockMap = useMemo(
    () => new Map(sourceStock.map((row) => [String(row.product_id), Number(row.available_quantity ?? 0)])),
    [sourceStock],
  );
  const transferUnits = useMemo(
    () => form.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0),
    [form.items],
  );
  const lineWarnings = useMemo(
    () =>
      form.items.map((item) => {
        const available = sourceStockMap.get(String(item.product_id)) ?? 0;
        const requested = Number(item.quantity || 0);
        return {
          available,
          insufficient: Boolean(item.product_id && requested > available),
        };
      }),
    [form.items, sourceStockMap],
  );

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
    <div className="page-stack">
      <PageHeader
        eyebrow="Inter-Warehouse Flow"
        title={isEditing ? "Edit Stock Transfer" : "Create Stock Transfer"}
        description="Draft, validate, and hand off stock movement between warehouses with clear quantity checks."
        actions={
          <>
            {recordStatus ? <StatusBadge value={recordStatus} /> : null}
            <BackButton fallbackTo={isEditing ? `/inventory/transfers/${transferId}` : "/inventory/transfers"} />
          </>
        }
      />

      <div className="metric-grid">
        <MetricCard label="Line Items" value={formatNumber(form.items.length)} delta="Distinct products in transfer" tone="neutral" />
        <MetricCard label="Units To Move" value={formatNumber(transferUnits)} delta="Requested quantity total" tone="info" />
        <MetricCard label="Source Selected" value={form.source_warehouse_id ? "Yes" : "No"} delta="Origin location ready" tone="warning" />
        <MetricCard label="Destination Selected" value={form.destination_warehouse_id ? "Yes" : "No"} delta="Receiving location ready" tone="positive" />
      </div>

      <form className="form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading transfer form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}
        {!state.loading && isEditing && !isDraftRecord ? (
          <div className="surface-placeholder">Only draft transfers can be edited. Use the detail screen for status changes.</div>
        ) : null}

        {!state.loading ? (
          <>
            <section className="workspace-card form-section">
              <div className="form-section-heading">
                <h3>Route definition</h3>
                <p>Select the origin and receiving warehouse before assigning line quantities.</p>
              </div>
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
            </section>

            <section className="workspace-card form-section">
              <div className="card-header-row">
                <div className="form-section-heading">
                  <h3>Transfer items</h3>
                  <p>Requested quantity is checked against the selected source warehouse’s currently available stock.</p>
                </div>
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
                      <div className="inventory-preview-card">
                        <span>Available at source</span>
                        <strong>{formatNumber(lineWarnings[index]?.available ?? 0)}</strong>
                        <p>
                          {lineWarnings[index]?.insufficient
                            ? "Requested quantity is higher than current availability."
                            : "Requested quantity is within the current available stock."}
                        </p>
                      </div>
                    </div>
                    {lineWarnings[index]?.insufficient ? (
                      <div className="surface-error">Requested quantity exceeds available stock in the selected source warehouse.</div>
                    ) : null}
                    {form.items.length > 1 ? (
                      <button className="inline-link danger-link" type="button" onClick={() => removeItem(index)} disabled={!isDraftRecord}>
                        Remove row
                      </button>
                    ) : null}
                  </div>
                ))}
              </div>
            </section>

            <section className="workspace-card form-section">
              <div className="form-section-heading">
                <h3>Transfer timeline</h3>
                <p>Every transfer starts as draft, then moves to in transit, and is only completed after stock is posted at both ends.</p>
              </div>
              <div className="timeline-strip">
                {["DRAFT", "IN_TRANSIT", "COMPLETED"].map((step) => (
                  <div className={`timeline-step ${recordStatus === step || (!recordStatus && step === "DRAFT") ? "timeline-step-active" : ""}`} key={step}>
                    <span className="timeline-dot" />
                    <strong>{step.replaceAll("_", " ")}</strong>
                  </div>
                ))}
              </div>
            </section>

            {warehouseConflict ? <div className="surface-error">Source and destination warehouses must be different.</div> : null}

            <div className="workspace-card sticky-form-actions">
              <BackButton fallbackTo={isEditing ? `/inventory/transfers/${transferId}` : "/inventory/transfers"} />
              <button className="ghost-button" type="button" onClick={() => setSourceStock([])}>
                Clear preview
              </button>
              <button className="primary-button" type="submit" disabled={state.saving || !isDraftRecord || warehouseConflict || lineWarnings.some((item) => item.insufficient)}>
                {state.saving ? "Saving…" : isEditing ? "Save Transfer" : "Create Transfer"}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
