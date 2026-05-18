export function DashboardWidget({ title, actions = null, children, className = "" }) {
  return (
    <section className={`widget-card ${className}`.trim()}>
      <div className="widget-header">
        <h2>{title}</h2>
        {actions}
      </div>
      <div className="widget-body">{children}</div>
    </section>
  );
}
