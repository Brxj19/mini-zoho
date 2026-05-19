import { useAuth } from "../contexts/AuthContext";
import { useDropdown } from "../hooks/useDropdown";
import { Icon } from "./Icon";

export function OrganizationSwitcher() {
  const { open, ref, toggle, close } = useDropdown();
  const { tenant, user } = useAuth();

  return (
    <div className="menu-shell" ref={ref}>
      <button className="utility-button with-text" type="button" onClick={toggle}>
        <span>{tenant?.company_name ?? "Platform"}</span>
        <Icon name="chevronDown" size={14} />
      </button>

      {open ? (
        <div className="menu-popover is-open">
          <button className="menu-item" type="button" onClick={close}>
            <span>{tenant?.company_name ?? "Platform Console"}</span>
            <small>{user?.role?.replaceAll("_", " ").toLowerCase() ?? "workspace"}</small>
          </button>
        </div>
      ) : null}
    </div>
  );
}
