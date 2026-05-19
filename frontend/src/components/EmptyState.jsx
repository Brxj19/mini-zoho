import { Link } from "react-router-dom";

import { Icon } from "./Icon";

export function EmptyState({ title, description, actionLabel, actionTo, onAction, icon = "box", actionTone = "primary" }) {
  const actionClassName = actionTone === "ghost" ? "button button-ghost" : "button button-primary";

  return (
    <div className="empty-state" role="status" aria-live="polite">
      <div className="empty-state-icon">
        <Icon name={icon} size={22} />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {actionLabel && actionTo ? <Link className={actionClassName} to={actionTo}>{actionLabel}</Link> : null}
      {actionLabel && !actionTo && onAction ? (
        <button className={actionClassName} type="button" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
