export function MetricCard({ label, value, delta, tone = "neutral" }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <p className={`metric-delta tone-${tone}`}>{delta}</p>
    </article>
  );
}
