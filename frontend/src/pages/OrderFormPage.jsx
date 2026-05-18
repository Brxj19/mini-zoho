import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../lib/api";
import { FormRow } from "../components/FormRow";
import { FormSection } from "../components/FormSection";
import { PageHeader } from "../components/PageHeader";

function buildEmptyLine(defaultWarehouse = "") {
  return {
    item_name: "",
    warehouse_name: defaultWarehouse,
    quantity: 1,
    rate: "",
  };
}

export function OrderFormPage({ type }) {
  const isSales = type === "sales";
  const navigate = useNavigate();
  const [counterpartOptions, setCounterpartOptions] = useState([]);
  const [itemOptions, setItemOptions] = useState([]);
  const [warehouseOptions, setWarehouseOptions] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState("");
  const [form, setForm] = useState({
    counterpart: "",
    reference: "",
    orderDate: new Date().toISOString().slice(0, 10),
    expectedDate: "",
    notes: "",
    terms: "",
    lines: [buildEmptyLine("")],
  });

  useEffect(() => {
    async function loadOptions() {
      try {
        const [counterpartsResponse, itemsResponse, warehousesResponse] = await Promise.all([
          api.get(`/app/${isSales ? "customers" : "vendors"}`),
          api.get("/app/items"),
          api.get("/app/warehouses"),
        ]);
        const warehouses = warehousesResponse.data.rows ?? [];
        setCounterpartOptions(counterpartsResponse.data.rows ?? []);
        setItemOptions(itemsResponse.data.rows ?? []);
        setWarehouseOptions(warehouses);
        setForm((current) => ({
          ...current,
          counterpart: current.counterpart || counterpartsResponse.data.rows?.[0]?.name || "",
          lines: current.lines.map((line, index) =>
            index === 0 && !line.warehouse_name
              ? { ...line, warehouse_name: warehouses[0]?.name || "" }
              : line
          ),
        }));
      } catch {
        setFormError("Unable to load order form options right now.");
      }
    }

    loadOptions();
  }, [isSales]);

  const totals = useMemo(() => {
    const subtotal = form.lines.reduce((sum, line) => {
      const quantity = Number(line.quantity) || 0;
      const rate = Number(line.rate) || 0;
      return sum + quantity * rate;
    }, 0);

    return {
      subtotal,
      total: subtotal,
    };
  }, [form.lines]);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function updateLine(index, field, value) {
    setForm((current) => ({
      ...current,
      lines: current.lines.map((line, lineIndex) => (lineIndex === index ? { ...line, [field]: value } : line)),
    }));
  }

  function addLine() {
    setForm((current) => ({
      ...current,
      lines: [...current.lines, buildEmptyLine(warehouseOptions[0]?.name || "")],
    }));
  }

  function removeLine(index) {
    setForm((current) => ({
      ...current,
      lines: current.lines.length === 1 ? current.lines : current.lines.filter((_, lineIndex) => lineIndex !== index),
    }));
  }

  function validateForm() {
    if (!form.counterpart) {
      return `Please select a ${isSales ? "customer" : "vendor"}.`;
    }
    if (form.lines.some((line) => !line.item_name || !line.quantity || !line.rate)) {
      return "Each order line needs an item, quantity, and rate.";
    }
    return "";
  }

  async function submitOrder(statusValue) {
    const validationMessage = validateForm();
    if (validationMessage) {
      setFormError(validationMessage);
      return;
    }

    setIsSubmitting(true);
    setFormError("");
    try {
      const payload = {
        reference_number: form.reference || null,
        order_date: form.orderDate,
        notes: [form.notes, form.terms].filter(Boolean).join("\n\n"),
        items: form.lines.map((line) => ({
          item_name: line.item_name,
          warehouse_name: line.warehouse_name || null,
          quantity: Number(line.quantity),
          rate: Number(line.rate),
        })),
        status: statusValue,
      };

      const endpoint = isSales ? "/app/sales-orders" : "/app/purchase-orders";
      const requestBody = isSales
        ? {
            ...payload,
            customer_name: form.counterpart,
            expected_shipment_date: form.expectedDate || null,
          }
        : {
            ...payload,
            vendor_name: form.counterpart,
            expected_delivery_date: form.expectedDate || null,
          };

      const { data } = await api.post(endpoint, requestBody);
      const targetPath = isSales ? `/sales-orders/${data.id}` : `/purchase-orders/${data.id}`;
      navigate(targetPath);
    } catch (error) {
      setFormError(error.response?.data?.detail ?? "Unable to save the order right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={isSales ? "Sales Orders" : "Purchase Orders"}
        title={isSales ? "New Sales Order" : "New Purchase Order"}
        description="Create a real order record with grouped sections, line items, totals, and workflow-ready actions."
      />

      <form className="form-shell" onSubmit={(event) => event.preventDefault()}>
        <FormSection title={isSales ? "Customer and Order Information" : "Vendor and PO Information"}>
          <FormRow>
            <label>
              {isSales ? "Customer" : "Vendor"}
              <select value={form.counterpart} onChange={(event) => updateField("counterpart", event.target.value)}>
                <option value="">Select {isSales ? "customer" : "vendor"}</option>
                {counterpartOptions.map((option) => (
                  <option key={option.id} value={option.name}>
                    {option.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Reference#
              <input value={form.reference} onChange={(event) => updateField("reference", event.target.value)} placeholder={isSales ? "REF-4902" : "V-3813"} />
            </label>
          </FormRow>

          <FormRow>
            <label>
              {isSales ? "Order Date" : "PO Date"}
              <input type="date" value={form.orderDate} onChange={(event) => updateField("orderDate", event.target.value)} />
            </label>
            <label>
              {isSales ? "Expected Shipment Date" : "Expected Delivery"}
              <input type="date" value={form.expectedDate} onChange={(event) => updateField("expectedDate", event.target.value)} />
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
                  <th>Amount</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {form.lines.map((line, index) => {
                  const lineAmount = (Number(line.quantity) || 0) * (Number(line.rate) || 0);
                  return (
                    <tr key={`line-${index}`}>
                      <td>
                        <select value={line.item_name} onChange={(event) => updateLine(index, "item_name", event.target.value)}>
                          <option value="">Select item</option>
                          {itemOptions.map((item) => (
                            <option key={item.id} value={item.name}>
                              {item.name}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <select value={line.warehouse_name} onChange={(event) => updateLine(index, "warehouse_name", event.target.value)}>
                          <option value="">Select warehouse</option>
                          {warehouseOptions.map((warehouse) => (
                            <option key={warehouse.id} value={warehouse.name}>
                              {warehouse.name}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <input type="number" min="1" value={line.quantity} onChange={(event) => updateLine(index, "quantity", event.target.value)} />
                      </td>
                      <td>
                        <input type="number" min="0" step="0.01" value={line.rate} onChange={(event) => updateLine(index, "rate", event.target.value)} placeholder="0.00" />
                      </td>
                      <td>₹{lineAmount.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</td>
                      <td>
                        <button className="button button-ghost" type="button" onClick={() => removeLine(index)}>
                          Remove
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <button className="button button-ghost" type="button" onClick={addLine}>
            Add another line
          </button>
        </FormSection>

        <div className="form-two-column">
          <FormSection title="Notes and Terms">
            <label>
              Notes
              <textarea value={form.notes} onChange={(event) => updateField("notes", event.target.value)} placeholder="Delivery notes, dispatch expectations, or receiving instructions." />
            </label>
            <label>
              Terms
              <textarea value={form.terms} onChange={(event) => updateField("terms", event.target.value)} placeholder="Commercial terms, payment notes, or internal reminders." />
            </label>
            <label>
              Attach files
              <input value="Attachment support placeholder" readOnly />
            </label>
          </FormSection>

          <FormSection title="Totals">
            <div className="totals-panel">
              <div><span>Subtotal</span><strong>₹{totals.subtotal.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</strong></div>
              <div><span>Discount</span><strong>₹0.00</strong></div>
              <div><span>Shipping</span><strong>₹0.00</strong></div>
              <div><span>Adjustment</span><strong>₹0.00</strong></div>
              <div><span>Tax</span><strong>Included in line rate</strong></div>
              <div className="totals-grand"><span>Total</span><strong>₹{totals.total.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</strong></div>
            </div>
          </FormSection>
        </div>

        {formError ? <div className="form-error">{formError}</div> : null}

        <div className="sticky-form-bar">
          <div className="sticky-form-actions">
            <button className="button button-primary" type="button" disabled={isSubmitting} onClick={() => submitOrder("DRAFT")}>
              {isSales ? "Save as Draft" : "Save"}
            </button>
            <button className="button button-secondary" type="button" disabled={isSubmitting} onClick={() => submitOrder(isSales ? "CONFIRMED" : "ISSUED")}>
              {isSales ? "Confirm" : "Issue"}
            </button>
            <button className="button button-ghost" type="button" disabled={isSubmitting} onClick={() => submitOrder(isSales ? "CONFIRMED" : "RECEIVED")}>
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
