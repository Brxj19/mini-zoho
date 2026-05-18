import { Link } from "react-router-dom";

import { FormRow } from "../components/FormRow";
import { FormSection } from "../components/FormSection";
import { PageHeader } from "../components/PageHeader";

export function OrderFormPage({ type }) {
  const isSales = type === "sales";

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={isSales ? "Sales Orders" : "Purchase Orders"}
        title={isSales ? "New Sales Order" : "New Purchase Order"}
        description="Sectioned order entry with item table, notes, totals, and status-ready action controls."
      />

      <form className="form-shell">
        <FormSection title={isSales ? "Customer and Order Information" : "Vendor and PO Information"}>
          <FormRow>
            <label>
              {isSales ? "Customer" : "Vendor"}
              <input value={isSales ? "Horizon Interiors" : "Atlas Components"} readOnly />
            </label>
            <label>
              {isSales ? "Sales Order#" : "PO#"}
              <input value={isSales ? "SO-211" : "PO-205"} readOnly />
            </label>
          </FormRow>

          <FormRow>
            <label>
              Reference#
              <input defaultValue={isSales ? "REF-4902" : "V-3813"} />
            </label>
            <label>
              {isSales ? "Order Date" : "Expected Delivery"}
              <input type="date" defaultValue="2026-05-18" />
            </label>
          </FormRow>
        </FormSection>

        <FormSection title="Item Details">
          <div className="table-wrap">
            <table className="data-table order-lines-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Warehouse</th>
                  <th>Qty</th>
                  <th>Rate</th>
                  <th>Discount</th>
                  <th>Tax</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Northstar Mesh Chair</td>
                  <td>Central Warehouse</td>
                  <td>12</td>
                  <td>$199</td>
                  <td>5%</td>
                  <td>Placeholder</td>
                  <td>$2,268</td>
                </tr>
                <tr>
                  <td>Beacon Standing Desk</td>
                  <td>Central Warehouse</td>
                  <td>4</td>
                  <td>$499</td>
                  <td>0%</td>
                  <td>Placeholder</td>
                  <td>$1,996</td>
                </tr>
              </tbody>
            </table>
          </div>

          <button className="button button-ghost" type="button">
            Add another line
          </button>
        </FormSection>

        <div className="form-two-column">
          <FormSection title="Notes and Terms">
            <label>
              Notes
              <textarea defaultValue="Customer requires delivery confirmation before invoicing." />
            </label>
            <label>
              Terms
              <textarea defaultValue="Placeholder until full document policies are connected." />
            </label>
            <label>
              Attach files
              <input value="Attachment support placeholder" readOnly />
            </label>
          </FormSection>

          <FormSection title="Totals">
            <div className="totals-panel">
              <div><span>Subtotal</span><strong>$4,264</strong></div>
              <div><span>Discount</span><strong>-$110</strong></div>
              <div><span>Shipping</span><strong>$120</strong></div>
              <div><span>Adjustment</span><strong>$0</strong></div>
              <div><span>Tax</span><strong>Placeholder</strong></div>
              <div className="totals-grand"><span>Total</span><strong>$4,274</strong></div>
            </div>
          </FormSection>
        </div>

        <div className="sticky-form-bar">
          <div className="sticky-form-actions">
            <button className="button button-primary" type="button">
              {isSales ? "Save as Draft" : "Save"}
            </button>
            <button className="button button-secondary" type="button">
              {isSales ? "Confirm" : "Issue"}
            </button>
            <button className="button button-ghost" type="button">
              {isSales ? "Save and Send" : "Receive"}
            </button>
            <Link className="button button-ghost" to={isSales ? "/sales-orders" : "/purchase-orders"}>
              Cancel
            </Link>
          </div>
        </div>
      </form>
    </div>
  );
}
