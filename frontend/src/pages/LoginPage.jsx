import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { AuthShowcase } from "../components/AuthShowcase";
import { BackButton } from "../components/BackButton";
import { Icon } from "../components/Icon";
import { useAuth } from "../contexts/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login, authError, clearAuthError, isAuthenticated, isLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [focusedField, setFocusedField] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const emailHelper = focusedField === "email" ? "Use the workspace email assigned to you or your tenant admin account." : "\u00A0";
  const passwordHelper =
    focusedField === "password"
      ? "Passwords are case-sensitive. Use the one configured for your workspace account."
      : "\u00A0";

  function getPostLoginDestination(session) {
    const tenantId = session?.tenant?.id;
    const role = session?.user?.role;
    if (!tenantId || role === "SUPER_ADMIN") {
      return "/dashboard";
    }

    const onboardingComplete = window.localStorage.getItem(`northstar.inventory.onboarding.complete.${tenantId}`);
    return onboardingComplete === "true" ? "/dashboard" : "/onboarding";
  }

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    clearAuthError();

    try {
      const session = await login({ email, password });
      navigate(getPostLoginDestination(session), { replace: true });
    } catch {
      // The auth provider owns the error message state.
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="public-screen auth-split-screen">
      <section className="auth-split-shell">
        <AuthShowcase
          eyebrow="Operations workspace"
          title="Sign in and keep inventory work moving."
          description="Get back to stock visibility, warehouse movement, purchasing, and sales execution from one clean control surface."
          secondaryCtaLabel="Create account"
          secondaryCtaTo="/register"
        />

        <form className="auth-split-card" onSubmit={handleSubmit}>
          <div className="auth-split-card-top">
            <BackButton fallbackTo="/" label="Back to home" />
            <div className="auth-split-card-top-links">
              <span className="auth-split-domain">northstar.local/workspace</span>
              <Link to="/register" className="auth-showcase-link">
                Create account
              </Link>
            </div>
          </div>

          <div className="auth-modern-card-header">
            <div>
              <p className="eyebrow">Welcome back</p>
              <h2>Sign in</h2>
            </div>
          </div>

          <label className="auth-modern-field">
            <span>Work email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => {
                clearAuthError();
                setEmail(event.target.value);
              }}
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
                value={password}
                onChange={(event) => {
                  clearAuthError();
                  setPassword(event.target.value);
                }}
                onFocus={() => setFocusedField("password")}
                onBlur={() => setFocusedField("")}
                required
                autoComplete="current-password"
                placeholder="Enter password"
              />
              <button type="button" className="auth-modern-text-button" onClick={() => setShowPassword((value) => !value)}>
                <Icon name={showPassword ? "eyeOff" : "eye"} size={15} />
              </button>
            </div>
            <small className="auth-modern-helper">{passwordHelper}</small>
          </label>

          <div className="auth-modern-form-row">
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
              />
              <span>Remember me</span>
            </label>
            <Link to="/forgot-password" className="auth-modern-inline-link">
              Forgot password?
            </Link>
          </div>

          {authError ? <p className="form-error">{authError}</p> : null}

          <button className="primary-button auth-modern-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>

          <p className="auth-modern-footer">
            New to Northstar?
            <Link to="/register">Start free trial</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
