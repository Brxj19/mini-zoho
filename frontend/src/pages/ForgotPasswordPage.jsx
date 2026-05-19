import { useState } from "react";
import { Link } from "react-router-dom";

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
        <div className="auth-copy">
          <p className="eyebrow">Auth Placeholder</p>
          <h1>Request a password reset.</h1>
          <p>This placeholder confirms the request flow while email delivery and secure token handling are still pending.</p>
          <div className="auth-links">
            <span>Remembered it?</span>
            <Link to="/login">Back to sign in</Link>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Work email
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>

          {state.error ? <p className="form-error">{state.error}</p> : null}
          {state.success ? <p className="surface-success">{state.success}</p> : null}

          <button className="primary-button" type="submit" disabled={state.saving}>
            {state.saving ? "Submitting..." : "Request reset"}
          </button>
        </form>
      </section>
    </div>
  );
}
