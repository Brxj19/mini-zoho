import { useAuth } from "../contexts/AuthContext";
import { useDropdown } from "../hooks/useDropdown";
import { Icon } from "./Icon";

export function OrganizationSwitcher() {
  const { open, ref, toggle, close } = useDropdown();
  const { tenant, user } = useAuth();
  const isSuperAdmin = user?.role === "SUPER_ADMIN";

  return (
    <div className="menu-shell" ref={ref}>
      <button className="utility-button with-text org-switcher-button" type="button" onClick={toggle}>
        <span className="org-switcher-copy">
          <strong>{isSuperAdmin ? "Platform Console" : tenant?.company_name ?? "Workspace"}</strong>
          <small>{isSuperAdmin ? "All tenants" : "Current organization"}</small>
        </span>
        <Icon name="chevronDown" size={14} />
      </button>

      {open ? (
        <div className="menu-popover is-open org-switcher-menu">
          <div className="menu-title">Organization</div>
          <button className="menu-item" type="button" onClick={close}>
            <span>{isSuperAdmin ? "Platform Console" : tenant?.company_name ?? "Workspace"}</span>
            <small>{user?.role?.replaceAll("_", " ").toLowerCase() ?? "workspace"}</small>
          </button>
        </div>
      ) : null}
    </div>
  );
}
