import { Link } from "react-router-dom";

import { Icon } from "../components/Icon";

export function LandingPage() {
  return (
    <div className="landing-screen">
      <section className="landing-hero">
        <div className="landing-copy">
          <div className="landing-brand">
            <span className="landing-brand-mark">
              <Icon name="sparkles" size={18} />
            </span>
            <span>Northstar Inventory</span>
          </div>
          <p className="eyebrow">Inventory operations platform</p>
          <h1>Run stock, purchasing, sales, and warehouses in one streamlined workspace.</h1>
          <p>Start with a clean, fast workspace built for teams that need accurate stock control, simple order flow, and tenant-safe access.</p>
          <div className="landing-actions">
            <Link to="/register" className="primary-button">
              Start free trial
            </Link>
            <Link to="/login" className="secondary-button">
              Sign in
            </Link>
          </div>
        </div>

        <div className="landing-cards">
          <div className="landing-feature-card">
            <strong>Quick inventory control</strong>
            <p>Move stock, log transfers, and reconcile warehouses without clutter.</p>
          </div>
          <div className="landing-feature-card">
            <strong>Order workflows that work</strong>
            <p>Buy, receive, sell, invoice, and return with clear status tracking.</p>
          </div>
          <div className="landing-feature-card">
            <strong>Tenant-safe access</strong>
            <p>Role-based users keep each workspace and warehouse securely separated.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
