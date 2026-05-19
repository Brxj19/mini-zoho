import { useState } from "react";
import { Link } from "react-router-dom";

import { Icon } from "../components/Icon";
import api from "../lib/api";

export function ResetPasswordPage() {
  const [form, setForm] = useState({ token: "", new_password: "", confirm_password: "" });
  const [state, setState] = useState({ saving: false, error: "", success: "" });

  function update(field, value) {
    setState((current) => ({ ...current, error: "", success: "" }));
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (form.new_password !== form.confirm_password) {
      setState({ saving: false, error: "Passwords do not match.", success: "" });
      return;
    }

    setState({ saving: true, error: "", success: "" });

    try {
      const response = await api.post("/auth/reset-password", {
        token: form.token,
        new_password: form.new_password,
      });
      setState({ saving: false, error: "", success: response.data.detail });
    } catch (error) {
      setState({
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to complete the password reset right now.",
        success: "",
      });
    }
  }

  return (
    <div className="auth-screen">
      <section className="auth-panel">
        <div className="auth-copy auth-copy-rich">
          <div className="auth-brand">
            <span className="auth-brand-mark">
              <Icon name="shield" size={16} />
            </span>
            <span>Northstar Inventory</span>
          </div>
          <p className="eyebrow">Reset Access</p>
          <h1>Create a new password and restore access to your workspace.</h1>
          <p>
            This screen is already wired to the backend placeholder route so you can verify the reset
            contract before full token delivery and email automation are introduced.
          </p>
          <div className="auth-links">
            <span>Need the request step first?</span>
            <Link to="/forgot-password">Open forgot password</Link>
          </div>
        </div>

        <form className="auth-form auth-card" onSubmit={handleSubmit}>
          <div className="auth-card-header">
            <p className="eyebrow">New password</p>
            <h2>Complete the reset</h2>
            <p>Paste the token you received and choose a strong new password.</p>
          </div>

          <label>
            Reset token
            <input value={form.token} onChange={(event) => update("token", event.target.value)} required />
          </label>

          <label>
            New password
            <input
              type="password"
              value={form.new_password}
              onChange={(event) => update("new_password", event.target.value)}
              minLength={8}
              required
            />
          </label>

          <label>
            Confirm password
            <input
              type="password"
              value={form.confirm_password}
              onChange={(event) => update("confirm_password", event.target.value)}
              minLength={8}
              required
            />
          </label>

          {state.error ? <p className="form-error">{state.error}</p> : null}
          {state.success ? <p className="surface-success">{state.success}</p> : null}

          <div className="auth-card-footer">
            <button className="primary-button" type="submit" disabled={state.saving}>
              {state.saving ? "Resetting..." : "Reset password"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
