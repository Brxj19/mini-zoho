import { useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { useDropdown } from "../hooks/useDropdown";
import { Icon } from "./Icon";

export function UserMenu() {
  const { open, ref, toggle, close } = useDropdown();
  const { logout, tenant, user } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    close();
    await logout();
  }

  return (
    <div className="menu-shell" ref={ref}>
      <button className="user-chip" type="button" onClick={toggle}>
        <span className="avatar-circle">
          <Icon name="avatar" size={16} />
        </span>
        <span className="user-chip-copy">
          <strong>{user?.name ?? "User"}</strong>
          <small>{tenant?.company_name ?? "Workspace"}</small>
        </span>
        <Icon name="chevronDown" size={14} />
      </button>

      {open ? (
        <div className="menu-popover user-menu is-open">
          <div className="menu-profile">
            <strong>{user?.name ?? "User"}</strong>
            <span>{user?.email ?? "No email"}</span>
            <small>{user?.role?.replaceAll("_", " ") ?? "Workspace user"}</small>
          </div>
          <button className="menu-item" type="button" onClick={() => navigate("/settings")}>
            Settings
          </button>
          <button className="menu-item" type="button" onClick={() => navigate("/notifications")}>
            Notifications
          </button>
          <button className="menu-item is-danger" type="button" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      ) : null}
    </div>
  );
}
