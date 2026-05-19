import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { LottieAnimation } from "../components/common/LottieAnimation";
import { Icon } from "../components/Icon";
import { useAuth } from "../contexts/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login, authError, clearAuthError, isAuthenticated, isLoading } = useAuth();
  const [email, setEmail] = useState("superadmin@example.com");
  const [password, setPassword] = useState("ChangeMe123!");
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
    <div className="auth-screen">
      <section className="auth-panel">
        <div className="auth-copy auth-copy-rich">
          <div className="auth-brand">
            <span className="auth-brand-mark">
              <Icon name="sparkles" size={16} />
            </span>
            <span>Northstar Inventory</span>
          </div>
          <p className="eyebrow">Inventory Operations Cloud</p>
          <LottieAnimation
            animationKey="onboarding"
            size={360}
            className="lottie-animation--large"
            ariaLabel="Inventory onboarding illustration"
            decorative={false}
          />
          <h1>Run your inventory, purchasing, sales, and warehouses from one compact workspace.</h1>
          <p>
            Sign in with your platform or tenant account to continue into the live Northstar Inventory
            workspace. Authentication uses the existing JWT session flow already wired to the backend.
          </p>

          <div className="auth-feature-stack">
            <div className="auth-highlight-card">
              <h3>What teams use it for</h3>
              <ul className="auth-bullet-list">
                <li>Track stock across multiple warehouses</li>
                <li>Manage purchase and sales order lifecycles</li>
                <li>Keep every tenant isolated with role-based access</li>
              </ul>
            </div>

            <div className="auth-highlight-card auth-credentials-card">
              <h3>Demo access</h3>
              <div className="auth-credential-row">
                <span>Super Admin</span>
                <strong>superadmin@example.com</strong>
              </div>
              <div className="auth-credential-row">
                <span>Password</span>
                <strong>ChangeMe123!</strong>
              </div>
            </div>
          </div>

          <div className="auth-links">
            <span>Need a tenant workspace?</span>
            <Link to="/register">Create one</Link>
          </div>
        </div>

        <form className="auth-form auth-card" onSubmit={handleSubmit}>
          <div className="auth-card-header">
            <p className="eyebrow">Welcome back</p>
            <h2>Sign in to your workspace</h2>
            <p>Use your work email and password to continue.</p>
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
            />
          </label>

          <div className="auth-form-meta">
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
              />
              <span>Remember me on this browser</span>
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
