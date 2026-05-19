import { useState } from "react";
import { Link } from "react-router-dom";

import { Icon } from "../components/Icon";
import api from "../lib/api";

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [state, setState] = useState({ saving: false, error: "", success: "" });

  async function handleSubmit(event) {
    event.preventDefault();
    setState({ saving: true, error: "", success: "" });

    try {
      const response = await api.post("/auth/forgot-password", { email });
      setState({ saving: false, error: "", success: response.data.detail });
    } catch (error) {
      setState({
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to submit the forgot password request.",
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
          <p className="eyebrow">Account Recovery</p>
          <h1>Request a reset link for your workspace account.</h1>
          <p>
            This flow already talks to the backend placeholder endpoint, so you can validate the reset
            request experience while secure email delivery is still being finalized.
          </p>
          <div className="auth-links">
            <span>Remembered it?</span>
            <Link to="/login">Back to sign in</Link>
          </div>
        </div>

        <form className="auth-form auth-card" onSubmit={handleSubmit}>
          <div className="auth-card-header">
            <p className="eyebrow">Reset access</p>
            <h2>Enter your work email</h2>
            <p>We’ll confirm the request and guide you into the placeholder reset step.</p>
          </div>

          <label>
            Work email
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>

          {state.error ? <p className="form-error">{state.error}</p> : null}
          {state.success ? <p className="surface-success">{state.success}</p> : null}

          <div className="auth-card-footer">
            <button className="primary-button" type="submit" disabled={state.saving}>
              {state.saving ? "Submitting..." : "Request reset"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
