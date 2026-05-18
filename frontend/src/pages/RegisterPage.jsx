import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuthStore } from "../stores/authStore";

export function RegisterPage() {
  const navigate = useNavigate();
  const register = useAuthStore((state) => state.register);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formState, setFormState] = useState({
    companyName: "Varsha Retail Studio",
    email: "owner@varsharetail.in",
    password: "ChangeMe123!",
    country: "India",
    phone: "+91 98765 43210",
  });

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const payload = await register(formState);
      navigate(payload.setup_required ? "/setup" : "/", { replace: true });
    } catch (requestError) {
      setError(requestError.response?.data?.detail ?? "Unable to register right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-screen">
      <section className="auth-layout auth-layout-register">
        <div className="auth-showcase">
          <p className="eyebrow">Business onboarding</p>
          <h1>Launch an inventory workspace for your team with a short setup flow.</h1>
          <p>
            Registering a tenant admin now creates a real tenant and user in the backend database
            before sending you into organization setup.
          </p>
        </div>

        <div className="auth-form-card">
          <div className="auth-form-header">
            <h2>Create your workspace</h2>
            <p>Tenant admins complete setup once. Super admin skips it entirely.</p>
          </div>

          <form className="stack-form" onSubmit={handleSubmit}>
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

            {error ? <div className="form-error">{error}</div> : null}

            <button className="button button-primary button-block" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create organization"}
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
