import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login, authError, clearAuthError, isAuthenticated, isLoading } = useAuth();
  const [email, setEmail] = useState("superadmin@example.com");
  const [password, setPassword] = useState("ChangeMe123!");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    clearAuthError();
    try {
      await login({ email, password });
      navigate("/", { replace: true });
    } catch {
      // Error state is already handled in the auth context.
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-screen">
      <section className="auth-panel">
        <div className="auth-copy">
          <p className="eyebrow">Inventory SaaS Starter</p>
          <h1>Launch a clean multi-tenant operations workspace.</h1>
          <p>
            Sign in with the seeded Super Admin account or a tenant admin created through the registration
            flow. Backend auth now issues JWT access and refresh tokens.
          </p>
          <div className="auth-links">
            <span>Need a tenant workspace?</span>
            <Link to="/register">Create one</Link>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Email
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

          {authError ? <p className="form-error">{authError}</p> : null}

          <div className="auth-links">
            <span>Forgot your password?</span>
            <Link to="/forgot-password">Reset access</Link>
          </div>

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing in..." : "Continue"}
          </button>
        </form>
      </section>
    </div>
  );
}
