import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import api from "../lib/api";
import { formatCurrency } from "../lib/format";

const workflowFormConfigs = {
  package: {
    title: "Create Package",
    kicker: "Sales Fulfillment",
    description: "Bundle confirmed sales-order lines into a dedicated package record.",
    endpoint: "/packages",
    listPath: "/packages",
    detailPath: (id) => `/packages/${id}`,
    orderEndpoint: "/sales-orders",
    orderLabel: "Sales order",
    orderNumberKey: "so_number",
    dateField: null,
    numberField: "package_number",
    numberLabel: "Package number",
    summaryLabel: "Packing timeline",
  },
  invoice: {
    title: "Create Invoice",
    kicker: "Revenue Ledger",
    description: "Generate a customer invoice record against an existing sales order.",
    endpoint: "/invoices",
    listPath: "/invoices",
    detailPath: (id) => `/invoices/${id}`,
    orderEndpoint: "/sales-orders",
    orderLabel: "Sales order",
    orderNumberKey: "so_number",
    dateField: "invoice_date",
    dateLabel: "Invoice date",
    dueField: "due_date",
    dueLabel: "Due date",
    numberField: "invoice_number",
    numberLabel: "Invoice number",
    summaryLabel: "Receivables visibility",
  },
  salesReturn: {
    title: "Create Sales Return",
    kicker: "Reverse Logistics",
    description: "Capture customer returns against delivered sales orders and route quantities back to stock.",
    endpoint: "/sales-returns",
    listPath: "/sales-returns",
    detailPath: (id) => `/sales-returns/${id}`,
    orderEndpoint: "/sales-orders",
    orderLabel: "Delivered sales order",
    orderNumberKey: "so_number",
    dateField: "return_date",
    dateLabel: "Return date",
    numberField: "return_number",
    numberLabel: "Return number",
    lineMode: "salesReturn",
    summaryLabel: "Reverse-stock handling",
  },
  purchaseReceive: {
    title: "Post Purchase Receive",
    kicker: "Inbound Stock",
    description: "Record the exact quantities received against an issued purchase order.",
    endpoint: "/purchase-receives",
    listPath: "/purchase-receives",
    detailPath: (id) => `/purchase-receives/${id}`,
    orderEndpoint: "/purchase-orders",
    orderLabel: "Purchase order",
    orderNumberKey: "po_number",
    dateField: "received_at",
    dateLabel: "Received on",
    numberField: "receive_number",
    numberLabel: "Receipt number",
    lineMode: "purchaseReceive",
    summaryLabel: "Warehouse receipt posting",
  },
  bill: {
    title: "Create Bill",
    kicker: "Accounts Payable",
    description: "Create a vendor bill against an existing purchase order for payment tracking.",
    endpoint: "/bills",
    listPath: "/bills",
    detailPath: (id) => `/bills/${id}`,
    orderEndpoint: "/purchase-orders",
    orderLabel: "Purchase order",
    orderNumberKey: "po_number",
    dateField: "bill_date",
    dateLabel: "Bill date",
    dueField: "due_date",
    dueLabel: "Due date",
    numberField: "bill_number",
    numberLabel: "Bill number",
    summaryLabel: "Payables handoff",
  },
};

function buildInitialForm(config) {
  return {
    order_id: "",
    notes: "",
    [config.numberField]: "",
    ...(config.dateField ? { [config.dateField]: new Date().toISOString().slice(0, 10) } : {}),
    ...(config.dueField ? { [config.dueField]: "" } : {}),
    lineItems: [],
  };
}

export function BusinessRecordFormPage({ kind }) {
  const config = workflowFormConfigs[kind];
  const navigate = useNavigate();
  const [state, setState] = useState({ loading: true, saving: false, error: "" });
  const [form, setForm] = useState(() => buildInitialForm(config));
  const [orders, setOrders] = useState([]);
  const [orderDetail, setOrderDetail] = useState(null);

  useEffect(() => {
    let active = true;
    api
      .get(config.orderEndpoint, { params: { page_size: 100 } })
      .then(({ data }) => {
        if (!active) return;
        const items = (data.items ?? []).filter((record) => {
          if (kind === "salesReturn") return record.status === "DELIVERED";
          if (kind === "purchaseReceive") return record.status === "ISSUED" || record.status === "PARTIALLY_RECEIVED";
          return record.status !== "CANCELLED";
        });
        setOrders(items);
        setState({ loading: false, saving: false, error: "" });
      })
      .catch((error) => {
        if (!active) return;
        setState({
          loading: false,
          saving: false,
          error: error?.response?.data?.detail ?? "Unable to prepare this workflow form.",
        });
      });

    return () => {
      active = false;
    };
  }, [config.orderEndpoint, kind]);

  useEffect(() => {
    if (!form.order_id) {
      setOrderDetail(null);
      setForm((current) => ({ ...current, lineItems: [] }));
      return;
    }

    let active = true;
    api
      .get(`${config.orderEndpoint}/${form.order_id}`)
      .then(({ data }) => {
        if (!active) return;
        setOrderDetail(data);
        if (config.lineMode === "salesReturn") {
          setForm((current) => ({
            ...current,
            lineItems: (data.items ?? []).map((item) => ({
              sales_order_item_id: item.id,
              product_id: item.product_id,
              warehouse_id: item.warehouse_id,
              quantity: "0",
              reason: "",
              notes: "",
            })),
          }));
        } else if (config.lineMode === "purchaseReceive") {
          setForm((current) => ({
            ...current,
            lineItems: (data.items ?? []).map((item) => ({
              purchase_order_item_id: item.id,
              product_id: item.product_id,
              warehouse_id: item.warehouse_id,
              remaining: Math.max(0, Number(item.quantity_ordered) - Number(item.quantity_received)),
              quantity_received: String(Math.max(0, Number(item.quantity_ordered) - Number(item.quantity_received))),
            })),
          }));
        } else if (kind === "package") {
          setForm((current) => ({
            ...current,
            lineItems: (data.items ?? []).map((item) => ({
              sales_order_item_id: item.id,
              product_id: item.product_id,
              warehouse_id: item.warehouse_id,
              quantity: String(item.quantity),
            })),
          }));
        }
      })
      .catch((error) => {
        if (!active) return;
        setState((current) => ({
          ...current,
          error: error?.response?.data?.detail ?? "Unable to load the selected order.",
        }));
      });

    return () => {
      active = false;
    };
  }, [config.lineMode, config.orderEndpoint, form.order_id, kind]);

  const totals = useMemo(() => {
    if (!orderDetail) return null;
    return {
      subtotal: Number(orderDetail.subtotal ?? 0),
      tax: Number(orderDetail.tax_amount ?? 0),
      discount: Number(orderDetail.discount_amount ?? 0),
      total: Number(orderDetail.total_amount ?? 0),
      items: (orderDetail.items ?? []).length,
    };
  }, [orderDetail]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function updateLine(index, field, value) {
    setForm((current) => ({
      ...current,
      lineItems: current.lineItems.map((item, itemIndex) => (itemIndex === index ? { ...item, [field]: value } : item)),
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, saving: true, error: "" }));

    const basePayload = {
      notes: form.notes || null,
      [config.numberField]: form[config.numberField],
      ...(config.dateField ? { [config.dateField]: form[config.dateField] } : {}),
      ...(config.dueField ? { [config.dueField]: form[config.dueField] || null } : {}),
    };

    let payload;
    if (kind === "package") {
      payload = {
        ...basePayload,
        sales_order_id: Number(form.order_id),
        items: form.lineItems
          .map((item) => ({
            sales_order_item_id: Number(item.sales_order_item_id),
            quantity: Number(item.quantity),
          }))
          .filter((item) => item.quantity > 0),
      };
    } else if (kind === "invoice") {
      payload = {
        ...basePayload,
        sales_order_id: Number(form.order_id),
      };
    } else if (kind === "salesReturn") {
      payload = {
        ...basePayload,
        sales_order_id: Number(form.order_id),
        items: form.lineItems
          .map((item) => ({
            sales_order_item_id: Number(item.sales_order_item_id),
            warehouse_id: Number(item.warehouse_id),
            quantity: Number(item.quantity),
            reason: item.reason || null,
            notes: item.notes || null,
          }))
          .filter((item) => item.quantity > 0),
      };
    } else if (kind === "purchaseReceive") {
      payload = {
        ...basePayload,
        purchase_order_id: Number(form.order_id),
        items: form.lineItems
          .map((item) => ({
            purchase_order_item_id: Number(item.purchase_order_item_id),
            quantity_received: Number(item.quantity_received),
          }))
          .filter((item) => item.quantity_received > 0),
      };
    } else {
      payload = {
        ...basePayload,
        purchase_order_id: Number(form.order_id),
      };
    }

    try {
      const response = await api.post(config.endpoint, payload);
      navigate(config.detailPath(response.data.id));
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to save this workflow record.",
      }));
    }
  }

  return (
    <div className="page-stack">
      <PageHeader eyebrow={config.kicker} title={config.title} description={config.description} backTo={config.listPath} />

      <div className="commercial-summary-grid">
        <article className="commercial-summary-card">
          <span>{config.orderLabel}</span>
          <strong>{orders.find((order) => String(order.id) === String(form.order_id))?.[config.orderNumberKey] ?? "Not selected"}</strong>
          <p>Pick the source order first so the downstream workflow can inherit live quantities and value.</p>
        </article>
        <article className="commercial-summary-card">
          <span>Workflow purpose</span>
          <strong>{config.summaryLabel}</strong>
          <p>{kind === "invoice" || kind === "bill" ? "Document financial follow-through after the operational order is created." : "Carry the operational order deeper into fulfillment or reverse-logistics stages."}</p>
        </article>
        <article className="commercial-summary-card">
          <span>Linked lines</span>
          <strong>{form.lineItems.length}</strong>
          <p>{kind === "invoice" || kind === "bill" ? "This workflow is document-level and does not require editable line quantities." : "Editable order lines are available once an order is chosen."}</p>
        </article>
        <article className="commercial-summary-card">
          <span>Order total</span>
          <strong>{formatCurrency(totals?.total ?? 0)}</strong>
          <p>Source order commercial value is shown here for quick operator context.</p>
        </article>
      </div>

      <form className="form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="workspace-card surface-placeholder">Loading form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
            <section className="form-section">
              <div className="form-section-heading">
                <h3>Document and source order</h3>
                <p>Select the order this record belongs to, then set the commercial document number and milestone dates.</p>
              </div>
              <div className="form-grid-wide">
                <label>
                  {config.orderLabel}
                  <select className="field-input" value={form.order_id} onChange={(event) => update("order_id", event.target.value)} required>
                    <option value="">Select {config.orderLabel.toLowerCase()}</option>
                    {orders.map((order) => (
                      <option key={order.id} value={order.id}>
                        {order[config.orderNumberKey]} • {order.status}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  {config.numberLabel}
                  <input className="field-input" value={form[config.numberField]} onChange={(event) => update(config.numberField, event.target.value)} required />
                </label>

                {config.dateField ? (
                  <label>
                    {config.dateLabel}
                    <input className="field-input" type="date" value={form[config.dateField]} onChange={(event) => update(config.dateField, event.target.value)} required />
                  </label>
                ) : null}

                {config.dueField ? (
                  <label>
                    {config.dueLabel}
                    <input className="field-input" type="date" value={form[config.dueField]} onChange={(event) => update(config.dueField, event.target.value)} />
                  </label>
                ) : null}
              </div>
            </section>

            {orderDetail ? (
              <section className="form-section">
                <div className="form-section-heading">
                  <h3>Source order snapshot</h3>
                  <p>Use this live order summary to verify commercial context before posting the downstream document.</p>
                </div>
                <div className="commercial-order-snapshot">
                  <div className="commercial-summary-card">
                    <span>Source status</span>
                    <strong>{orderDetail.status?.replaceAll("_", " ") ?? "—"}</strong>
                    <p>Lines: {totals?.items ?? 0}</p>
                  </div>
                  <div className="commercial-summary-card">
                    <span>Subtotal</span>
                    <strong>{formatCurrency(totals?.subtotal ?? 0)}</strong>
                    <p>Tax {formatCurrency(totals?.tax ?? 0)}</p>
                  </div>
                  <div className="commercial-summary-card">
                    <span>Discount</span>
                    <strong>{formatCurrency(totals?.discount ?? 0)}</strong>
                    <p>Included only if the source order supports discounts.</p>
                  </div>
                  <div className="commercial-summary-card">
                    <span>Total</span>
                    <strong>{formatCurrency(totals?.total ?? 0)}</strong>
                    <p>Use this for quick cross-checking before posting.</p>
                  </div>
                </div>
              </section>
            ) : null}

            {form.lineItems.length ? (
              <section className="form-section">
                <div className="form-section-heading">
                  <h3>{kind === "purchaseReceive" ? "Receive quantities" : kind === "salesReturn" ? "Return lines" : "Package lines"}</h3>
                  <p>{kind === "purchaseReceive" ? "Confirm the exact quantities received into the warehouse." : kind === "salesReturn" ? "Specify the lines coming back into stock and why they were returned." : "Choose the quantities that belong in this package."}</p>
                </div>
                <div className="line-items-stack">
                  {form.lineItems.map((item, index) => (
                    <div className="line-item-card" key={`${index}-${item.product_id}-${item.warehouse_id}`}>
                      <div className="commercial-line-header">
                        <strong>Line {index + 1}</strong>
                        <span>Product #{item.product_id} • Warehouse #{item.warehouse_id}</span>
                      </div>
                      <div className="form-grid-wide">
                        {kind === "purchaseReceive" ? (
                          <>
                            <label>
                              Remaining quantity
                              <input className="field-input" value={item.remaining ?? 0} disabled />
                            </label>
                            <label>
                              Quantity received
                              <input className="field-input" type="number" min="0" max={item.remaining ?? undefined} value={item.quantity_received} onChange={(event) => updateLine(index, "quantity_received", event.target.value)} />
                            </label>
                          </>
                        ) : (
                          <>
                            <label>
                              Quantity
                              <input className="field-input" type="number" min="0" value={item.quantity} onChange={(event) => updateLine(index, "quantity", event.target.value)} />
                            </label>
                            {kind === "salesReturn" ? (
                              <label>
                                Return reason
                                <input className="field-input" value={item.reason} onChange={(event) => updateLine(index, "reason", event.target.value)} />
                              </label>
                            ) : null}
                          </>
                        )}
                        {kind === "salesReturn" ? (
                          <label className="field-span-full">
                            Notes
                            <textarea className="field-input field-textarea" value={item.notes} onChange={(event) => updateLine(index, "notes", event.target.value)} />
                          </label>
                        ) : null}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            ) : null}

            <div className="commercial-form-columns">
              <section className="form-section">
                <div className="form-section-heading">
                  <h3>Notes and internal context</h3>
                  <p>Capture handoff notes, exceptions, or AP/AR context for the next operator.</p>
                </div>
                <label className="field-span-full">
                  Notes
                  <textarea className="field-input field-textarea" value={form.notes} onChange={(event) => update("notes", event.target.value)} />
                </label>
              </section>

              <section className="form-section">
                <div className="form-section-heading">
                  <h3>Posting guidance</h3>
                  <p>Use this workflow to keep downstream activity tied directly to the source order and tenant data.</p>
                </div>
                <div className="mini-list">
                  <div className="mini-list-row">
                    <div>
                      <strong>Linked order</strong>
                      <span>{orderDetail ? "Ready" : "Select a source order"}</span>
                    </div>
                  </div>
                  <div className="mini-list-row">
                    <div>
                      <strong>Document number</strong>
                      <span>{form[config.numberField] || "Not entered yet"}</span>
                    </div>
                  </div>
                  <div className="mini-list-row">
                    <div>
                      <strong>Workflow type</strong>
                      <span>{config.summaryLabel}</span>
                    </div>
                  </div>
                </div>
              </section>
            </div>

            <div className="sticky-form-actions">
              <button className="button button-ghost" type="button" onClick={() => navigate(config.listPath)}>
                Cancel
              </button>
              <button className="button button-primary" type="submit" disabled={state.saving}>
                {state.saving ? "Saving…" : config.title}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
