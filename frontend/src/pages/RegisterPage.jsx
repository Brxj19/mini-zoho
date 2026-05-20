import { useMemo, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { AuthShowcase } from "../components/AuthShowcase";
import { BackButton } from "../components/BackButton";
import { Icon } from "../components/Icon";
import { useAuth } from "../contexts/AuthContext";

const passwordChecks = [
  { id: "length", label: "At least 8 characters" },
  { id: "letter", label: "Contains a letter" },
  { id: "number", label: "Contains a number" },
];

function evaluatePassword(password) {
  return {
    length: password.length >= 8,
    letter: /[A-Za-z]/.test(password),
    number: /\d/.test(password),
  };
}

export function RegisterPage() {
  const navigate = useNavigate();
  const { register, authError, clearAuthError, isAuthenticated, isLoading } = useAuth();
  const [form, setForm] = useState({
    company_name: "",
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    agree_to_terms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [focusedField, setFocusedField] = useState("");
  const [localError, setLocalError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const passwordState = useMemo(() => evaluatePassword(form.password), [form.password]);
  const passwordsMatch = form.confirmPassword.length > 0 && form.password === form.confirmPassword;

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const updateField = (field) => (event) => {
    clearAuthError();
    setLocalError("");
    setForm((current) => ({
      ...current,
      [field]: event.target.type === "checkbox" ? event.target.checked : event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    clearAuthError();
    setLocalError("");

    if (form.password !== form.confirmPassword) {
      setLocalError("Passwords do not match.");
      return;
    }

    const isPasswordValid = Object.values(passwordState).every(Boolean);
    if (!isPasswordValid) {
      setLocalError("Create a stronger password before continuing.");
      return;
    }

    setIsSubmitting(true);
    try {
      await register({
        company_name: form.company_name,
        name: form.name,
        email: form.email,
        password: form.password,
        agree_to_terms: form.agree_to_terms,
        phone: null,
        business_type: null,
        address: null,
        contact_email: form.email,
      });
      navigate("/onboarding", { replace: true });
    } catch {
      // The auth provider owns the request error message state.
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="public-screen auth-split-screen">
      <section className="auth-split-shell auth-split-shell-signup">
        <AuthShowcase
          eyebrow="Start your workspace"
          title="Create your inventory workspace in minutes."
          description="Set up your organization once, then move into onboarding, stock setup, vendors, customers, and daily operations without clutter."
          secondaryCtaLabel="Sign in"
          secondaryCtaTo="/login"
          badge="Tenant-ready setup"
        />

        <form className="auth-split-card auth-split-card-signup" onSubmit={handleSubmit}>
          <div className="auth-split-card-top">
            <BackButton fallbackTo="/" label="Back to home" />
            <div className="auth-split-card-top-links">
              <span className="auth-split-domain">northstar.local/trial</span>
              <Link to="/login" className="auth-showcase-link">
                Sign in
              </Link>
            </div>
          </div>

          <div className="auth-modern-card-header">
            <div>
              <p className="eyebrow">Free trial</p>
              <h2>Create account</h2>
            </div>
          </div>

          <div className="auth-modern-form-grid">
            <label className="auth-modern-field auth-modern-field-full">
              <span>Company name</span>
              <input
                type="text"
                value={form.company_name}
                onChange={updateField("company_name")}
                onFocus={() => setFocusedField("company_name")}
                onBlur={() => setFocusedField("")}
                required
                placeholder="Northstar Retail"
              />
              {focusedField === "company_name" ? <small className="auth-modern-helper">Use the organization name your team will recognize in the workspace.</small> : null}
            </label>

            <label className="auth-modern-field">
              <span>Admin name</span>
              <input
                type="text"
                value={form.name}
                onChange={updateField("name")}
                onFocus={() => setFocusedField("name")}
                onBlur={() => setFocusedField("")}
                required
                placeholder="Aakash Sharma"
              />
              {focusedField === "name" ? <small className="auth-modern-helper">This becomes the primary admin name for the new workspace.</small> : null}
            </label>

            <label className="auth-modern-field">
              <span>Work email</span>
              <input
                type="email"
                value={form.email}
                onChange={updateField("email")}
                onFocus={() => setFocusedField("email")}
                onBlur={() => setFocusedField("")}
                required
                autoComplete="email"
                placeholder="you@company.com"
              />
              {focusedField === "email" ? <small className="auth-modern-helper">We’ll use this email for sign in, workspace notices, and onboarding communication.</small> : null}
            </label>

            <label className="auth-modern-field">
              <span>Password</span>
              <div className="auth-modern-password-field">
                <input
                  type={showPassword ? "text" : "password"}
                  value={form.password}
                  onChange={updateField("password")}
                  onFocus={() => setFocusedField("password")}
                  onBlur={() => setFocusedField("")}
                  minLength={8}
                  required
                  autoComplete="new-password"
                  placeholder="Create password"
                />
                <button type="button" className="auth-modern-text-button" onClick={() => setShowPassword((value) => !value)}>
                  <Icon name={showPassword ? "eyeOff" : "eye"} size={15} />
                  <span>{showPassword ? "Hide" : "Show"}</span>
                </button>
              </div>
              {(focusedField === "password" || form.password) ? (
                <small className="auth-modern-helper">
                  Use at least 8 characters with letters and numbers for a stronger workspace password.
                </small>
              ) : null}
            </label>

            <label className="auth-modern-field">
              <span>Confirm password</span>
              <div className="auth-modern-password-field">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  value={form.confirmPassword}
                  onChange={updateField("confirmPassword")}
                  onFocus={() => setFocusedField("confirmPassword")}
                  onBlur={() => setFocusedField("")}
                  minLength={8}
                  required
                  autoComplete="new-password"
                  placeholder="Confirm password"
                />
                <button type="button" className="auth-modern-text-button" onClick={() => setShowConfirmPassword((value) => !value)}>
                  <Icon name={showConfirmPassword ? "eyeOff" : "eye"} size={15} />
                  <span>{showConfirmPassword ? "Hide" : "Show"}</span>
                </button>
              </div>
              {(focusedField === "confirmPassword" || form.confirmPassword) ? (
                <small className={`auth-modern-helper ${passwordsMatch ? "is-success" : ""}`}>
                  {passwordsMatch ? "Passwords match." : "Re-enter the same password to confirm your workspace login."}
                </small>
              ) : null}
            </label>
          </div>

          <div className="auth-modern-password-checks">
            {passwordChecks.map((item) => (
              <div className={`auth-modern-password-check ${passwordState[item.id] ? "is-complete" : ""}`} key={item.id}>
                <Icon name={passwordState[item.id] ? "shield" : "sparkles"} size={14} />
                <span>{item.label}</span>
              </div>
            ))}
          </div>

          <label className="checkbox-row auth-modern-checkbox">
            <input
              type="checkbox"
              checked={form.agree_to_terms}
              onChange={updateField("agree_to_terms")}
              required
            />
            <span>I agree to the terms, privacy policy, and workspace provisioning rules.</span>
          </label>

          {localError ? <p className="form-error">{localError}</p> : null}
          {authError ? <p className="form-error">{authError}</p> : null}

          <button className="primary-button auth-modern-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating account..." : "Create workspace"}
          </button>

          <p className="auth-modern-footer">
            Already have access?
            <Link to="/login">Sign in</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
