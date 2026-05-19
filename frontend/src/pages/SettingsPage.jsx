import { useSearchParams } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import { useAuth } from "../contexts/AuthContext";
import { settingsNavigation } from "../lib/navigation";

export function SettingsPage() {
  const { user, tenant } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const section = searchParams.get("section") ?? "organization";
  const activeSection = settingsNavigation.find((item) => item.key === section) ?? settingsNavigation[0];

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Admin"
        title="Settings"
        description="Workspace profile, operational preferences, and account-level controls."
        backTo="/"
      />

      <div className="detail-grid">
        <section className="workspace-card">
          <div className="widget-header">
            <h2>Configuration Areas</h2>
          </div>
          <div className="settings-panel-nav">
            {settingsNavigation.map((item) => (
              <button
                key={item.key}
                className={`sidebar-link ${activeSection.key === item.key ? "is-active" : ""}`}
                type="button"
                onClick={() => setSearchParams({ section: item.key })}
              >
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="workspace-card">
          <div className="widget-header">
            <h2>{activeSection.label}</h2>
          </div>
          <div className="kv-grid">
            <div className="kv-item">
              <span>Organization</span>
              <strong>{tenant?.company_name ?? "Platform"}</strong>
            </div>
            <div className="kv-item">
              <span>Contact Email</span>
              <strong>{tenant?.contact_email ?? user?.email ?? "—"}</strong>
            </div>
            <div className="kv-item">
              <span>Current User</span>
              <strong>{user?.name ?? "—"}</strong>
            </div>
            <div className="kv-item">
              <span>Role</span>
              <strong>{user?.role?.replaceAll("_", " ") ?? "—"}</strong>
            </div>
          </div>
          {activeSection.key === "subscription" ? (
            <p>
              Subscription governance now has a dedicated workspace. Open the subscription module to manage plans,
              quotas, and tenant usage.
            </p>
          ) : null}
          <p>
            This section is structured for future module-specific settings. The shell and navigation are now in
            place so backend-backed settings can slot in without another redesign.
          </p>
        </section>
      </div>
    </div>
  );
}
