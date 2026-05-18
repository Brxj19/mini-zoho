import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="panel-card">
      <p className="eyebrow">404</p>
      <h2>Page not found</h2>
      <p>The route you requested is not part of the starter shell yet.</p>
      <Link className="primary-button inline-button" to="/">
        Back to dashboard
      </Link>
    </div>
  );
}

