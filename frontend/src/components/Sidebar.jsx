import { useEffect, useMemo, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

import { homeNavigation, navigationGroups } from "../lib/navigation";
import { useAuth } from "../contexts/AuthContext";
import { useUiStore } from "../stores/uiStore";
import { Icon } from "./Icon";

export function Sidebar({ mobile = false }) {
  const location = useLocation();
  const { user } = useAuth();
  const role = user?.role;
  const isCollapsed = useUiStore((state) => state.isSidebarCollapsed);
  const closeMobileSidebar = useUiStore((state) => state.closeMobileSidebar);
  const toggleSidebar = useUiStore((state) => state.toggleSidebar);
  const initialGroup = useMemo(
    () =>
      navigationGroups.find((group) => group.items.some((item) => location.pathname.startsWith(item.path)))?.title ??
      navigationGroups[0].title,
    [location.pathname],
  );
  const [openGroup, setOpenGroup] = useState(initialGroup);

  useEffect(() => {
    setOpenGroup(initialGroup);
  }, [initialGroup]);

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
        {!mobile ? (
          <button className="icon-button sidebar-collapse-button" type="button" onClick={toggleSidebar}>
            <Icon name={isCollapsed ? "chevronRight" : "chevronDown"} size={14} />
          </button>
        ) : null}
      </div>

      <nav className="sidebar-groups" aria-label="Primary navigation">
        <NavLink
          className={({ isActive }) => `sidebar-link sidebar-link-home ${isActive ? "is-active" : ""}`}
          to={homeNavigation.path}
          onClick={mobile ? closeMobileSidebar : undefined}
        >
          <Icon name={homeNavigation.icon} size={18} />
          {isCollapsed && !mobile ? null : <span>{homeNavigation.label}</span>}
        </NavLink>

        {navigationGroups.map((group) => {
          const visibleItems = group.items.filter((item) => !item.superAdminOnly || role === "SUPER_ADMIN");
          const isOpen = openGroup === group.title;

          return (
            <div className="sidebar-group" key={group.title}>
              {isCollapsed && !mobile ? null : (
                <button
                  className="sidebar-group-toggle"
                  type="button"
                  onClick={() => setOpenGroup((current) => (current === group.title ? "" : group.title))}
                >
                  <span>{group.title}</span>
                  <Icon name={isOpen ? "chevronDown" : "chevronRight"} size={14} />
                </button>
              )}

              <div className={`sidebar-links-wrap ${(isCollapsed && !mobile) || isOpen ? "is-open" : ""}`}>
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
              </div>
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
