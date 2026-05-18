export function PageHeader({
  eyebrow,
  title,
  description,
  actions = null,
  filter = null,
}) {
  return (
    <header className="page-header">
      <div>
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
