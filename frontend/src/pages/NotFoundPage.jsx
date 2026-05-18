import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="standalone-page">
      <div className="standalone-shell">
        <section className="panel-card">
          <p className="eyebrow">404</p>
          <h1>Page not found</h1>
          <p>The route you requested is not part of the current Northstar Inventory experience.</p>
          <Link className="button button-primary" to="/">
            Back to dashboard
          </Link>
        </section>
      </div>
    </div>
  );
}
