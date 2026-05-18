import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";

export function PlaceholderModulePage({ title, description, actionLabel, actionTo }) {
  return (
    <div className="page-stack">
      <PageHeader eyebrow="Placeholder Module" title={title} description={description} />
      <EmptyState
        icon="sparkles"
        title={`${title} is not connected yet`}
        description="This screen is intentionally presented as a forward-looking placeholder until backend support exists."
        actionLabel={actionLabel}
        actionTo={actionTo}
      />
    </div>
  );
}
