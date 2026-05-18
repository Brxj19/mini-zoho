import { Link, useMatches } from "react-router-dom";

import { Icon } from "./Icon";

export function Breadcrumbs() {
  const matches = useMatches();
  const crumbs = matches
    .filter((match) => match.handle?.breadcrumb)
    .map((match) => ({
      label:
        typeof match.handle.breadcrumb === "function"
          ? match.handle.breadcrumb(match.params)
          : match.handle.breadcrumb,
      path: match.pathname,
    }));

  if (crumbs.length <= 1) {
    return null;
  }

  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      {crumbs.map((crumb, index) => (
        <span key={crumb.path} className="breadcrumb-item">
          {index > 0 ? <Icon name="chevronRight" size={14} /> : null}
          {index === crumbs.length - 1 ? <span>{crumb.label}</span> : <Link to={crumb.path}>{crumb.label}</Link>}
        </span>
      ))}
    </nav>
  );
}
