import { titleCase } from "../lib/format";

const toneMap = {
  ACTIVE: "success",
  RECEIVED: "success",
  DELIVERED: "success",
  COMPLETED: "success",
  CONFIRMED: "info",
  PACKED: "info",
  SHIPPED: "info",
  ISSUED: "info",
  IN_TRANSIT: "info",
  DRAFT: "muted",
  PARTIALLY_RECEIVED: "warning",
  CANCELLED: "danger",
  ARCHIVED: "danger",
  DISABLED: "danger",
  INACTIVE: "danger",
  LOW_STOCK: "warning",
};

export function StatusBadge({ value }) {
  const normalized = String(value ?? "Unknown").toUpperCase();
  const tone = toneMap[normalized] ?? "muted";
  return <span className={`status-badge status-badge-${tone}`}>{titleCase(value)}</span>;
}
