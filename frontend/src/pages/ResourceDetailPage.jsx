import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import api from "../lib/api";
import { formatCurrency, formatDate, formatDateTime } from "../lib/format";
import { StatusBadge } from "../components/StatusBadge";

const detailConfigs = {
  product: {
    title: "Item Detail",
    endpoint: (id) => `/products/${id}`,
    editPath: (id) => `/items/${id}/edit`,
    listPath: "/items",
    supplementary: (id) => [
      { key: "stock", endpoint: `/products/${id}/stock` },
      { key: "transactions", endpoint: `/products/${id}/transactions` },
    ],
  },
  warehouse: {
    title: "Warehouse Detail",
    endpoint: (id) => `/warehouses/${id}`,
    editPath: (id) => `/warehouses/${id}/edit`,
    listPath: "/warehouses",
  },
  category: {
    title: "Category Detail",
    endpoint: (id) => `/categories/${id}`,
    editPath: (id) => `/categories/${id}/edit`,
    listPath: "/categories",
  },
  brand: {
    title: "Brand Detail",
    endpoint: (id) => `/brands/${id}`,
    editPath: (id) => `/brands/${id}/edit`,
    listPath: "/brands",
  },
  vendor: {
    title: "Vendor Detail",
    endpoint: (id) => `/vendors/${id}`,
    editPath: (id) => `/vendors/${id}/edit`,
    listPath: "/vendors",
  },
  customer: {
    title: "Customer Detail",
    endpoint: (id) => `/customers/${id}`,
    editPath: (id) => `/customers/${id}/edit`,
    listPath: "/customers",
  },
  stockTransfer: {
    title: "Stock Transfer Detail",
    endpoint: (id) => `/inventory/transfers/${id}`,
    editPath: (id) => `/inventory/transfers/${id}/edit`,
    canEdit: (record) => record?.status === "DRAFT",
    listPath: "/inventory/transfers",
  },
  purchaseOrder: {
    title: "Purchase Order Detail",
    endpoint: (id) => `/purchase-orders/${id}`,
    editPath: (id) => `/purchase-orders/${id}/edit`,
    canEdit: (record) => record?.status === "DRAFT",
    listPath: "/purchase-orders",
  },
  salesOrder: {
    title: "Sales Order Detail",
    endpoint: (id) => `/sales-orders/${id}`,
    editPath: (id) => `/sales-orders/${id}/edit`,
    canEdit: (record) => record?.status === "DRAFT",
    listPath: "/sales-orders",
  },
};

const workflowConfigs = {
  stockTransfer: {
    title: "Transfer Progress",
    steps: ["DRAFT", "IN_TRANSIT", "COMPLETED"],
    actions: (record, id) => {
      const actions = [];
      if (record.status === "DRAFT") {
        actions.push({
          type: "request",
          label: "Mark In Transit",
          endpoint: `/inventory/transfers/${id}/in-transit`,
          successMessage: "Transfer moved to in transit.",
        });
        actions.push({
          type: "request",
          label: "Cancel Transfer",
          endpoint: `/inventory/transfers/${id}/cancel`,
          tone: "danger",
          successMessage: "Transfer cancelled.",
        });
      }
      if (record.status === "IN_TRANSIT") {
        actions.push({
          type: "request",
          label: "Complete Transfer",
          endpoint: `/inventory/transfers/${id}/complete`,
          successMessage: "Transfer completed and stock positions updated.",
        });
        actions.push({
          type: "request",
          label: "Cancel Transfer",
          endpoint: `/inventory/transfers/${id}/cancel`,
          tone: "danger",
          successMessage: "Transfer cancelled.",
        });
      }
      return actions;
    },
  },
  purchaseOrder: {
    title: "Purchase Timeline",
    steps: ["DRAFT", "ISSUED", "PARTIALLY_RECEIVED", "RECEIVED"],
    actions: (record, id) => {
      const actions = [];
      if (record.status === "DRAFT") {
        actions.push({
          type: "request",
          label: "Issue Purchase Order",
          endpoint: `/purchase-orders/${id}/issue`,
          successMessage: "Purchase order issued.",
        });
      }
      if (record.status === "ISSUED" || record.status === "PARTIALLY_RECEIVED") {
        actions.push({
          type: "receive",
          label: record.status === "PARTIALLY_RECEIVED" ? "Receive Remaining" : "Receive Stock",
        });
      }
      if (record.status !== "RECEIVED" && record.status !== "CANCELLED") {
        actions.push({
          type: "request",
          label: "Cancel Purchase Order",
          endpoint: `/purchase-orders/${id}/cancel`,
          tone: "danger",
          successMessage: "Purchase order cancelled.",
        });
      }
      return actions;
    },
  },
  salesOrder: {
    title: "Sales Timeline",
    steps: ["DRAFT", "CONFIRMED", "PACKED", "SHIPPED", "DELIVERED"],
    actions: (record, id) => {
      const actions = [];
      if (record.status === "DRAFT") {
        actions.push({
          type: "request",
          label: "Confirm Order",
          endpoint: `/sales-orders/${id}/confirm`,
          successMessage: "Sales order confirmed and stock reserved.",
        });
      }
      if (record.status === "CONFIRMED") {
        actions.push({
          type: "request",
          label: "Mark Packed",
          endpoint: `/sales-orders/${id}/pack`,
          successMessage: "Sales order marked as packed.",
        });
      }
      if (record.status === "PACKED") {
        actions.push({
          type: "request",
          label: "Mark Shipped",
          endpoint: `/sales-orders/${id}/ship`,
          successMessage: "Sales order marked as shipped.",
        });
      }
      if (record.status === "SHIPPED") {
        actions.push({
          type: "request",
          label: "Mark Delivered",
          endpoint: `/sales-orders/${id}/deliver`,
          successMessage: "Sales order delivered and stock deducted.",
        });
      }
      if (record.status !== "DELIVERED" && record.status !== "CANCELLED") {
        actions.push({
          type: "request",
          label: "Cancel Order",
          endpoint: `/sales-orders/${id}/cancel`,
          tone: "danger",
          successMessage: "Sales order cancelled.",
        });
      }
      return actions;
    },
  },
};

function keyValueEntries(record) {
  return Object.entries(record ?? {}).filter(([key, value]) => !Array.isArray(value) && typeof value !== "object" && key !== "id");
}

function formatValue(key, value) {
  if (key.includes("amount") || key.includes("price")) return formatCurrency(value);
  if (key.includes("date") || key.endsWith("_at")) return key.endsWith("_at") ? formatDateTime(value) : formatDate(value);
  if (key === "status") return <StatusBadge value={value} />;
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return value ?? "—";
}

function workflowStepState(step, status, steps) {
  if (status === "CANCELLED") return "pending";
  const activeIndex = steps.indexOf(status);
  const stepIndex = steps.indexOf(step);
  if (stepIndex < activeIndex) return "complete";
  if (stepIndex === activeIndex) return "active";
  return "pending";
}

export function ResourceDetailPage({ detailKey, paramKey }) {
  const { [paramKey]: entityId } = useParams();
  const config = detailConfigs[detailKey];
  const workflow = workflowConfigs[detailKey];
  const [reloadKey, setReloadKey] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: "",
    record: null,
    supplementary: {},
  });
  const [feedback, setFeedback] = useState({ success: "" });
  const [modal, setModal] = useState(null);
  const [actionState, setActionState] = useState({ submitting: false, error: "" });

  useEffect(() => {
    let active = true;

    async function load() {
      setState((current) => ({ ...current, loading: true, error: "" }));
      try {
        const primaryResponse = await api.get(config.endpoint(entityId));
        const extraEntries = {};

        if (config.supplementary) {
          const results = await Promise.all(
            config.supplementary(entityId).map(async (entry) => {
              const response = await api.get(entry.endpoint);
              return [entry.key, response.data];
            }),
          );
          results.forEach(([key, value]) => {
            extraEntries[key] = value;
          });
        }

        if (!active) return;
        setState({
          loading: false,
          error: "",
          record: primaryResponse.data,
          supplementary: extraEntries,
        });
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load record details.",
          record: null,
          supplementary: {},
        });
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [config, entityId, reloadKey]);

  const entries = useMemo(() => keyValueEntries(state.record), [state.record]);
  const itemRows = state.record?.items ?? [];
  const stockRows = state.supplementary.stock?.warehouses ?? [];
  const transactionRows = state.supplementary.transactions?.items ?? [];
  const workflowActions = workflow && state.record ? workflow.actions(state.record, entityId) : [];
  const canEdit = config.editPath && state.record ? (config.canEdit ? config.canEdit(state.record) : true) : false;

  function openActionModal(action) {
    setActionState({ submitting: false, error: "" });
    if (action.type === "receive") {
      const receiveItems = (state.record?.items ?? [])
        .map((item) => {
          const remaining = Math.max(0, Number(item.quantity_ordered) - Number(item.quantity_received));
          return {
            purchase_order_item_id: item.id,
            product_id: item.product_id,
            warehouse_id: item.warehouse_id,
            remaining,
            quantity_received: remaining > 0 ? String(remaining) : "0",
          };
        })
        .filter((item) => item.remaining > 0);

      setModal({
        type: "receive",
        label: action.label,
        notes: state.record?.notes ?? "",
        items: receiveItems,
      });
      return;
    }

    setModal({
      type: "request",
      label: action.label,
      endpoint: action.endpoint,
      tone: action.tone ?? "primary",
      successMessage: action.successMessage,
      notes: state.record?.notes ?? "",
    });
  }

  function closeModal() {
    setModal(null);
    setActionState({ submitting: false, error: "" });
  }

  async function submitRequestAction() {
    if (!modal?.endpoint) return;
    setActionState({ submitting: true, error: "" });

    try {
      await api.post(modal.endpoint, { notes: modal.notes || null });
      closeModal();
      setFeedback({ success: modal.successMessage ?? `${modal.label} completed.` });
      setReloadKey((value) => value + 1);
    } catch (error) {
      setActionState({
        submitting: false,
        error: error?.response?.data?.detail ?? `Unable to ${modal.label.toLowerCase()}.`,
      });
    }
  }

  async function submitReceiveAction() {
    if (!modal) return;

    const items = modal.items
      .map((item) => ({
        purchase_order_item_id: item.purchase_order_item_id,
        quantity_received: Number(item.quantity_received),
      }))
      .filter((item) => item.quantity_received > 0);

    if (!items.length) {
      setActionState({ submitting: false, error: "Enter at least one received quantity greater than zero." });
      return;
    }

    setActionState({ submitting: true, error: "" });

    try {
      await api.post(`/purchase-orders/${entityId}/receive`, {
        notes: modal.notes || null,
        items,
      });
      closeModal();
      setFeedback({ success: "Purchase receipt posted successfully." });
      setReloadKey((value) => value + 1);
    } catch (error) {
      setActionState({
        submitting: false,
        error: error?.response?.data?.detail ?? "Unable to receive this purchase order.",
      });
    }
  }

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Workspace Detail</p>
          <h2>{config.title}</h2>
          <p>Key record details, line items, and related operational activity.</p>
        </div>
        <div className="page-header-actions">
          <BackButton fallbackTo={config.listPath ?? "/"} />
          {canEdit ? (
            <Link className="ghost-button" to={config.editPath(entityId)}>
              Edit
            </Link>
          ) : null}
        </div>
      </section>

      {feedback.success ? <div className="surface-success">{feedback.success}</div> : null}
      {state.loading ? <div className="workspace-card surface-placeholder">Loading detail…</div> : null}
      {!state.loading && state.error ? <div className="workspace-card surface-error">{state.error}</div> : null}

      {!state.loading && state.record ? (
        <>
          {workflow ? (
            <section className="workspace-card workflow-card">
              <div className="card-header-row">
                <div>
                  <h3>{workflow.title}</h3>
                  <p>Advance the workflow with live backend status actions.</p>
                </div>
                <StatusBadge value={state.record.status} />
              </div>

              <div className="timeline-strip">
                {workflow.steps.map((step) => (
                  <div className={`timeline-step timeline-step-${workflowStepState(step, state.record.status, workflow.steps)}`} key={step}>
                    <span className="timeline-dot" />
                    <strong>{step.replaceAll("_", " ")}</strong>
                  </div>
                ))}
                {state.record.status === "CANCELLED" ? (
                  <div className="timeline-terminal">
                    <StatusBadge value="CANCELLED" />
                  </div>
                ) : null}
              </div>

              {workflowActions.length ? (
                <div className="workflow-actions">
                  {workflowActions.map((action) => (
                    <button
                      key={action.label}
                      className={action.tone === "danger" ? "button button-ghost button-danger" : "button button-primary"}
                      type="button"
                      onClick={() => openActionModal(action)}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="surface-placeholder">No further operational actions are available for the current status.</div>
              )}
            </section>
          ) : null}

          <section className="detail-grid">
            <article className="workspace-card">
              <div className="card-header-row">
                <h3>Summary</h3>
              </div>
              <div className="kv-grid">
                {entries.map(([key, value]) => (
                  <div className="kv-item" key={key}>
                    <span>{key.replaceAll("_", " ")}</span>
                    <strong>{formatValue(key, value)}</strong>
                  </div>
                ))}
              </div>
            </article>

            {stockRows.length > 0 ? (
              <article className="workspace-card">
                <div className="card-header-row">
                  <h3>Stock Footprint</h3>
                </div>
                <div className="mini-list">
                  {stockRows.map((item) => (
                    <div className="mini-list-row" key={item.warehouse_id}>
                      <div>
                        <strong>Warehouse #{item.warehouse_id}</strong>
                        <span>Available {item.available_quantity}</span>
                      </div>
                      <StatusBadge value={item.available_quantity <= item.reorder_level ? "LOW_STOCK" : "ACTIVE"} />
                    </div>
                  ))}
                </div>
              </article>
            ) : null}
          </section>

          {itemRows.length > 0 ? (
            <section className="workspace-card">
              <div className="card-header-row">
                <h3>Line Items</h3>
              </div>
              <div className="data-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      {Object.keys(itemRows[0]).map((key) => (
                        <th key={key}>{key.replaceAll("_", " ")}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {itemRows.map((row) => (
                      <tr key={row.id}>
                        {Object.entries(row).map(([key, value]) => (
                          <td key={key}>{formatValue(key, value)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}

          {transactionRows.length > 0 ? (
            <section className="workspace-card">
              <div className="card-header-row">
                <h3>Recent Movement</h3>
              </div>
              <div className="mini-list">
                {transactionRows.slice(0, 6).map((row) => (
                  <div className="mini-list-row" key={row.id}>
                    <div>
                      <strong>{row.transaction_type.replaceAll("_", " ")}</strong>
                      <span>{formatDateTime(row.created_at)}</span>
                    </div>
                    <span>{row.quantity}</span>
                  </div>
                ))}
              </div>
            </section>
          ) : null}
        </>
      ) : null}

      {modal ? (
        <div className="modal-scrim" role="dialog" aria-modal="true">
          <div className={`modal-card ${modal.type === "receive" ? "modal-card-wide" : ""}`}>
            <h3>{modal.label}</h3>
            <p className="page-header-description">
              {modal.type === "receive"
                ? "Post received quantities for each remaining purchase line."
                : "Add an optional workflow note and confirm the status action."}
            </p>

            {modal.type === "receive" ? (
              <div className="line-items-stack">
                {modal.items.length ? (
                  modal.items.map((item, index) => (
                    <div className="line-item-card" key={item.purchase_order_item_id}>
                      <div className="line-item-grid">
                        <div className="workflow-meta">
                          <span>Product ID</span>
                          <strong>{item.product_id}</strong>
                        </div>
                        <div className="workflow-meta">
                          <span>Warehouse ID</span>
                          <strong>{item.warehouse_id}</strong>
                        </div>
                        <div className="workflow-meta">
                          <span>Remaining</span>
                          <strong>{item.remaining}</strong>
                        </div>
                        <label>
                          Receive now
                          <input
                            className="field-input"
                            type="number"
                            min="0"
                            max={item.remaining}
                            step="1"
                            value={item.quantity_received}
                            onChange={(event) =>
                              setModal((current) => ({
                                ...current,
                                items: current.items.map((entry, itemIndex) =>
                                  itemIndex === index ? { ...entry, quantity_received: event.target.value } : entry,
                                ),
                              }))
                            }
                          />
                        </label>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="surface-placeholder">All line items are already fully received.</div>
                )}
              </div>
            ) : null}

            <label className="modal-field">
              Notes
              <textarea
                className="field-input field-textarea"
                value={modal.notes}
                onChange={(event) => setModal((current) => ({ ...current, notes: event.target.value }))}
              />
            </label>

            {actionState.error ? <div className="surface-error">{actionState.error}</div> : null}

            <div className="modal-actions">
              <button className="ghost-button" type="button" onClick={closeModal} disabled={actionState.submitting}>
                Close
              </button>
              <button
                className={modal.tone === "danger" ? "button button-ghost button-danger" : "primary-button"}
                type="button"
                onClick={modal.type === "receive" ? submitReceiveAction : submitRequestAction}
                disabled={actionState.submitting || (modal.type === "receive" && modal.items.length === 0)}
              >
                {actionState.submitting ? "Submitting…" : modal.type === "receive" ? "Post Receipt" : modal.label}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
