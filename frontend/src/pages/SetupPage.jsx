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
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formState, setFormState] = useState({
    organizationName: activeOrganization?.name ?? "Varsha Retail Studio",
    industry: "Retail",
    address: "Koramangala, Bengaluru",
    currency: "INR",
    timezone: "Asia/Kolkata",
  });

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await completeSetup(formState);
      navigate("/", { replace: true });
    } catch (requestError) {
      setError(requestError.response?.data?.detail ?? "Unable to complete setup right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="standalone-page">
      <div className="standalone-shell">
        <PageHeader
          eyebrow="Organization Setup"
          title="Finish your workspace setup"
          description="Tenant admins complete this once so the organization profile is saved in the backend."
        />

        <div className="setup-grid">
          <section className="form-shell">
            <form className="stack-form" onSubmit={handleSubmit}>
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

              {error ? <div className="form-error">{error}</div> : null}

              <button className="button button-primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Saving..." : "Finish setup"}
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
