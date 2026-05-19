import { BackButton } from "./BackButton";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions = null,
  filter = null,
  backTo = null,
  backLabel = "Back",
}) {
  return (
    <header className="page-header">
      <div>
        {backTo ? <BackButton fallbackTo={backTo} label={backLabel} /> : null}
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        <div className="page-header-title-row">
          <h1>{title}</h1>
          {filter}
        </div>
        {description ? <p className="page-header-description">{description}</p> : null}
      </div>
      {actions ? <div className="page-header-actions">{actions}</div> : null}
    </header>
  );
}
