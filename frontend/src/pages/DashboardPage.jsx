import { useAuth } from "../contexts/AuthContext";

const stats = [
  { label: "Products", value: "Phase 4", note: "Catalog and stock core are next after master data." },
  { label: "Warehouses", value: "Phase 3", note: "Tenant-owned locations arrive in the next milestone." },
  { label: "Purchase Orders", value: "Phase 6", note: "Inbound stock workflow is already mapped in the PRD." },
  { label: "Low Stock Alerts", value: "Phase 4", note: "Rules will key off warehouse stock and reorder levels." },
];

export function DashboardPage() {
  const { user, tenant } = useAuth();

  return (
    <div className="dashboard-grid">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Phase 2 Active</p>
          <h2>Auth, tenants, roles, and strict backend tenant isolation are now wired into the platform.</h2>
          <p>
            Signed in as <strong>{user?.name ?? "Unknown user"}</strong>
            {tenant ? ` for ${tenant.company_name}` : " in the platform workspace"}.
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
            <p className="eyebrow">Current Session</p>
            <h3>Access summary</h3>
          </div>
        </div>

        <ul className="milestone-list">
          <li>Role: {user?.role?.replaceAll("_", " ") ?? "Unknown"}</li>
          <li>Tenant status: {tenant?.status ?? "Platform-level access"}</li>
          <li>Contact email: {tenant?.contact_email ?? user?.email ?? "Unavailable"}</li>
          <li>Next milestone: master data modules for categories, brands, vendors, customers, and warehouses</li>
        </ul>
      </section>
    </div>
  );
}
