export function formatLabel(value) {
  return String(value)
    .replaceAll("_", " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2");
}
