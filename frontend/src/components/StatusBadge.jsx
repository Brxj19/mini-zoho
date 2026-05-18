export function StatusBadge({ status }) {
  const tone = getStatusTone(status);

  return (
    <span className={`status-badge status-${tone}`}>
      {String(status).replaceAll("_", " ")}
    </span>
  );
}

function getStatusTone(status) {
  const value = String(status).toUpperCase();

  if (["ACTIVE", "DELIVERED", "RECEIVED", "COMPLETED", "SUCCESS"].includes(value)) {
    return "success";
  }

  if (["CONFIRMED", "ISSUED", "INFO"].includes(value)) {
    return "info";
  }

  if (["PACKED", "IN_TRANSIT", "PARTIALLY_RECEIVED", "LOW_STOCK", "WARNING"].includes(value)) {
    return "warning";
  }

  if (["SHIPPED"].includes(value)) {
    return "purple";
  }

  if (["CANCELLED", "DISABLED", "INACTIVE", "DANGER", "VOID"].includes(value)) {
    return "danger";
  }

  return "neutral";
}
