import { ComingSoon } from "../components/common/ComingSoon";
import { PageHeader } from "../components/PageHeader";

export function PlaceholderModulePage({ title, description, actionLabel, actionTo }) {
  return (
    <div className="page-stack">
      <PageHeader eyebrow="Placeholder Module" title={title} description={description} />
      <ComingSoon
        title={`${title} is not connected yet`}
        description="This screen is intentionally presented as a forward-looking placeholder until backend support exists."
      />
    </div>
  );
}
