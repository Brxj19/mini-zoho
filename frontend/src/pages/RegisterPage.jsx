import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { Icon } from "../components/Icon";
import { useAuth } from "../contexts/AuthContext";

export function RegisterPage() {
  const navigate = useNavigate();
  const { register, authError, clearAuthError, isAuthenticated, isLoading } = useAuth();
  const [form, setForm] = useState({
    company_name: "",
    name: "",
    email: "",
    password: "",
    agree_to_terms: false,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const updateField = (field) => (event) => {
    clearAuthError();
    setForm((current) => ({
      ...current,
      [field]: event.target.type === "checkbox" ? event.target.checked : event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      await register({
        ...form,
        phone: null,
        business_type: null,
        address: null,
        contact_email: form.email,
      });
      navigate("/onboarding", { replace: true });
    } catch {
      // Error state is already handled in the auth context.
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-screen auth-screen-compact">
      <section className="auth-panel auth-panel-compact">
        <div className="auth-copy auth-copy-compact">
          <div className="auth-brand">
            <span className="auth-brand-mark">
              <Icon name="sparkles" size={16} />
            </span>
            <span>Northstar Inventory</span>
          </div>
          <p className="eyebrow">Create your workspace</p>
          <h1>Set up your inventory workspace in minutes.</h1>
          <p>One tenant, one dashboard, and the controls you need to track stock, orders, and dispatch.</p>
          <div className="auth-hero-actions">
            <Link to="/login" className="secondary-button">
              Sign in instead
            </Link>
          </div>
        </div>

        <form className="auth-form auth-card auth-card-compact" onSubmit={handleSubmit}>
          <div className="auth-card-header">
            <p className="eyebrow">Get started</p>
            <h2>Create account</h2>
          </div>

          <label>
            Company name
            <input type="text" value={form.company_name} onChange={updateField("company_name")} required placeholder="Your company" />
          </label>

          <label>
            Admin name
            <input type="text" value={form.name} onChange={updateField("name")} required placeholder="Your name" />
          </label>

          <label>
            Work email
            <input type="email" value={form.email} onChange={updateField("email")} required placeholder="you@company.com" />
          </label>

          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={updateField("password")}
              minLength={8}
              required
              placeholder="Create a strong password"
            />
          </label>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={form.agree_to_terms}
              onChange={updateField("agree_to_terms")}
              required
            />
            <span>I agree to the workspace terms and privacy policy.</span>
          </label>

          {authError ? <p className="form-error">{authError}</p> : null}

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating account..." : "Create account"}
          </button>

          <div className="auth-links auth-links-centered">
            <span>Already have access?</span>
            <Link to="/login">Sign in</Link>
          </div>
        </form>
      </section>
    </div>
  );
}
