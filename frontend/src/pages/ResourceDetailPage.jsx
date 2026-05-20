import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { Tabs } from "../components/Tabs";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";
import { formatCurrency, formatDate, formatDateTime, titleCase } from "../lib/format";
import { hasAnyRole } from "../lib/permissions";
import { StatusBadge } from "../components/StatusBadge";

const inventoryRoles = ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER"];
const salesRoles = ["SUPER_ADMIN", "TENANT_ADMIN", "SALES_STAFF"];
const purchaseRoles = ["SUPER_ADMIN", "TENANT_ADMIN", "INVENTORY_MANAGER", "PURCHASE_STAFF"];
const adminRoles = ["SUPER_ADMIN", "TENANT_ADMIN"];
const superAdminRoles = ["SUPER_ADMIN"];

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
    editRoles: inventoryRoles,
  },
  warehouse: {
    title: "Warehouse Detail",
    endpoint: (id) => `/warehouses/${id}`,
    editPath: (id) => `/warehouses/${id}/edit`,
    listPath: "/warehouses",
    editRoles: inventoryRoles,
  },
  category: {
    title: "Category Detail",
    endpoint: (id) => `/categories/${id}`,
    editPath: (id) => `/categories/${id}/edit`,
    listPath: "/categories",
    editRoles: inventoryRoles,
  },
  brand: {
    title: "Brand Detail",
    endpoint: (id) => `/brands/${id}`,
    editPath: (id) => `/brands/${id}/edit`,
    listPath: "/brands",
    editRoles: inventoryRoles,
  },
  vendor: {
    title: "Vendor Detail",
    endpoint: (id) => `/vendors/${id}`,
    editPath: (id) => `/vendors/${id}/edit`,
    listPath: "/vendors",
    editRoles: purchaseRoles,
  },
  customer: {
    title: "Customer Detail",
    endpoint: (id) => `/customers/${id}`,
    editPath: (id) => `/customers/${id}/edit`,
    listPath: "/customers",
    editRoles: salesRoles,
  },
  user: {
    title: "User Detail",
    endpoint: (id) => `/users/${id}`,
    editPath: (id) => `/users/${id}/edit`,
    listPath: "/users",
    editRoles: adminRoles,
  },
  tenant: {
    title: "Tenant Detail",
    endpoint: (id) => `/tenants/${id}`,
    supplementary: (id) => [{ key: "usage", endpoint: `/tenants/${id}/usage` }],
    editPath: (id) => `/tenants/${id}/edit`,
    listPath: "/tenants",
    editRoles: superAdminRoles,
  },
  stockTransfer: {
    title: "Stock Transfer Detail",
    endpoint: (id) => `/inventory/transfers/${id}`,
    editPath: (id) => `/inventory/transfers/${id}/edit`,
    canEdit: (record) => record?.status === "DRAFT",
    listPath: "/inventory/transfers",
    editRoles: inventoryRoles,
  },
  purchaseOrder: {
    title: "Purchase Order Detail",
    endpoint: (id) => `/purchase-orders/${id}`,
    editPath: (id) => `/purchase-orders/${id}/edit`,
    canEdit: (record) => record?.status === "DRAFT",
    listPath: "/purchase-orders",
    editRoles: purchaseRoles,
  },
  salesOrder: {
    title: "Sales Order Detail",
    endpoint: (id) => `/sales-orders/${id}`,
    editPath: (id) => `/sales-orders/${id}/edit`,
    canEdit: (record) => record?.status === "DRAFT",
    listPath: "/sales-orders",
    editRoles: salesRoles,
  },
  package: {
    title: "Package Detail",
    endpoint: (id) => `/packages/${id}`,
    listPath: "/packages",
    editRoles: salesRoles,
  },
  invoice: {
    title: "Invoice Detail",
    endpoint: (id) => `/invoices/${id}`,
    listPath: "/invoices",
    editRoles: salesRoles,
  },
  salesReturn: {
    title: "Sales Return Detail",
    endpoint: (id) => `/sales-returns/${id}`,
    listPath: "/sales-returns",
    editRoles: salesRoles,
  },
  purchaseReceive: {
    title: "Purchase Receive Detail",
    endpoint: (id) => `/purchase-receives/${id}`,
    listPath: "/purchase-receives",
    editRoles: purchaseRoles,
  },
  bill: {
    title: "Bill Detail",
    endpoint: (id) => `/bills/${id}`,
    listPath: "/bills",
    editRoles: purchaseRoles,
  },
};

const workflowConfigs = {
  stockTransfer: {
    title: "Transfer Progress",
    steps: ["DRAFT", "IN_TRANSIT", "COMPLETED"],
    actionRoles: inventoryRoles,
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
    actionRoles: purchaseRoles,
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
    actionRoles: salesRoles,
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
  package: {
    title: "Package Timeline",
    steps: ["DRAFT", "PACKED", "SHIPPED", "DELIVERED"],
    actionRoles: salesRoles,
    actions: (record, id) => {
      const actions = [];
      if (record.status === "DRAFT") {
        actions.push({ type: "request", label: "Mark Packed", endpoint: `/packages/${id}/pack`, successMessage: "Package marked as packed." });
        actions.push({ type: "request", label: "Cancel Package", endpoint: `/packages/${id}/cancel`, tone: "danger", successMessage: "Package cancelled." });
      }
      if (record.status === "PACKED") {
        actions.push({ type: "request", label: "Mark Shipped", endpoint: `/packages/${id}/ship`, successMessage: "Package marked as shipped." });
        actions.push({ type: "request", label: "Cancel Package", endpoint: `/packages/${id}/cancel`, tone: "danger", successMessage: "Package cancelled." });
      }
      if (record.status === "SHIPPED") {
        actions.push({ type: "request", label: "Mark Delivered", endpoint: `/packages/${id}/deliver`, successMessage: "Package delivered." });
      }
      return actions;
    },
  },
  invoice: {
    title: "Invoice Timeline",
    steps: ["DRAFT", "SENT", "PAID"],
    actionRoles: salesRoles,
    actions: (record, id) => {
      const actions = [];
      if (record.status === "DRAFT") {
        actions.push({ type: "request", label: "Send Invoice", endpoint: `/invoices/${id}/send`, successMessage: "Invoice marked as sent." });
        actions.push({ type: "request", label: "Void Invoice", endpoint: `/invoices/${id}/void`, tone: "danger", successMessage: "Invoice voided." });
      }
      if (record.status === "SENT") {
        actions.push({ type: "request", label: "Mark Paid", endpoint: `/invoices/${id}/pay`, successMessage: "Invoice marked as paid." });
        actions.push({ type: "request", label: "Void Invoice", endpoint: `/invoices/${id}/void`, tone: "danger", successMessage: "Invoice voided." });
      }
      return actions;
    },
  },
  salesReturn: {
    title: "Return Timeline",
    steps: ["DRAFT", "RECEIVED", "REFUNDED"],
    actionRoles: salesRoles,
    actions: (record, id) => {
      const actions = [];
      if (record.status === "DRAFT") {
        actions.push({ type: "request", label: "Receive Return", endpoint: `/sales-returns/${id}/receive`, successMessage: "Returned stock received back into inventory." });
        actions.push({ type: "request", label: "Cancel Return", endpoint: `/sales-returns/${id}/cancel`, tone: "danger", successMessage: "Sales return cancelled." });
      }
      if (record.status === "RECEIVED") {
        actions.push({ type: "request", label: "Mark Refunded", endpoint: `/sales-returns/${id}/refund`, successMessage: "Sales return marked as refunded." });
      }
      return actions;
    },
  },
  bill: {
    title: "Bill Timeline",
    steps: ["DRAFT", "POSTED", "PAID"],
    actionRoles: purchaseRoles,
    actions: (record, id) => {
      const actions = [];
      if (record.status === "DRAFT") {
        actions.push({ type: "request", label: "Post Bill", endpoint: `/bills/${id}/post`, successMessage: "Bill posted." });
        actions.push({ type: "request", label: "Void Bill", endpoint: `/bills/${id}/void`, tone: "danger", successMessage: "Bill voided." });
      }
      if (record.status === "POSTED") {
        actions.push({ type: "request", label: "Mark Paid", endpoint: `/bills/${id}/pay`, successMessage: "Bill marked as paid." });
        actions.push({ type: "request", label: "Void Bill", endpoint: `/bills/${id}/void`, tone: "danger", successMessage: "Bill voided." });
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

function getRecordHeadline(detailKey, record, fallbackTitle) {
  if (!record) return fallbackTitle;
  if (detailKey === "salesOrder") return record.so_number ?? fallbackTitle;
  if (detailKey === "purchaseOrder") return record.po_number ?? fallbackTitle;
  if (detailKey === "package") return record.package_number ?? fallbackTitle;
  if (detailKey === "invoice") return record.invoice_number ?? fallbackTitle;
  if (detailKey === "salesReturn") return record.return_number ?? fallbackTitle;
  if (detailKey === "purchaseReceive") return record.receive_number ?? fallbackTitle;
  if (detailKey === "bill") return record.bill_number ?? fallbackTitle;
  if (detailKey === "customer" || detailKey === "vendor" || detailKey === "brand" || detailKey === "category" || detailKey === "warehouse" || detailKey === "user") {
    return record.name ?? fallbackTitle;
  }
  if (detailKey === "tenant") return record.company_name ?? fallbackTitle;
  return fallbackTitle;
}

function getRecordDescription(detailKey, record) {
  if (!record) return "Key record details, line items, and related operational activity.";
  if (detailKey === "salesOrder") return "Review customer order context, timeline progress, and warehouse-backed order lines.";
  if (detailKey === "purchaseOrder") return "Review vendor commitments, receiving progress, and inbound line quantities.";
  if (detailKey === "package") return "Track packing, shipping, and final delivery against the originating sales order.";
  if (detailKey === "invoice") return "Review billing progress, due dates, and linked sales context.";
  if (detailKey === "salesReturn") return "Manage the reverse-logistics journey from received goods to refund completion.";
  if (detailKey === "purchaseReceive") return "Confirm warehouse receipt postings against the linked purchase order.";
  if (detailKey === "bill") return "Track payable milestones and commercial context for the linked procurement record.";
  if (detailKey === "customer") return "Customer profile, order relationships, and activity context for the sales workspace.";
  if (detailKey === "vendor") return "Vendor profile, procurement context, and payable-facing details for purchasing teams.";
  return "Key record details, line items, and related operational activity.";
}

function buildSummaryCards(detailKey, record, usage, stockRows, itemRows) {
  if (!record) return [];

  if (detailKey === "salesOrder") {
    return [
      { label: "Status", value: titleCase(record.status), helper: "Current order stage" },
      { label: "Customer", value: record.customer_id ? `Customer #${record.customer_id}` : "—", helper: record.order_date ? `Created ${formatDate(record.order_date)}` : "Customer linkage" },
      { label: "Total", value: formatCurrency(record.total_amount), helper: `${itemRows.length} order lines` },
      { label: "Discount", value: formatCurrency(record.discount_amount), helper: "Applied at order level" },
    ];
  }

  if (detailKey === "purchaseOrder") {
    return [
      { label: "Status", value: titleCase(record.status), helper: "Current procurement stage" },
      { label: "Vendor", value: record.vendor_id ? `Vendor #${record.vendor_id}` : "—", helper: record.expected_delivery_date ? `Expected ${formatDate(record.expected_delivery_date)}` : "Vendor linkage" },
      { label: "Total", value: formatCurrency(record.total_amount), helper: `${itemRows.length} incoming lines` },
      { label: "Notes", value: record.notes ? "Available" : "—", helper: "Purchase context" },
    ];
  }

  if (["package", "invoice", "salesReturn", "purchaseReceive", "bill"].includes(detailKey)) {
    return [
      { label: "Status", value: titleCase(record.status), helper: "Workflow stage" },
      { label: "Linked Order", value: record.sales_order_id ? `SO #${record.sales_order_id}` : record.purchase_order_id ? `PO #${record.purchase_order_id}` : "—", helper: "Source document" },
      { label: "Line Items", value: String(itemRows.length), helper: "Attached workflow rows" },
      { label: "Total", value: record.total_amount != null ? formatCurrency(record.total_amount) : "—", helper: "Commercial value if available" },
    ];
  }

  if (detailKey === "customer" || detailKey === "vendor") {
    return [
      { label: "Status", value: titleCase(record.status), helper: "Directory state" },
      { label: "Email", value: record.email || "—", helper: "Primary communication" },
      { label: "Phone", value: record.phone || "—", helper: "Contact number" },
      { label: "GST", value: record.gst_number || "—", helper: detailKey === "vendor" ? "Procurement tax profile" : "Sales tax profile" },
    ];
  }

  if (detailKey === "tenant" && usage) {
    return [
      { label: "Plan", value: usage.plan_name ?? "Unassigned", helper: "Assigned subscription" },
      { label: "Users", value: String(usage.total_users ?? 0), helper: `${usage.active_users ?? 0} active` },
      { label: "Products", value: String(usage.total_products ?? 0), helper: "Catalog records" },
      { label: "Orders", value: String(usage.total_orders ?? 0), helper: "Combined purchase and sales" },
    ];
  }

  if (detailKey === "product") {
    return [
      { label: "Status", value: titleCase(record.status), helper: "Catalog state" },
      { label: "SKU", value: record.sku || "—", helper: "Stock keeping unit" },
      { label: "Barcode", value: record.barcode || "—", helper: "Scan/search ready" },
      { label: "Warehouses", value: String(stockRows.length), helper: "Active stock locations" },
    ];
  }

  return [
    { label: "Status", value: record.status ? titleCase(record.status) : "—", helper: "Current state" },
    { label: "Created", value: formatDate(record.created_at ?? record.order_date), helper: "Record milestone" },
  ];
}

function getDocumentConfig(detailKey, record, id) {
  if (detailKey === "invoice" && record?.invoice_number) {
    return {
      endpoint: `/invoices/${id}/pdf`,
      emailEndpoint: `/invoices/${id}/email`,
      filename: `${record.invoice_number}.pdf`,
      successMessage: `Invoice ${record.invoice_number} emailed successfully.`,
      emailLabel: "Email Invoice",
      downloadLabel: "Download PDF",
    };
  }

  if (detailKey === "bill" && record?.bill_number) {
    return {
      endpoint: `/bills/${id}/pdf`,
      emailEndpoint: `/bills/${id}/email`,
      filename: `${record.bill_number}.pdf`,
      successMessage: `Bill ${record.bill_number} emailed successfully.`,
      emailLabel: "Email Bill",
      downloadLabel: "Download PDF",
    };
  }

  return null;
}

async function getErrorMessage(error, fallbackMessage) {
  const response = error?.response;
  const blob = response?.data;

  if (blob instanceof Blob) {
    try {
      const text = await blob.text();
      const parsed = JSON.parse(text);
      return parsed?.detail || parsed?.error || fallbackMessage;
    } catch {
      return fallbackMessage;
    }
  }

  return response?.data?.detail ?? fallbackMessage;
}

export function ResourceDetailPage({ detailKey, paramKey }) {
  const { [paramKey]: entityId } = useParams();
  const { user } = useAuth();
  const config = detailConfigs[detailKey];
  const workflow = workflowConfigs[detailKey];
  const [reloadKey, setReloadKey] = useState(0);
  const [activeTab, setActiveTab] = useState("overview");
  const [state, setState] = useState({
    loading: true,
    error: "",
    record: null,
    supplementary: {},
  });
  const [feedback, setFeedback] = useState({ success: "" });
  const [modal, setModal] = useState(null);
  const [actionState, setActionState] = useState({ submitting: false, error: "" });
  const [documentState, setDocumentState] = useState({ downloading: false, emailing: false, error: "" });

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
  const usage = state.supplementary.usage ?? null;
  const showsLineItems = ["purchaseOrder", "salesOrder", "stockTransfer", "package", "salesReturn", "purchaseReceive"].includes(detailKey);
  const canRunWorkflowActions = hasAnyRole(user, workflow?.actionRoles);
  const workflowActions = workflow && state.record && canRunWorkflowActions ? workflow.actions(state.record, entityId) : [];
  const canEdit =
    config.editPath &&
    state.record &&
    hasAnyRole(user, config.editRoles) &&
    (config.canEdit ? config.canEdit(state.record) : true);
  const headerTitle = getRecordHeadline(detailKey, state.record, config.title);
  const headerDescription = getRecordDescription(detailKey, state.record);
  const summaryCards = buildSummaryCards(detailKey, state.record, usage, stockRows, itemRows);
  const documentConfig = useMemo(() => getDocumentConfig(detailKey, state.record, entityId), [detailKey, entityId, state.record]);
  const tabItems = useMemo(() => {
    const items = [{ key: "overview", label: "Overview" }];
    if (itemRows.length || showsLineItems) items.push({ key: "lines", label: "Line Items" });
    if (transactionRows.length || detailKey === "customer" || detailKey === "vendor" || workflow) items.push({ key: "activity", label: "Activity" });
    return items;
  }, [detailKey, itemRows.length, showsLineItems, transactionRows.length, workflow]);

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

  async function handleDownloadPdf() {
    if (!documentConfig) return;
    setDocumentState({ downloading: true, emailing: false, error: "" });

    try {
      const response = await api.get(documentConfig.endpoint, { responseType: "blob" });
      const blobUrl = window.URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = documentConfig.filename;
      document.body.append(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
      setDocumentState({ downloading: false, emailing: false, error: "" });
      setFeedback({ success: `${documentConfig.filename} downloaded.` });
    } catch (error) {
      setDocumentState({
        downloading: false,
        emailing: false,
        error: await getErrorMessage(error, "Unable to download the PDF right now."),
      });
    }
  }

  async function handleEmailDocument() {
    if (!documentConfig) return;
    setDocumentState({ downloading: false, emailing: true, error: "" });

    try {
      await api.post(documentConfig.emailEndpoint, { notes: state.record?.notes || null });
      setDocumentState({ downloading: false, emailing: false, error: "" });
      setFeedback({ success: documentConfig.successMessage });
      setReloadKey((value) => value + 1);
    } catch (error) {
      setDocumentState({
        downloading: false,
        emailing: false,
        error: await getErrorMessage(error, "Unable to email the document right now."),
      });
    }
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
      <PageHeader
        eyebrow={workflow ? "Operational Workflow" : detailKey === "customer" ? "Sales Directory" : detailKey === "vendor" ? "Purchase Directory" : "Workspace Detail"}
        title={headerTitle}
        description={headerDescription}
        backTo={config.listPath ?? "/"}
        actions={
          <>
            {documentConfig ? (
              <>
                <button className="ghost-button" type="button" onClick={handleDownloadPdf} disabled={documentState.downloading || documentState.emailing}>
                  {documentState.downloading ? "Downloading..." : documentConfig.downloadLabel}
                </button>
                <button className="button button-primary" type="button" onClick={handleEmailDocument} disabled={documentState.downloading || documentState.emailing}>
                  {documentState.emailing ? "Sending..." : documentConfig.emailLabel}
                </button>
              </>
            ) : null}
            {canEdit ? (
              <Link className="ghost-button" to={config.editPath(entityId)}>
                Edit
              </Link>
            ) : null}
          </>
        }
      />

      {feedback.success ? <div className="surface-success">{feedback.success}</div> : null}
      {documentState.error ? <div className="surface-error">{documentState.error}</div> : null}
      {state.loading ? <div className="workspace-card surface-placeholder">Loading detail…</div> : null}
      {!state.loading && state.error ? (
        <EmptyState
          icon="alert"
          title="Unable to load record details"
          description={state.error}
          actionLabel="Try Again"
          onAction={() => setReloadKey((value) => value + 1)}
          actionTone="ghost"
        />
      ) : null}

      {!state.loading && state.record ? (
        <>
          {summaryCards.length ? (
            <section className="commercial-summary-grid">
              {summaryCards.map((card) => (
                <article className="commercial-summary-card" key={card.label}>
                  <span>{card.label}</span>
                  <strong>{card.value}</strong>
                  <p>{card.helper}</p>
                </article>
              ))}
            </section>
          ) : null}

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
              ) : canRunWorkflowActions ? (
                <div className="surface-placeholder">No further operational actions are available for the current status.</div>
              ) : (
                <div className="surface-placeholder">You have read-only access to this workflow. Ask an administrator for operational permissions if you need to progress it.</div>
              )}
            </section>
          ) : null}

          <Tabs items={tabItems} activeKey={activeTab} onChange={setActiveTab} />

          {activeTab === "overview" ? (
            <section className="detail-grid">
              <article className="workspace-card">
                <div className="card-header-row">
                  <h3>Overview</h3>
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

              {detailKey === "tenant" && usage ? (
                <article className="workspace-card">
                  <div className="card-header-row">
                    <h3>Usage Snapshot</h3>
                  </div>
                  <div className="kv-grid">
                    <div className="kv-item">
                      <span>Total users</span>
                      <strong>{usage.total_users}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Active users</span>
                      <strong>{usage.active_users}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Products</span>
                      <strong>{usage.total_products}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Warehouses</span>
                      <strong>{usage.total_warehouses}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Sales orders</span>
                      <strong>{usage.total_sales_orders}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Purchase orders</span>
                      <strong>{usage.total_purchase_orders}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Stock transfers</span>
                      <strong>{usage.total_stock_transfers}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Total orders</span>
                      <strong>{usage.total_orders}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Assigned plan</span>
                      <strong>{usage.plan_name ?? "Unassigned"}</strong>
                    </div>
                  </div>
                </article>
              ) : null}

              {detailKey === "user" && state.record?.tenant ? (
                <article className="workspace-card">
                  <div className="card-header-row">
                    <h3>Tenant Access</h3>
                  </div>
                  <div className="kv-grid">
                    <div className="kv-item">
                      <span>Company</span>
                      <strong>{state.record.tenant.company_name}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Tenant status</span>
                      <strong><StatusBadge value={state.record.tenant.status} /></strong>
                    </div>
                    <div className="kv-item">
                      <span>Contact email</span>
                      <strong>{state.record.tenant.contact_email}</strong>
                    </div>
                    <div className="kv-item">
                      <span>Business type</span>
                      <strong>{state.record.tenant.business_type ?? "—"}</strong>
                    </div>
                  </div>
                </article>
              ) : null}
            </section>
          ) : null}

          {activeTab === "lines" ? (
            itemRows.length > 0 ? (
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
            ) : (
              <section className="workspace-card surface-empty">No line items are attached to this record.</section>
            )
          ) : null}

          {activeTab === "activity" ? (
            transactionRows.length > 0 ? (
              <section className="workspace-card">
                <div className="card-header-row">
                  <h3>{detailKey === "product" ? "Recent Movement" : "Recent Activity"}</h3>
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
            ) : (
              <section className="workspace-card surface-empty">
                {workflow
                  ? "Workflow activity will appear here as the record progresses."
                  : detailKey === "customer" || detailKey === "vendor"
                    ? "Related notes and recent activity will appear here once connected workflows start using this record."
                    : "No recent movement has been recorded for this record yet."}
              </section>
            )
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
