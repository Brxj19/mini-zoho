import { useMemo, useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { canAccess, navigationGroups, resolveActiveGroup } from "../lib/uiConfig";

function Glyph({ name }) {
  const commonProps = { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.8", strokeLinecap: "round", strokeLinejoin: "round" };
  switch (name) {
    case "home":
      return (
        <svg {...commonProps}><path d="M3 10.5 12 3l9 7.5" /><path d="M5.5 9.5V20h13V9.5" /><path d="M9.5 20v-6h5v6" /></svg>
      );
    case "box":
      return (
        <svg {...commonProps}><path d="M4 8.5 12 4l8 4.5-8 4.5L4 8.5Z" /><path d="M4 8.5V17l8 4 8-4V8.5" /><path d="M12 13v8" /></svg>
      );
    case "layers":
      return (
        <svg {...commonProps}><path d="m12 4-8 4 8 4 8-4-8-4Z" /><path d="m4 12 8 4 8-4" /><path d="m4 16 8 4 8-4" /></svg>
      );
    case "cart":
      return (
        <svg {...commonProps}><circle cx="9" cy="19" r="1.5" /><circle cx="17" cy="19" r="1.5" /><path d="M3 4h2l2.6 10.3a1 1 0 0 0 1 .7h8.9a1 1 0 0 0 1-.8L22 7H7" /></svg>
      );
    case "bag":
      return (
        <svg {...commonProps}><path d="M6 8h12l1 12H5L6 8Z" /><path d="M9 8a3 3 0 1 1 6 0" /></svg>
      );
    case "warehouse":
      return (
        <svg {...commonProps}><path d="M3 10 12 4l9 6v9H3v-9Z" /><path d="M7 19v-5h10v5" /><path d="M7 10h.01M12 10h.01M17 10h.01" /></svg>
      );
    case "chart":
      return (
        <svg {...commonProps}><path d="M4 20V10" /><path d="M10 20V4" /><path d="M16 20v-7" /><path d="M22 20v-11" /></svg>
      );
    case "users":
      return (
        <svg {...commonProps}><circle cx="9" cy="8" r="3" /><path d="M3 20a6 6 0 0 1 12 0" /><circle cx="17" cy="10" r="2.5" /><path d="M15 20a5 5 0 0 1 6-4.8" /></svg>
      );
    case "bell":
      return (
        <svg {...commonProps}><path d="M6 9a6 6 0 1 1 12 0c0 6 2 7 2 7H4s2-1 2-7" /><path d="M10 20a2 2 0 0 0 4 0" /></svg>
      );
    case "plus":
      return (
        <svg {...commonProps}><path d="M12 5v14" /><path d="M5 12h14" /></svg>
      );
    case "settings":
      return (
        <svg {...commonProps}><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 0 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 0 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 0 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3h.1a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5h.1a1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 0 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8v.1a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z" /></svg>
      );
    default:
      return (
        <svg {...commonProps}><circle cx="12" cy="12" r="8" /></svg>
      );
  }
}

export function AppShell() {
  const { logout, user, tenant } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const activeGroup = useMemo(() => resolveActiveGroup(location.pathname), [location.pathname]);
  const [expandedKey, setExpandedKey] = useState(activeGroup.key);
  const [searchText, setSearchText] = useState("");
  const visibleGroup = navigationGroups.find((group) => group.key === expandedKey) ?? activeGroup;

  const filteredItems = visibleGroup.items.filter((item) => canAccess(user?.role, item.roles));
  const quickActionPath =
    filteredItems.find((item) => item.label.toLowerCase().startsWith("create"))?.path ??
    filteredItems[0]?.path ??
    "/";

  return (
    <div className="saas-shell">
      <div className="notice-strip">
        <span>Workspace UI refresh is live. The operations shell now favors faster navigation and denser context.</span>
      </div>

      <header className="shell-topbar">
        <div className="shell-brand">
          <div className="shell-brand-mark">N</div>
          <div>
            <strong>Northstar Inventory</strong>
            <span>Operations cockpit</span>
          </div>
        </div>

        <div className="shell-topbar-search">
          <Glyph name="chart" />
          <input
            className="shell-search"
            value={searchText}
            onChange={(event) => setSearchText(event.target.value)}
            placeholder="Search products, customers, orders, reports…"
          />
        </div>

        <div className="shell-topbar-actions">
          <span className="utility-copy">Workspace secured</span>
          <button className="icon-button accent-button" type="button" aria-label="Create" onClick={() => navigate(quickActionPath)}>
            <Glyph name="plus" />
          </button>
          <Link className="icon-button" to="/notifications" aria-label="Notifications">
            <Glyph name="bell" />
          </Link>
          <Link className="icon-button" to="/settings" aria-label="Settings">
            <Glyph name="settings" />
          </Link>
          <div className="user-chip">
            <span>{tenant?.company_name ?? "Platform"}</span>
            <strong>{user?.name ?? "User"}</strong>
          </div>
        </div>
      </header>

      <div className="shell-body">
        <aside className="rail-nav" aria-label="Primary">
          {navigationGroups.map((group) => {
            const isActive = activeGroup.key === group.key;
            const isVisible = group.items.some((item) => canAccess(user?.role, item.roles));
            if (!isVisible) {
              return null;
            }
            return (
              <button
                className={`rail-button ${isActive ? "rail-button-active" : ""}`}
                key={group.key}
                type="button"
                onClick={() => setExpandedKey(group.key)}
              >
                <span className="rail-icon"><Glyph name={group.icon} /></span>
                <span>{group.label}</span>
              </button>
            );
          })}

          <button className="rail-button rail-button-exit" type="button" onClick={() => logout()}>
            <span className="rail-icon">↩</span>
            <span>Exit</span>
          </button>
        </aside>

        <div className="submenu-panel">
          <div className="submenu-card">
            <div className="submenu-header">
              <span>{visibleGroup.label}</span>
            </div>
            <nav className="submenu-links">
              {filteredItems.map((item) => (
                <NavLink
                  className={({ isActive }) => `submenu-link ${isActive ? "submenu-link-active" : ""}`}
                  key={item.path}
                  to={item.path}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>

        <main className="shell-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
