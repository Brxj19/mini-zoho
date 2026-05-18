import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../lib/api";
import { DashboardWidget } from "../components/DashboardWidget";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";

export function WarehouseDetailPage() {
  const { warehouseId } = useParams();
  const navigate = useNavigate();
  const [warehouse, setWarehouse] = useState(null);

  useEffect(() => {
    api.get(`/app/warehouses/${warehouseId}`).then(({ data }) => setWarehouse(data)).catch(() => setWarehouse(null));
  }, [warehouseId]);

  if (!warehouse) {
    return (
      <EmptyState
        icon="warehouse"
        title="Warehouse not found"
        description="This warehouse record is not available."
        actionLabel="Back to warehouses"
        actionTo="/warehouses"
      />
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Warehouse Detail"
        title={warehouse.name}
        description={`${warehouse.location} • Managed by ${warehouse.manager}`}
        actions={
          <div className="header-inline-chips">
            {warehouse.primary ? <span className="status-pill is-info">Primary Warehouse</span> : null}
            <StatusBadge status={warehouse.status} />
          </div>
        }
      />

      <section className="detail-grid">
        <DashboardWidget title="Warehouse Actions">
          <div className="stack-actions">
            <button className="button button-primary" type="button" onClick={() => navigate("/stock-transfers")}>Transfer Stock</button>
            <button className="button button-secondary" type="button" onClick={() => navigate("/settings?section=warehouses")}>Mark as Primary</button>
            <button className="button button-ghost" type="button" onClick={() => navigate("/inventory-adjustments")}>Activate / Deactivate</button>
          </div>
        </DashboardWidget>

        <DashboardWidget title="Snapshot" className="widget-span-2">
          <div className="detail-overview-grid">
            <div><span>Items in Stock</span><strong>{warehouse.stockCount}</strong></div>
            <div><span>Status</span><strong>{warehouse.status}</strong></div>
            <div><span>Primary</span><strong>{warehouse.primary ? "Yes" : "No"}</strong></div>
            <div><span>Manager</span><strong>{warehouse.manager}</strong></div>
          </div>
        </DashboardWidget>
      </section>

      <DashboardWidget title="Stock by Item">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>SKU</th>
                <th>Category</th>
                <th>On Hand</th>
                <th>Reorder Level</th>
              </tr>
            </thead>
            <tbody>
              {(warehouse.items ?? []).map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td>{item.sku}</td>
                  <td>{item.category}</td>
                  <td>{item.stockOnHand}</td>
                  <td>{item.reorderLevel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DashboardWidget>

      <DashboardWidget title="Recent Transactions">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Product</th>
                <th>Reference</th>
                <th>Qty</th>
              </tr>
            </thead>
            <tbody>
              {(warehouse.transactions ?? []).map((transaction) => (
                <tr key={transaction.id}>
                  <td>{transaction.date}</td>
                  <td>{transaction.type}</td>
                  <td>{transaction.product}</td>
                  <td>{transaction.reference}</td>
                  <td>{transaction.quantity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DashboardWidget>
    </div>
  );
}
