const stats = [
  { label: "Products", value: "0", note: "Catalog foundation ready" },
  { label: "Warehouses", value: "0", note: "Module scheduled in Phase 3" },
  { label: "Purchase Orders", value: "0", note: "Workflow starts in Phase 6" },
  { label: "Low Stock Alerts", value: "0", note: "Rules start in Phase 4" },
];

export function DashboardPage() {
  return (
    <div className="dashboard-grid">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Phase 1 Ready</p>
          <h2>Project foundation is in place for a tenant-isolated inventory platform.</h2>
          <p>
            The next milestone will add tenants, users, JWT auth, role guards, and backend isolation
            dependencies.
          </p>
        </div>
      </section>

      <section className="stats-grid">
        {stats.map((stat) => (
          <article className="stat-card" key={stat.label}>
            <span>{stat.label}</span>
            <strong>{stat.value}</strong>
            <p>{stat.note}</p>
          </article>
        ))}
      </section>

      <section className="panel-card">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Roadmap</p>
            <h3>Implementation milestones</h3>
          </div>
        </div>

        <ul className="milestone-list">
          <li>Phase 1: Project setup, Docker, env files, FastAPI, React, MySQL, Alembic</li>
          <li>Phase 2: Auth, roles, tenants, seed users, tenant isolation</li>
          <li>Phase 3: Categories, brands, vendors, customers, warehouses</li>
          <li>Phase 4+: Product, stock, transfers, orders, reports, audit logs, AI assistant</li>
        </ul>
      </section>
    </div>
  );
}

