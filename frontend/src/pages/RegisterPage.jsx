import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

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
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const updateField = (field) => (event) => {
    clearAuthError();
    setForm((current) => ({
      ...current,
      [field]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      await register({
        ...form,
        phone: form.phone || null,
        business_type: form.business_type || null,
      });
      navigate("/", { replace: true });
    } catch {
      // Error state is already handled in the auth context.
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-screen">
      <section className="auth-panel auth-panel-wide">
        <div className="auth-copy">
          <p className="eyebrow">Create Workspace</p>
          <h1>Start a tenant-ready inventory workspace with a built-in admin account.</h1>
          <p>
            Registration creates a tenant and signs in the first Tenant Admin so you can continue with
            catalog, warehouse, and order setup in the next milestones.
          </p>
          <div className="auth-links">
            <span>Already have an account?</span>
            <Link to="/login">Sign in</Link>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
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
              <input type="password" value={form.password} onChange={updateField("password")} required />
            </label>

            <label>
              Phone
              <input type="text" value={form.phone} onChange={updateField("phone")} />
            </label>

            <label>
              Business type
              <input type="text" value={form.business_type} onChange={updateField("business_type")} />
            </label>
          </div>

          {authError ? <p className="form-error">{authError}</p> : null}

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating workspace..." : "Create workspace"}
          </button>
        </form>
      </section>
    </div>
  );
}
