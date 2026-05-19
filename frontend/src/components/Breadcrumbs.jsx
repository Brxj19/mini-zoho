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
  const uniqueCrumbs = crumbs.filter(
    (crumb, index) => index === crumbs.findIndex((entry) => entry.path === crumb.path && entry.label === crumb.label),
  );

  if (uniqueCrumbs.length <= 1) {
    return null;
  }

  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      {uniqueCrumbs.map((crumb, index) => (
        <span key={`${crumb.path}-${crumb.label}`} className="breadcrumb-item">
          {index > 0 ? <Icon name="chevronRight" size={14} /> : null}
          {index === uniqueCrumbs.length - 1 ? <span>{crumb.label}</span> : <Link to={crumb.path}>{crumb.label}</Link>}
        </span>
      ))}
    </nav>
  );
}
