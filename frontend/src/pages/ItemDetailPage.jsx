import { useParams } from "react-router-dom";

import { DashboardWidget } from "../components/DashboardWidget";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { getCollection, getRecordById } from "../lib/demoData";

export function ItemDetailPage() {
  const { itemId } = useParams();
  const item = getRecordById("items", itemId);
  const transactions = getCollection("transactions").slice(0, 4);

  if (!item) {
    return (
      <EmptyState
        icon="box"
        title="Item not found"
        description="This item record is not present in the current UI data set."
        actionLabel="Back to items"
        actionTo="/items"
      />
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Item Detail"
        title={item.name}
        description={`${item.sku} • ${item.category} • ${item.brand}`}
        actions={
          <div className="header-inline-chips">
            <StatusBadge status={item.status} />
            <button className="button button-secondary" type="button">
              Print
            </button>
          </div>
        }
      />

      <section className="detail-grid">
        <DashboardWidget title="Overview" className="widget-span-2">
          <div className="detail-overview-grid">
            <div><span>Stock on Hand</span><strong>{item.stockOnHand}</strong></div>
            <div><span>Reorder Level</span><strong>{item.reorderLevel}</strong></div>
            <div><span>Selling Price</span><strong>{item.sellingPrice}</strong></div>
            <div><span>Cost Price</span><strong>{item.costPrice}</strong></div>
            <div><span>Barcode</span><strong>{item.barcode}</strong></div>
            <div><span>Unit</span><strong>{item.unit}</strong></div>
          </div>
          <p className="detail-copy">{item.description}</p>
        </DashboardWidget>

        <DashboardWidget title="Item Controls">
          <div className="stack-actions">
            <button className="button button-primary" type="button">Adjust Stock</button>
            <button className="button button-secondary" type="button">Transfer Stock</button>
            <button className="button button-ghost" type="button">Clone Item</button>
          </div>
        </DashboardWidget>
      </section>

      <DashboardWidget title="Recent Transactions">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Warehouse</th>
                <th>Reference</th>
                <th>Quantity</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td>{transaction.date}</td>
                  <td>{transaction.type}</td>
                  <td>{transaction.warehouse}</td>
                  <td>{transaction.reference}</td>
                  <td className={transaction.quantity.startsWith("-") ? "quantity-negative" : "quantity-positive"}>
                    {transaction.quantity}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DashboardWidget>
    </div>
  );
}
