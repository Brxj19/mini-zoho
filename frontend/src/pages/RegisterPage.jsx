import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuthStore } from "../stores/authStore";

export function RegisterPage() {
  const navigate = useNavigate();
  const register = useAuthStore((state) => state.register);
  const [formState, setFormState] = useState({
    companyName: "Northstar Retail",
    email: "owner@northstar.io",
    password: "ChangeMe123!",
    country: "India",
    phone: "+91 98765 43210",
  });

  return (
    <div className="auth-screen">
      <section className="auth-layout auth-layout-register">
        <div className="auth-showcase">
          <p className="eyebrow">Business onboarding</p>
          <h1>Set up a clean operations workspace for your inventory team.</h1>
          <p>
            Start with your organization, then move into items, warehouses, purchasing, sales, and
            reporting.
          </p>
        </div>

        <div className="auth-form-card">
          <div className="auth-form-header">
            <h2>Create your workspace</h2>
            <p>We’ll take you to a short setup flow after registration.</p>
          </div>

          <form
            className="stack-form"
            onSubmit={(event) => {
              event.preventDefault();
              register(formState);
              navigate("/setup", { replace: true });
            }}
          >
            <label>
              Company name
              <input
                value={formState.companyName}
                onChange={(event) => setFormState((state) => ({ ...state, companyName: event.target.value }))}
                required
              />
            </label>

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

            <div className="form-row columns-2">
              <label>
                Country
                <input
                  value={formState.country}
                  onChange={(event) => setFormState((state) => ({ ...state, country: event.target.value }))}
                  required
                />
              </label>

              <label>
                Phone
                <input
                  value={formState.phone}
                  onChange={(event) => setFormState((state) => ({ ...state, phone: event.target.value }))}
                  required
                />
              </label>
            </div>

            <button className="button button-primary button-block" type="submit">
              Create organization
            </button>
          </form>

          <div className="auth-footer-links">
            <span>Already have an account?</span>
            <Link to="/login">Sign in</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
