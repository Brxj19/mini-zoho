import { useMemo, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { AuthShowcase } from "../components/AuthShowcase";
import { BackButton } from "../components/BackButton";
import { Icon } from "../components/Icon";
import { useAuth } from "../contexts/AuthContext";
import { ONBOARDING_STATUS_PENDING, getOnboardingStatus, setOnboardingStatus } from "../lib/onboarding";

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
  const { register, authError, clearAuthError, isAuthenticated, isLoading, tenant, user } = useAuth();
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
  const companyHelper =
    focusedField === "company_name"
      ? "Use the organization name your team will recognize in the workspace."
      : "\u00A0";
  const nameHelper =
    focusedField === "name"
      ? "This becomes the primary admin name for the new workspace."
      : "\u00A0";
  const emailHelper =
    focusedField === "email"
      ? "We’ll use this email for sign in, workspace notices, and onboarding communication."
      : "\u00A0";
  const passwordHelper =
    focusedField === "password" || form.password
      ? "Use at least 8 characters with letters and numbers for a stronger workspace password."
      : "\u00A0";
  const confirmPasswordHelper =
    focusedField === "confirmPassword" || form.confirmPassword
      ? passwordsMatch
        ? "Passwords match."
        : "Re-enter the same password to confirm your workspace login."
      : "\u00A0";

  if (!isLoading && isAuthenticated) {
    const tenantId = tenant?.id;
    const shouldGoToOnboarding = tenantId && user?.role !== "SUPER_ADMIN" && getOnboardingStatus(tenantId) === ONBOARDING_STATUS_PENDING;
    return <Navigate to={shouldGoToOnboarding ? "/onboarding" : "/dashboard"} replace />;
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
      const session = await register({
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
      if (session?.tenant?.id) {
        setOnboardingStatus(session.tenant.id, ONBOARDING_STATUS_PENDING);
      }
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
              <small className="auth-modern-helper">{companyHelper}</small>
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
              <small className="auth-modern-helper">{nameHelper}</small>
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
              <small className="auth-modern-helper">{emailHelper}</small>
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
                </button>
              </div>
              <small className="auth-modern-helper">{passwordHelper}</small>
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
                </button>
              </div>
              <small className={`auth-modern-helper ${passwordsMatch && form.confirmPassword ? "is-success" : ""}`}>
                {confirmPasswordHelper}
              </small>
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
