import { useEffect, useMemo, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { Icon } from "../components/Icon";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";

function getPrefsStorageKey(tenantId) {
  return `northstar.inventory.onboarding.prefs.${tenantId}`;
}

function getCompletionStorageKey(tenantId) {
  return `northstar.inventory.onboarding.complete.${tenantId}`;
}

export function OnboardingPage() {
  const navigate = useNavigate();
  const { tenant, user, isLoading, refreshProfile } = useAuth();
  const [form, setForm] = useState({
    company_name: "",
    business_type: "",
    address: "",
    phone: "",
    country: "India",
    currency: "INR",
    time_zone: "Asia/Kolkata",
  });
  const [state, setState] = useState({ saving: false, error: "", success: "" });

  const tenantId = tenant?.id ?? null;
  const completionKey = tenantId ? getCompletionStorageKey(tenantId) : null;
  const preferencesKey = tenantId ? getPrefsStorageKey(tenantId) : null;

  const isSetupComplete = useMemo(() => {
    if (!completionKey) {
      return false;
    }

    return window.localStorage.getItem(completionKey) === "true";
  }, [completionKey]);

  useEffect(() => {
    if (!tenant) {
      return;
    }

    let preferences = {};
    if (preferencesKey) {
      try {
        preferences = JSON.parse(window.localStorage.getItem(preferencesKey) ?? "{}");
      } catch {
        preferences = {};
      }
    }

    setForm({
      company_name: tenant.company_name ?? "",
      business_type: tenant.business_type ?? "",
      address: tenant.address ?? "",
      phone: tenant.phone ?? "",
      country: preferences.country ?? "India",
      currency: preferences.currency ?? "INR",
      time_zone: preferences.time_zone ?? "Asia/Kolkata",
    });
  }, [tenant, preferencesKey]);

  if (!isLoading && !user) {
    return <Navigate to="/login" replace />;
  }

  if (!isLoading && (!tenant || user?.role === "SUPER_ADMIN")) {
    return <Navigate to="/" replace />;
  }

  function updateField(field, value) {
    setState((current) => ({ ...current, error: "", success: "" }));
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!tenantId || !preferencesKey || !completionKey) {
      return;
    }

    setState({ saving: true, error: "", success: "" });

    try {
      await api.patch(`/tenants/${tenantId}`, {
        company_name: form.company_name,
        business_type: form.business_type || null,
        address: form.address || null,
        phone: form.phone || null,
      });

      window.localStorage.setItem(
        preferencesKey,
        JSON.stringify({
          country: form.country,
          currency: form.currency,
          time_zone: form.time_zone,
        }),
      );
      window.localStorage.setItem(completionKey, "true");

      await refreshProfile();

      setState({ saving: false, error: "", success: "Workspace details saved successfully." });
      navigate("/", { replace: true });
    } catch (error) {
      setState({
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to finish workspace setup right now.",
        success: "",
      });
    }
  }

  function handleSkip() {
    if (completionKey) {
      window.localStorage.setItem(completionKey, "true");
    }
    navigate("/", { replace: true });
  }

  return (
    <div className="auth-screen auth-screen-onboarding">
      <section className="auth-panel auth-panel-wide auth-panel-onboarding">
        <div className="auth-copy auth-copy-onboarding">
          <div className="auth-brand">
            <span className="auth-brand-mark">
              <Icon name="sparkles" size={16} />
            </span>
            <span>Northstar Inventory</span>
          </div>
          <p className="eyebrow">Organization Setup</p>
          <h1>Set up your workspace before you start receiving, selling, and moving stock.</h1>
          <p>
            This quick onboarding saves your core organization profile to the tenant record and keeps your
            operating preferences ready for the rest of the product experience.
          </p>

          <div className="auth-feature-stack">
            <div className="auth-highlight-card">
              <h3>What gets saved now</h3>
              <ul className="auth-bullet-list">
                <li>Organization name and industry</li>
                <li>Primary business address and phone</li>
                <li>Country, currency, and time zone preferences for this browser session</li>
              </ul>
            </div>

            <div className="auth-highlight-card">
              <h3>Getting started checklist</h3>
              <div className="checklist-grid">
                {[
                  "Update organization details",
                  "Create or import items",
                  "Add vendors",
                  "Add customers",
                  "Create a purchase order",
                  "Create a sales order",
                  "Invite your team",
                ].map((item) => (
                  <div className="checklist-item" key={item}>
                    <Icon name="clipboard" size={16} />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <form className="auth-card auth-form auth-card-onboarding" onSubmit={handleSubmit}>
          <div className="auth-card-header">
            <p className="eyebrow">Workspace Profile</p>
            <h2>Tell us how your inventory operation is set up</h2>
            <p>{isSetupComplete ? "You can update these details anytime from Settings." : "This takes less than two minutes."}</p>
          </div>

          <div className="form-section">
            <div className="form-section-heading">
              <h3>Organization details</h3>
              <p>These values are saved to your tenant profile and shown across the workspace.</p>
            </div>
            <div className="form-grid">
              <label>
                Organization name
                <input
                  type="text"
                  value={form.company_name}
                  onChange={(event) => updateField("company_name", event.target.value)}
                  required
                />
              </label>
              <label>
                Industry
                <input
                  type="text"
                  value={form.business_type}
                  onChange={(event) => updateField("business_type", event.target.value)}
                  placeholder="Retail, wholesale, manufacturing..."
                />
              </label>
              <label className="field-span-full">
                Business address
                <textarea
                  value={form.address}
                  onChange={(event) => updateField("address", event.target.value)}
                  rows={4}
                  placeholder="Street, locality, city, state, PIN code"
                />
              </label>
              <label>
                Contact phone
                <input
                  type="text"
                  value={form.phone}
                  onChange={(event) => updateField("phone", event.target.value)}
                  placeholder="+91 98765 43210"
                />
              </label>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-heading">
              <h3>Operating preferences</h3>
              <p>These preferences help shape the UI while fuller backend-backed settings continue to expand.</p>
            </div>
            <div className="form-grid">
              <label>
                Country
                <select value={form.country} onChange={(event) => updateField("country", event.target.value)}>
                  <option value="India">India</option>
                  <option value="United Arab Emirates">United Arab Emirates</option>
                  <option value="Singapore">Singapore</option>
                  <option value="United States">United States</option>
                </select>
              </label>
              <label>
                Currency
                <select value={form.currency} onChange={(event) => updateField("currency", event.target.value)}>
                  <option value="INR">INR - Indian Rupee</option>
                  <option value="USD">USD - US Dollar</option>
                  <option value="AED">AED - UAE Dirham</option>
                  <option value="SGD">SGD - Singapore Dollar</option>
                </select>
              </label>
              <label>
                Time zone
                <select value={form.time_zone} onChange={(event) => updateField("time_zone", event.target.value)}>
                  <option value="Asia/Kolkata">Asia/Kolkata</option>
                  <option value="Asia/Dubai">Asia/Dubai</option>
                  <option value="Asia/Singapore">Asia/Singapore</option>
                  <option value="America/New_York">America/New_York</option>
                </select>
              </label>
            </div>
          </div>

          {state.error ? <p className="form-error">{state.error}</p> : null}
          {state.success ? <p className="surface-success">{state.success}</p> : null}

          <div className="auth-card-footer auth-card-footer-split">
            <button className="button button-ghost" type="button" onClick={handleSkip}>
              Finish later
            </button>
            <button className="primary-button" type="submit" disabled={state.saving}>
              {state.saving ? "Saving workspace..." : "Finish setup"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
