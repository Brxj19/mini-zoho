import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Icon } from "../components/Icon";
import { useAuthStore } from "../stores/authStore";

export function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [formState, setFormState] = useState({
    email: "superadmin@example.com",
    password: "ChangeMe123!",
  });

  return (
    <div className="auth-screen">
      <section className="auth-layout">
        <div className="auth-showcase">
          <p className="eyebrow">Northstar Inventory</p>
          <h1>Run inventory, purchasing, and sales from one compact workspace.</h1>
          <p>
            A modern inventory SaaS shell inspired by dense business workflows, purpose-built for
            retail operators and warehouse teams.
          </p>

          <ul className="feature-bullets">
            <li>Multi-tenant operational dashboard</li>
            <li>Stock transfers, purchase orders, and sales workflows</li>
            <li>Reports, audit trails, and structured settings</li>
          </ul>

          <div className="auth-note-card">
            <span className="auth-note-icon">
              <Icon name="sparkles" size={18} />
            </span>
            <div>
              <strong>Current branch note</strong>
              <p>Frontend modules with missing backend support are clearly marked as UI placeholders.</p>
            </div>
          </div>
        </div>

        <div className="auth-form-card">
          <div className="auth-form-header">
            <h2>Sign in</h2>
            <p>Use the starter credentials or continue with any email to preview the UI.</p>
          </div>

          <form
            className="stack-form"
            onSubmit={(event) => {
              event.preventDefault();
              login(formState.email);
              navigate("/", { replace: true });
            }}
          >
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

            <button className="button button-primary button-block" type="submit">
              Sign in
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
