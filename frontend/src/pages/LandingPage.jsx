import { Link } from "react-router-dom";

import { Icon } from "../components/Icon";

const featureCards = [
  {
    title: "Inventory that stays accurate",
    description: "Track stock, transfers, receipts, and reservations from one source of truth.",
    icon: "warehouse",
  },
  {
    title: "Sales and purchasing in sync",
    description: "Move from order to invoice or bill without losing status, stock, or ownership context.",
    icon: "clipboard",
  },
  {
    title: "Built for growing teams",
    description: "Role-based access, multi-tenant controls, and clean operational visibility out of the box.",
    icon: "shield",
  },
];

const heroStats = [
  { value: "Orders", label: "Sales, purchasing, invoicing, and returns in one flow" },
  { value: "Warehouses", label: "Transfer, replenish, and reconcile stock with less friction" },
  { value: "Teams", label: "Role-safe workspaces for admins, inventory, sales, and purchasing" },
];

const solutionCards = [
  {
    title: "Inventory teams",
    description: "Keep stock positions accurate across receipts, transfers, adjustments, and warehouse movement.",
  },
  {
    title: "Sales teams",
    description: "Move from customer order to package, invoice, and delivery with clearer status ownership.",
  },
  {
    title: "Purchase teams",
    description: "Track inbound orders, receives, bills, and vendor follow-up without scattered spreadsheets.",
  },
];

const whyNorthstar = [
  "A cleaner inventory workspace that stays readable as operations grow",
  "Stock-aware workflows so orders and warehouse positions stay in sync",
  "Multi-tenant and role-based structure built for real operations teams",
];

const footerColumns = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "#features" },
      { label: "Solutions", href: "#solutions" },
      { label: "Why Northstar", href: "#why-northstar" },
    ],
  },
  {
    title: "Access",
    links: [
      { label: "Sign in", to: "/login" },
      { label: "Create workspace", to: "/register" },
    ],
  },
];

export function LandingPage() {
  return (
    <div className="public-screen marketing-screen">
      <div className="marketing-shell">
        <header className="marketing-nav">
          <Link to="/" className="public-brand">
            <span className="public-brand-mark">
              <span />
              <span />
              <span />
              <span />
            </span>
            <span>Northstar Inventory</span>
          </Link>

          <nav className="marketing-nav-links" aria-label="Marketing">
            <a href="#features">Features</a>
            <a href="#solutions">Solutions</a>
            <a href="#pricing">Why Northstar</a>
          </nav>

          <div className="marketing-nav-actions">
            <Link to="/login" className="marketing-nav-link">
              Sign in
            </Link>
            <Link to="/register" className="ghost-button marketing-outline-button">
              Get started
            </Link>
          </div>
        </header>

        <section className="marketing-stage">
          <div className="marketing-stage-note">
            <span className="marketing-note-pin" />
            <strong>Daily control</strong>
            <p>Keep stock, orders, and warehouse work moving without scattered tools.</p>
          </div>

          <div className="marketing-stage-panel marketing-stage-panel-left">
            <div className="marketing-mini-card">
              <div className="marketing-mini-card-icon">
                <Icon name="packagePlus" size={20} />
              </div>
              <div>
                <strong>Inbound stock</strong>
                <span>Receipts posted to the right warehouse</span>
              </div>
            </div>
          </div>

          <div className="marketing-stage-panel marketing-stage-panel-right">
            <div className="marketing-reminder-card">
              <strong>Today</strong>
              <span>Follow up pending purchase receipts and low stock items.</span>
            </div>
          </div>

          <div className="marketing-stage-panel marketing-stage-panel-bottom">
            <div className="marketing-integration-card">
              <strong>Connected workflows</strong>
              <div className="marketing-integration-icons">
                <span>PO</span>
                <span>SO</span>
                <span>INV</span>
              </div>
            </div>
          </div>

          <div className="marketing-stage-content">
            <div className="marketing-stage-badge">
              <Icon name="sparkles" size={14} />
              <span>Inventory SaaS for modern operations teams</span>
            </div>

            <h1>
              Keep stock, orders,
              <br />
              and warehouse work
              <span> in one clear system.</span>
            </h1>

            <p>
              Northstar helps teams stay fast without losing control. Track inventory, run purchasing and sales,
              and keep every warehouse move visible from one clean operational workspace.
            </p>

            <div className="marketing-stage-actions">
              <Link to="/register" className="primary-button marketing-cta-button">
                Start free trial
              </Link>
              <Link to="/login" className="ghost-button marketing-outline-button">
                Sign in
              </Link>
            </div>

            <div className="marketing-stage-stats">
              {heroStats.map((item) => (
                <article key={item.value} className="marketing-stat-card">
                  <strong>{item.value}</strong>
                  <p>{item.label}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="marketing-feature-strip" id="features">
          {featureCards.map((item) => (
            <article key={item.title} className="marketing-feature-card">
              <span className="marketing-feature-icon">
                <Icon name={item.icon} size={18} />
              </span>
              <strong>{item.title}</strong>
              <p>{item.description}</p>
            </article>
          ))}
        </section>

        <section className="marketing-detail-section" id="solutions">
          <div className="marketing-section-heading">
            <p className="eyebrow">Solutions</p>
            <h2>Built for the teams that move inventory every day.</h2>
            <p>
              Northstar is designed around the operational handoffs that usually break stock accuracy:
              receiving, transferring, billing, shipping, and reconciliation.
            </p>
          </div>

          <div className="marketing-solution-grid">
            {solutionCards.map((item) => (
              <article key={item.title} className="marketing-solution-card">
                <strong>{item.title}</strong>
                <p>{item.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="marketing-spotlight-grid" id="why-northstar">
          <article className="marketing-spotlight-card marketing-spotlight-primary">
            <p className="eyebrow">Why Northstar</p>
            <h2>Less manual chasing. More control over what is actually moving.</h2>
            <p>
              Use a single place for stock in, stock out, transfers, orders, invoices, and bills instead of
              stitching together separate operational tools.
            </p>
          </article>

          <article className="marketing-spotlight-card">
            <p className="eyebrow">Why teams switch</p>
            <ul className="marketing-spotlight-list">
              {whyNorthstar.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        </section>

        <section className="marketing-footer-cta">
          <div>
            <p className="eyebrow">Ready to start?</p>
            <h2>Set up a cleaner inventory workspace for your team.</h2>
          </div>
          <div className="marketing-stage-actions">
            <Link to="/register" className="primary-button marketing-cta-button">
              Create workspace
            </Link>
            <Link to="/login" className="ghost-button marketing-outline-button">
              Sign in
            </Link>
          </div>
        </section>

        <footer className="marketing-footer">
          <div className="marketing-footer-brand">
            <Link to="/" className="public-brand">
              <span className="public-brand-mark">
                <span />
                <span />
                <span />
                <span />
              </span>
              <span>Northstar Inventory</span>
            </Link>
            <p>
              A modern inventory operations workspace for stock control, warehouses, purchasing, sales, and tenant-safe access.
            </p>
          </div>

          <div className="marketing-footer-links">
            {footerColumns.map((column) => (
              <div key={column.title} className="marketing-footer-column">
                <strong>{column.title}</strong>
                {column.links.map((link) =>
                  link.to ? (
                    <Link key={link.label} to={link.to}>
                      {link.label}
                    </Link>
                  ) : (
                    <a key={link.label} href={link.href}>
                      {link.label}
                    </a>
                  ),
                )}
              </div>
            ))}
          </div>
        </footer>
      </div>
    </div>
  );
}
