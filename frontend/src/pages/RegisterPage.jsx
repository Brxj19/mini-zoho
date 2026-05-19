import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { LottieAnimation } from "../components/common/LottieAnimation";
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
    phone: "",
    business_type: "",
    country: "India",
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
    if (!form.agree_to_terms) {
      clearAuthError();
      return;
    }
    setIsSubmitting(true);
    try {
      await register({
        ...form,
        phone: form.phone || null,
        business_type: form.business_type || null,
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
    <div className="auth-screen">
      <section className="auth-panel auth-panel-wide">
        <div className="auth-copy auth-copy-rich">
          <div className="auth-brand">
            <span className="auth-brand-mark">
              <Icon name="sparkles" size={16} />
            </span>
            <span>Northstar Inventory</span>
          </div>
          <p className="eyebrow">Create Organization</p>
          <LottieAnimation
            animationKey="onboarding"
            size={360}
            className="lottie-animation--large"
            ariaLabel="Organization signup illustration"
            decorative={false}
          />
          <h1>Launch a fresh inventory workspace with your first tenant admin already in place.</h1>
          <p>
            Registration creates your tenant and signs you in immediately so you can finish workspace setup,
            define warehouses, and start moving products without a second setup tool.
          </p>

          <div className="auth-feature-stack">
            <div className="auth-highlight-card">
              <h3>Included from day one</h3>
              <ul className="auth-bullet-list">
                <li>Multi-warehouse stock visibility</li>
                <li>Purchasing, sales, and transfer workflows</li>
                <li>Tenant-safe roles, reports, and notifications</li>
              </ul>
            </div>
            <div className="auth-highlight-card">
              <h3>Best fit</h3>
              <p>Retail, wholesale, distribution, and growing operations teams that need an admin-first SaaS setup.</p>
            </div>
          </div>

          <div className="auth-links">
            <span>Already have an account?</span>
            <Link to="/login">Sign in</Link>
          </div>
        </div>

        <form className="auth-form auth-card auth-card-wide" onSubmit={handleSubmit}>
          <div className="auth-card-header">
            <p className="eyebrow">Workspace signup</p>
            <h2>Create your organization</h2>
            <p>We’ll create your tenant and make you the first admin.</p>
          </div>

          <div className="form-section">
            <div className="form-section-heading">
              <h3>Company and admin details</h3>
              <p>These values create your initial tenant and user account.</p>
            </div>

            <div className="form-grid">
              <label>
                Company name
                <input type="text" value={form.company_name} onChange={updateField("company_name")} required />
              </label>

              <label>
                Admin name
                <input type="text" value={form.name} onChange={updateField("name")} required />
              </label>

              <label>
                Work email
                <input type="email" value={form.email} onChange={updateField("email")} required />
              </label>

              <label>
                Password
                <input
                  type="password"
                  value={form.password}
                  onChange={updateField("password")}
                  minLength={8}
                  required
                />
              </label>

              <label>
                Phone
                <input type="text" value={form.phone} onChange={updateField("phone")} placeholder="+91 98765 43210" />
              </label>

              <label>
                Country
                <select value={form.country} onChange={updateField("country")}>
                  <option value="India">India</option>
                  <option value="United Arab Emirates">United Arab Emirates</option>
                  <option value="Singapore">Singapore</option>
                  <option value="United States">United States</option>
                </select>
              </label>

              <label className="field-span-full">
                Business type
                <input
                  type="text"
                  value={form.business_type}
                  onChange={updateField("business_type")}
                  placeholder="Retail, distribution, manufacturing..."
                />
              </label>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-heading">
              <h3>Before you continue</h3>
              <p>You’ll be signed in immediately and taken to organization setup next.</p>
            </div>

            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={form.agree_to_terms}
                onChange={updateField("agree_to_terms")}
                required
              />
              <span>I agree to continue with the workspace creation and initial admin setup.</span>
            </label>
          </div>

          {authError ? <p className="form-error">{authError}</p> : null}

          <div className="auth-card-footer">
            <button className="primary-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating organization..." : "Create organization"}
            </button>
          </div>

          <div className="auth-links auth-links-centered">
            <span>Already have access?</span>
            <Link to="/login">Go to sign in</Link>
          </div>
        </form>
      </section>
    </div>
  );
}
