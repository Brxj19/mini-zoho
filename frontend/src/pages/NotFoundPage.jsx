import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="auth-screen">
      <section className="auth-panel compact-panel">
        <div className="auth-copy">
          <p className="eyebrow">Missing View</p>
          <h1>This workspace route does not exist.</h1>
          <p>The URL may be outdated, or the page has not been mapped into the current UI flow yet.</p>
          <Link className="primary-button inline-button" to="/">
            Return to Dashboard
          </Link>
        </div>
      </section>
    </div>
  );
}
