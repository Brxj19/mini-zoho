import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import api from "../lib/api";

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
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">{config.kicker}</p>
          <h2>{config.title}</h2>
          <p>{config.description}</p>
        </div>
        <BackButton fallbackTo={config.listPath} />
      </section>

      <form className="workspace-card form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
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

              <label className="field-span-full">
                Notes
                <textarea className="field-input field-textarea" value={form.notes} onChange={(event) => update("notes", event.target.value)} />
              </label>
            </div>

            {orderDetail ? (
              <>
                <div className="card-header-row">
                  <h3>Selected order snapshot</h3>
                </div>
                <div className="kv-grid">
                  <div className="kv-item">
                    <span>Status</span>
                    <strong>{orderDetail.status}</strong>
                  </div>
                  <div className="kv-item">
                    <span>Partner ID</span>
                    <strong>{orderDetail.customer_id ?? orderDetail.vendor_id}</strong>
                  </div>
                  <div className="kv-item">
                    <span>Order date</span>
                    <strong>{orderDetail.order_date}</strong>
                  </div>
                  {totals ? (
                    <div className="kv-item">
                      <span>Total</span>
                      <strong>{totals.total.toFixed(2)}</strong>
                    </div>
                  ) : null}
                </div>
              </>
            ) : null}

            {form.lineItems.length ? (
              <>
                <div className="card-header-row">
                  <h3>Line items</h3>
                </div>
                <div className="line-items-stack">
                  {form.lineItems.map((item, index) => (
                    <div className="line-item-card" key={`${index}-${item.product_id}-${item.warehouse_id}`}>
                      <div className="line-item-grid">
                        <label>
                          Product ID
                          <input className="field-input" value={item.product_id} disabled />
                        </label>
                        <label>
                          Warehouse ID
                          <input className="field-input" value={item.warehouse_id} disabled />
                        </label>
                        {kind === "purchaseReceive" ? (
                          <>
                            <label>
                              Remaining
                              <input className="field-input" value={item.remaining} disabled />
                            </label>
                            <label>
                              Receive now
                              <input
                                className="field-input"
                                type="number"
                                min="0"
                                max={item.remaining}
                                step="1"
                                value={item.quantity_received}
                                onChange={(event) => updateLine(index, "quantity_received", event.target.value)}
                              />
                            </label>
                          </>
                        ) : (
                          <label>
                            Quantity
                            <input
                              className="field-input"
                              type="number"
                              min="0"
                              step="1"
                              value={item.quantity}
                              onChange={(event) => updateLine(index, "quantity", event.target.value)}
                            />
                          </label>
                        )}

                        {kind === "salesReturn" ? (
                          <>
                            <label>
                              Reason
                              <input className="field-input" value={item.reason} onChange={(event) => updateLine(index, "reason", event.target.value)} />
                            </label>
                            <label className="field-span-full">
                              Line notes
                              <textarea className="field-input field-textarea" value={item.notes} onChange={(event) => updateLine(index, "notes", event.target.value)} />
                            </label>
                          </>
                        ) : null}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : null}

            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={state.saving}>
                {state.saving ? "Saving…" : "Create Record"}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
