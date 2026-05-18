import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import { useActiveOrganization, useAuthStore } from "../stores/authStore";

const checklist = [
  "Update organization details",
  "Create or import items",
  "Add vendors",
  "Create purchase order",
  "Create sales order",
  "Invite users",
];

export function SetupPage() {
  const activeOrganization = useActiveOrganization();
  const completeSetup = useAuthStore((state) => state.completeSetup);
  const navigate = useNavigate();
  const [formState, setFormState] = useState({
    organizationName: activeOrganization?.name ?? "Northstar Retail",
    industry: "Retail",
    address: "Bengaluru, Karnataka",
    currency: "INR",
    timezone: "Asia/Kolkata",
  });

  return (
    <div className="standalone-page">
      <div className="standalone-shell">
        <PageHeader
          eyebrow="Organization Setup"
          title="Finish your workspace setup"
          description="This onboarding step stays frontend-led until the backend organization setup workflow is connected."
        />

        <div className="setup-grid">
          <section className="form-shell">
            <form
              className="stack-form"
              onSubmit={(event) => {
                event.preventDefault();
                completeSetup(formState);
                navigate("/", { replace: true });
              }}
            >
              <label>
                Organization name
                <input
                  value={formState.organizationName}
                  onChange={(event) =>
                    setFormState((state) => ({ ...state, organizationName: event.target.value }))
                  }
                  required
                />
              </label>

              <label>
                Industry
                <input
                  value={formState.industry}
                  onChange={(event) => setFormState((state) => ({ ...state, industry: event.target.value }))}
                />
              </label>

              <label>
                Address
                <input
                  value={formState.address}
                  onChange={(event) => setFormState((state) => ({ ...state, address: event.target.value }))}
                />
              </label>

              <div className="form-row columns-2">
                <label>
                  Currency
                  <input
                    value={formState.currency}
                    onChange={(event) => setFormState((state) => ({ ...state, currency: event.target.value }))}
                  />
                </label>
                <label>
                  Time zone
                  <input
                    value={formState.timezone}
                    onChange={(event) => setFormState((state) => ({ ...state, timezone: event.target.value }))}
                  />
                </label>
              </div>

              <button className="button button-primary" type="submit">
                Finish setup
              </button>
            </form>
          </section>

          <section className="panel-card">
            <h2>Getting started checklist</h2>
            <ul className="checklist">
              {checklist.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}
