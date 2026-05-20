import { Link } from "react-router-dom";

import { Icon } from "./Icon";

const miniCards = [
  {
    label: "Low stock alert",
    value: "12 items need replenishment",
    icon: "alert",
    tone: "warning",
  },
  {
    label: "Purchase queue",
    value: "8 receives pending today",
    icon: "truck",
    tone: "info",
  },
  {
    label: "Warehouse flow",
    value: "3 transfers in transit",
    icon: "warehouse",
    tone: "neutral",
  },
];

export function AuthShowcase({ eyebrow, title, description, secondaryCtaLabel, secondaryCtaTo, badge = "Inventory operations" }) {
  return (
    <section className="auth-showcase">
      <div className="auth-showcase-topbar">
        <Link to="/" className="public-brand">
          <span className="public-brand-mark">
            <span />
            <span />
            <span />
            <span />
          </span>
          <span>Northstar Inventory</span>
        </Link>

        {secondaryCtaLabel && secondaryCtaTo ? (
          <Link to={secondaryCtaTo} className="auth-showcase-link">
            {secondaryCtaLabel}
          </Link>
        ) : null}
      </div>

      <div className="auth-showcase-copy">
        <span className="auth-showcase-badge">{badge}</span>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>

      <div className="auth-showcase-stage">
        <div className="auth-showcase-floating auth-showcase-floating-left">
          <strong>Today’s ops</strong>
          <div className="auth-showcase-progress">
            <span>Inbound stock booked</span>
            <strong>84%</strong>
          </div>
          <div className="auth-showcase-bar">
            <span />
          </div>
        </div>

        <div className="auth-showcase-floating auth-showcase-floating-right">
          <span className="auth-showcase-floating-icon">
            <Icon name="packagePlus" size={18} />
          </span>
          <div>
            <strong>Stock synced</strong>
            <p>Inventory, orders, and warehouse positions stay aligned.</p>
          </div>
        </div>

        <div className="auth-showcase-device">
          <div className="auth-showcase-device-header">
            <div className="auth-showcase-device-pill">Northstar workspace</div>
            <div className="auth-showcase-device-actions">
              <span />
              <span />
              <span />
            </div>
          </div>

          <div className="auth-showcase-device-body">
            <div className="auth-showcase-sidebar">
              <span className="is-active">Dashboard</span>
              <span>Items</span>
              <span>Orders</span>
              <span>Warehouses</span>
            </div>

            <div className="auth-showcase-canvas">
              <div className="auth-showcase-metric-row">
                <article>
                  <span>Stock on hand</span>
                  <strong>18,420</strong>
                </article>
                <article>
                  <span>To be shipped</span>
                  <strong>146</strong>
                </article>
                <article>
                  <span>Pending receives</span>
                  <strong>22</strong>
                </article>
              </div>

              <div className="auth-showcase-board">
                <div className="auth-showcase-board-card auth-showcase-board-card-large">
                  <div className="auth-showcase-board-header">
                    <strong>Warehouse activity</strong>
                    <span>Live</span>
                  </div>
                  <div className="auth-showcase-bars">
                    <span style={{ height: "48%" }} />
                    <span style={{ height: "76%" }} />
                    <span style={{ height: "62%" }} />
                    <span style={{ height: "88%" }} />
                    <span style={{ height: "54%" }} />
                  </div>
                </div>

                <div className="auth-showcase-board-card">
                  <div className="auth-showcase-board-header">
                    <strong>Order split</strong>
                  </div>
                  <div className="auth-showcase-donut" />
                </div>
              </div>

              <div className="auth-showcase-mini-grid">
                {miniCards.map((card) => (
                  <article key={card.label} className={`auth-showcase-mini-card tone-${card.tone}`}>
                    <span className="auth-showcase-mini-icon">
                      <Icon name={card.icon} size={16} />
                    </span>
                    <div>
                      <strong>{card.label}</strong>
                      <p>{card.value}</p>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
