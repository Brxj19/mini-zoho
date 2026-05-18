import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("superadmin@example.com");
  const [password, setPassword] = useState("ChangeMe123!");

  const handleSubmit = (event) => {
    event.preventDefault();
    login(`demo-token:${email}`);
    navigate("/", { replace: true });
  };

  return (
    <div className="auth-screen">
      <section className="auth-panel">
        <div className="auth-copy">
          <p className="eyebrow">Inventory SaaS Starter</p>
          <h1>Launch a clean multi-tenant operations workspace.</h1>
          <p>
            Phase 1 includes the React shell, FastAPI foundation, MySQL connectivity, Alembic wiring,
            and Docker-based local setup.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Email
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          <button className="primary-button" type="submit">
            Continue
          </button>
        </form>
      </section>
    </div>
  );
}

