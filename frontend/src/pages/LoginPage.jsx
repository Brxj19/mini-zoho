import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Icon } from "../components/Icon";
import { useAuthStore } from "../stores/authStore";

export function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formState, setFormState] = useState({
    email: "superadmin@example.com",
    password: "ChangeMe123!",
  });

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const payload = await login(formState);
      navigate(payload.setup_required ? "/setup" : "/", { replace: true });
    } catch (requestError) {
      setError(requestError.response?.data?.detail ?? "Unable to sign in right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-screen">
      <section className="auth-layout">
        <div className="auth-showcase">
          <p className="eyebrow">Northstar Inventory</p>
          <h1>Inventory, purchasing, and sales in one focused operations workspace.</h1>
          <p>
            The seeded demo environment now comes from the backend database, so the UI is previewing
            real app data instead of local-only objects.
          </p>
          <ul className="feature-bullets">
            <li>Super admin can sign in directly without any setup flow</li>
            <li>Indian tenants, operators, suppliers, customers, and products pre-seeded</li>
            <li>Dashboard, tables, reports, and notifications backed by API data</li>
          </ul>
          <div className="auth-note-card">
            <span className="auth-note-icon">
              <Icon name="sparkles" size={18} />
            </span>
            <div>
              <strong>Starter credentials</strong>
              <p>`superadmin@example.com` / `ChangeMe123!`</p>
            </div>
          </div>
        </div>

        <div className="auth-form-card">
          <div className="auth-form-header">
            <h2>Sign in</h2>
            <p>Access the seeded workspace or use your registered tenant account.</p>
          </div>

          <form className="stack-form" onSubmit={handleSubmit}>
            <label>
              Work email
              <input
                type="email"
                value={formState.email}
                onChange={(event) => setFormState((state) => ({ ...state, email: event.target.value }))}
                required
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={formState.password}
                onChange={(event) => setFormState((state) => ({ ...state, password: event.target.value }))}
                required
              />
            </label>

            {error ? <div className="form-error">{error}</div> : null}

            <button className="button button-primary button-block" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <div className="auth-footer-links">
            <button className="text-button" type="button">
              Forgot password
            </button>
            <Link to="/register">Create account</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
