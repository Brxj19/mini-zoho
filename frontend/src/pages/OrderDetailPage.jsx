import { useParams } from "react-router-dom";

import { DashboardWidget } from "../components/DashboardWidget";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { Timeline } from "../components/Timeline";
import { getRecordById } from "../lib/demoData";

export function OrderDetailPage({ type }) {
  const { orderId } = useParams();
  const moduleKey = type === "sales" ? "sales-orders" : "purchase-orders";
  const order = getRecordById(moduleKey, orderId);
  const steps =
    type === "sales"
      ? ["DRAFT", "CONFIRMED", "PACKED", "SHIPPED", "DELIVERED"]
      : ["DRAFT", "ISSUED", "PARTIALLY_RECEIVED", "RECEIVED"];

  if (!order) {
    return (
      <EmptyState
        icon="clipboard"
        title="Order not found"
        description="This order record is not present in the current UI demo data."
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
        title={order.id}
        description={`${counterpartLabel}: ${counterpartValue} • Reference: ${order.reference}`}
        actions={
          <div className="header-inline-chips">
            <StatusBadge status={order.status} />
            <button className="button button-secondary" type="button">Print</button>
            <button className="button button-ghost" type="button">PDF</button>
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
                <button className="button button-primary" type="button">Confirm</button>
                <button className="button button-secondary" type="button">Pack</button>
                <button className="button button-secondary" type="button">Ship</button>
                <button className="button button-secondary" type="button">Deliver</button>
              </>
            ) : (
              <>
                <button className="button button-primary" type="button">Issue</button>
                <button className="button button-secondary" type="button">Receive</button>
              </>
            )}
            <button className="button button-ghost" type="button">Email</button>
            <button className="button button-ghost" type="button">Clone</button>
            <button className="button button-ghost" type="button">Cancel</button>
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
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Northstar Mesh Chair</td>
                <td>Central Warehouse</td>
                <td>12</td>
                <td>$199</td>
                <td>$2,388</td>
              </tr>
              <tr>
                <td>Orbit Monitor Arm</td>
                <td>Central Warehouse</td>
                <td>8</td>
                <td>$140</td>
                <td>$1,120</td>
              </tr>
            </tbody>
          </table>
        </div>
      </DashboardWidget>
    </div>
  );
}
