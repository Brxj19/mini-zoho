import { useState } from "react";
import { Link } from "react-router-dom";

import api from "../lib/api";

export function ResetPasswordPage() {
  const [form, setForm] = useState({ token: "", new_password: "", confirm_password: "" });
  const [state, setState] = useState({ saving: false, error: "", success: "" });

  function update(field, value) {
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
        error: error?.response?.data?.detail ?? "Unable to submit the reset password placeholder.",
        success: "",
      });
    }
  }

  return (
    <div className="auth-screen">
      <section className="auth-panel">
        <div className="auth-copy">
          <p className="eyebrow">Auth Placeholder</p>
          <h1>Reset your password.</h1>
          <p>This placeholder simulates the reset form until secure token issuance and email workflows are implemented.</p>
          <div className="auth-links">
            <span>Need the request step first?</span>
            <Link to="/forgot-password">Open forgot password</Link>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Reset token
            <input value={form.token} onChange={(event) => update("token", event.target.value)} required />
          </label>
          <label>
            New password
            <input type="password" value={form.new_password} onChange={(event) => update("new_password", event.target.value)} required />
          </label>
          <label>
            Confirm password
            <input type="password" value={form.confirm_password} onChange={(event) => update("confirm_password", event.target.value)} required />
          </label>

          {state.error ? <p className="form-error">{state.error}</p> : null}
          {state.success ? <p className="surface-success">{state.success}</p> : null}

          <button className="primary-button" type="submit" disabled={state.saving}>
            {state.saving ? "Submitting..." : "Reset password"}
          </button>
        </form>
      </section>
    </div>
  );
}
