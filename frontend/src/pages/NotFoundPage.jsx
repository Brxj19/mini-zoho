import { EmptyState } from "../components/common/EmptyState";

export function NotFoundPage() {
  return (
    <div className="auth-screen">
      <section className="auth-panel compact-panel">
        <div className="auth-copy">
          <p className="eyebrow">Missing View</p>
          <EmptyState
            animationKey="notFound404"
            title="This workspace route does not exist."
            description="The URL may be outdated, or the page has not been mapped into the current UI flow yet."
            primaryActionLabel="Return to Dashboard"
            primaryActionTo="/"
          />
        </div>
      </section>
    </div>
  );
}
