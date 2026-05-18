import { useSearchParams } from "react-router-dom";

import { FormRow } from "../components/FormRow";
import { FormSection } from "../components/FormSection";
import { Icon } from "../components/Icon";
import { PageHeader } from "../components/PageHeader";
import { settingsNavigation } from "../lib/navigation";

export function SettingsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeSection = searchParams.get("section") ?? "organization";

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Admin"
        title="Settings"
        description="Sub-navigation layout for organization profile, preferences, security, and future modules."
      />

      <div className="settings-layout">
        <aside className="settings-sidebar">
          {settingsNavigation.map((item) => (
            <button
              key={item.key}
              className={`settings-nav-link ${item.key === activeSection ? "is-active" : ""}`}
              type="button"
              onClick={() => setSearchParams({ section: item.key })}
            >
              <Icon name={item.icon} size={16} />
              <span>{item.label}</span>
            </button>
          ))}
        </aside>

        <div className="settings-content">
          <FormSection
            title={settingsNavigation.find((item) => item.key === activeSection)?.label ?? "Settings"}
            description="These sections are wired for layout consistency first, then ready for backend settings integration."
          >
            <FormRow>
              <label>
                Display Name
                <input defaultValue="Northstar Retail" />
              </label>
              <label>
                Primary Contact
                <input defaultValue="ops@northstar.io" />
              </label>
            </FormRow>
            <FormRow>
              <label>
                Timezone
                <input defaultValue="Asia/Kolkata" />
              </label>
              <label>
                Currency
                <input defaultValue="INR" />
              </label>
            </FormRow>
            <label>
              Notes
              <textarea defaultValue="Placeholder settings form content until the selected backend module is connected." />
            </label>
            <div className="stack-actions horizontal">
              <button className="button button-primary" type="button">Save Changes</button>
              <button className="button button-secondary" type="button">Preview</button>
            </div>
          </FormSection>
        </div>
      </div>
    </div>
  );
}
