import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { Icon } from "../components/Icon";
import { useAuth } from "../contexts/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login, authError, clearAuthError, isAuthenticated, isLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function getPostLoginDestination(session) {
    const tenantId = session?.tenant?.id;
    const role = session?.user?.role;
    if (!tenantId || role === "SUPER_ADMIN") {
      return "/";
    }

    const onboardingComplete = window.localStorage.getItem(`northstar.inventory.onboarding.complete.${tenantId}`);
    return onboardingComplete === "true" ? "/" : "/onboarding";
  }

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    clearAuthError();
    try {
      const session = await login({ email, password });
      navigate(getPostLoginDestination(session), { replace: true });
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
          <p className="eyebrow">Inventory operations platform</p>
          <h1>Sign in to manage stock, orders, and warehouses.</h1>
          <p>Secure access for teams that need fast inventory control and tenant-safe workflow management.</p>
          <div className="auth-hero-actions">
            <Link to="/register" className="secondary-button">
              Start free trial
            </Link>
            <Link to="/landing" className="ghost-button">
              Learn more
            </Link>
          </div>
        </div>

        <form className="auth-form auth-card auth-card-compact" onSubmit={handleSubmit}>
          <div className="auth-card-header">
            <p className="eyebrow">Welcome back</p>
            <h2>Sign in</h2>
          </div>

          <label>
            Work email
            <input
              type="email"
              value={email}
              onChange={(event) => {
                clearAuthError();
                setEmail(event.target.value);
              }}
              required
              placeholder="you@company.com"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => {
                clearAuthError();
                setPassword(event.target.value);
              }}
              required
              placeholder="Enter password"
            />
          </label>

          <div className="auth-form-meta">
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
              />
              <span>Remember me</span>
            </label>
            <Link to="/forgot-password">Forgot password?</Link>
          </div>

          {authError ? <p className="form-error">{authError}</p> : null}

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>

          <div className="auth-links auth-links-centered">
            <span>New to Northstar?</span>
            <Link to="/register">Create your organization</Link>
          </div>
        </form>
      </section>
    </div>
  );
}
