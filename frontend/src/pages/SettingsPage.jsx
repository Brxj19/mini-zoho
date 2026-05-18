import { useAuth } from "../contexts/AuthContext";

export function SettingsPage() {
  const { user, tenant } = useAuth();

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Workspace Settings</p>
          <h2>Platform Controls</h2>
          <p>Profile context, workspace identity, and backend operating rails at a glance.</p>
        </div>
      </section>

      <section className="detail-grid">
        <article className="workspace-card">
          <div className="card-header-row">
            <h3>Signed-in user</h3>
          </div>
          <div className="kv-grid">
            <div className="kv-item">
              <span>Name</span>
              <strong>{user?.name}</strong>
            </div>
            <div className="kv-item">
              <span>Email</span>
              <strong>{user?.email}</strong>
            </div>
            <div className="kv-item">
              <span>Role</span>
              <strong>{user?.role?.replaceAll("_", " ")}</strong>
            </div>
            <div className="kv-item">
              <span>Tenant</span>
              <strong>{tenant?.company_name ?? "Platform"}</strong>
            </div>
          </div>
        </article>

        <article className="workspace-card">
          <div className="card-header-row">
            <h3>Backend rails</h3>
          </div>
          <ul className="notes-list">
            <li>Tenant isolation is enforced in the API layer.</li>
            <li>Request IDs and response timing are available through middleware.</li>
            <li>Notifications, reports, and audit logs are active in the current workspace.</li>
            <li>Phase 9 focuses on making the operating UI feel cohesive and fast.</li>
          </ul>
        </article>
      </section>
    </div>
  );
}
