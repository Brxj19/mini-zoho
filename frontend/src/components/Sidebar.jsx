import { useState } from "react";
import { NavLink } from "react-router-dom";

import { navigationGroups } from "../lib/navigation";
import { useAuthStore } from "../stores/authStore";
import { useUiStore } from "../stores/uiStore";
import { Icon } from "./Icon";

export function Sidebar({ mobile = false }) {
  const [openGroups, setOpenGroups] = useState(
    Object.fromEntries(navigationGroups.map((group) => [group.title, true])),
  );
  const role = useAuthStore((state) => state.user?.role);
  const isCollapsed = useUiStore((state) => state.isSidebarCollapsed);
  const closeMobileSidebar = useUiStore((state) => state.closeMobileSidebar);

  return (
    <aside className={`sidebar ${isCollapsed && !mobile ? "is-collapsed" : ""}`}>
      <div className="sidebar-brand">
        <div className="brand-symbol">N</div>
        {isCollapsed && !mobile ? null : (
          <div>
            <strong>Northstar Inventory</strong>
            <p>Retail operations command center</p>
          </div>
        )}
      </div>

      <nav className="sidebar-groups" aria-label="Primary navigation">
        {navigationGroups.map((group) => {
          const visibleItems = group.items.filter((item) => !item.superAdminOnly || role === "SUPER_ADMIN");

          return (
            <div className="sidebar-group" key={group.title}>
              {isCollapsed && !mobile ? null : (
                <button
                  className="sidebar-group-toggle"
                  type="button"
                  onClick={() =>
                    setOpenGroups((current) => ({ ...current, [group.title]: !current[group.title] }))
                  }
                >
                  <span>{group.title}</span>
                  <Icon name={openGroups[group.title] ? "chevronDown" : "chevronRight"} size={14} />
                </button>
              )}

              {(isCollapsed && !mobile ? true : openGroups[group.title]) ? (
                <div className="sidebar-links">
                  {visibleItems.map((item) => (
                    <NavLink
                      key={item.path}
                      className={({ isActive }) => `sidebar-link ${isActive ? "is-active" : ""}`}
                      to={item.path}
                      onClick={mobile ? closeMobileSidebar : undefined}
                    >
                      <Icon name={item.icon} size={18} />
                      {isCollapsed && !mobile ? null : <span>{item.label}</span>}
                    </NavLink>
                  ))}
                </div>
              ) : null}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
