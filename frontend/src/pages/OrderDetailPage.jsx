import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../lib/api";
import { DashboardWidget } from "../components/DashboardWidget";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { Timeline } from "../components/Timeline";

export function OrderDetailPage({ type }) {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const moduleKey = type === "sales" ? "sales-orders" : "purchase-orders";
  const [order, setOrder] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const steps =
    type === "sales"
      ? ["DRAFT", "CONFIRMED", "PACKED", "SHIPPED", "DELIVERED"]
      : ["DRAFT", "ISSUED", "PARTIALLY_RECEIVED", "RECEIVED"];

  useEffect(() => {
    api.get(`/app/${moduleKey}/${orderId}`).then(({ data }) => setOrder(data)).catch(() => setOrder(null));
  }, [moduleKey, orderId]);

  async function updateStatus(nextStatus) {
    setIsUpdating(true);
    try {
      const { data } = await api.patch(`/app/${moduleKey}/${orderId}/status`, { status: nextStatus });
      setOrder((current) => ({ ...current, ...data }));
    } finally {
      setIsUpdating(false);
    }
  }

  if (!order) {
    return (
      <EmptyState
        icon="clipboard"
        title="Order not found"
        description="This order record is not available."
        actionLabel={`Back to ${type === "sales" ? "sales" : "purchase"} orders`}
        actionTo={type === "sales" ? "/sales-orders" : "/purchase-orders"}
      />
    );
  }

  const counterpartLabel = type === "sales" ? "Customer" : "Vendor";
  const counterpartValue = type === "sales" ? order.customerName : order.vendorName;

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={type === "sales" ? "Sales Order Detail" : "Purchase Order Detail"}
        title={order.orderNumber}
        description={`${counterpartLabel}: ${counterpartValue} • Reference: ${order.reference}`}
        actions={
          <div className="header-inline-chips">
            <StatusBadge status={order.status} />
            <button className="button button-secondary" type="button" onClick={() => window.print()}>
              Print
            </button>
            <button className="button button-ghost" type="button" onClick={() => window.print()}>
              PDF
            </button>
          </div>
        }
      />

      <DashboardWidget title="Workflow Progress">
        <Timeline steps={steps} currentStep={order.status} />
      </DashboardWidget>

      <section className="detail-grid">
        <DashboardWidget title="Order Actions" className="widget-span-2">
          <div className="stack-actions horizontal">
            {type === "sales" ? (
              <>
                <button className="button button-primary" type="button" disabled={isUpdating} onClick={() => updateStatus("CONFIRMED")}>Confirm</button>
                <button className="button button-secondary" type="button" disabled={isUpdating} onClick={() => updateStatus("PACKED")}>Pack</button>
                <button className="button button-secondary" type="button" disabled={isUpdating} onClick={() => updateStatus("SHIPPED")}>Ship</button>
                <button className="button button-secondary" type="button" disabled={isUpdating} onClick={() => updateStatus("DELIVERED")}>Deliver</button>
              </>
            ) : (
              <>
                <button className="button button-primary" type="button" disabled={isUpdating} onClick={() => updateStatus("ISSUED")}>Issue</button>
                <button className="button button-secondary" type="button" disabled={isUpdating} onClick={() => updateStatus("RECEIVED")}>Receive</button>
              </>
            )}
            <button className="button button-ghost" type="button" onClick={() => navigate(type === "sales" ? "/sales-orders/new" : "/purchase-orders/new")}>Clone</button>
            <button className="button button-ghost" type="button" disabled={isUpdating} onClick={() => updateStatus("CANCELLED")}>Cancel</button>
          </div>
        </DashboardWidget>

        <DashboardWidget title={`${counterpartLabel} Panel`}>
          <div className="detail-overview-grid compact">
            <div><span>Name</span><strong>{counterpartValue}</strong></div>
            <div><span>Date</span><strong>{order.date}</strong></div>
            <div><span>Status</span><strong>{order.status.replaceAll("_", " ")}</strong></div>
            <div><span>Amount</span><strong>{order.amount}</strong></div>
          </div>
        </DashboardWidget>
      </section>

      <DashboardWidget title="Item Table">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Warehouse</th>
                <th>Qty</th>
                <th>Rate</th>
              </tr>
            </thead>
            <tbody>
              {(order.items ?? []).map((item, index) => (
                <tr key={`${item.name}-${index}`}>
                  <td>{item.name}</td>
                  <td>{item.warehouse ?? "Central Warehouse"}</td>
                  <td>{item.quantity}</td>
                  <td>{item.rate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DashboardWidget>
    </div>
  );
}
