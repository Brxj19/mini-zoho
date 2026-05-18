import { Outlet } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

const primaryNavigation = [
  "Dashboard",
  "Items",
  "Inventory",
  "Warehouses",
  "Sales",
  "Purchases",
  "Customers",
  "Vendors",
  "Reports",
  "Users",
  "Settings",
];

export function AppShell() {
  const { logout, user, tenant } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand-mark">Northstar</div>
          <p className="brand-copy">
            {tenant?.company_name ?? "Platform Console"}
            <br />
            Inventory operations for modern retail teams.
          </p>
        </div>

        <nav className="sidebar-nav" aria-label="Primary">
          {primaryNavigation.map((item) => (
            <button className="nav-link" key={item} type="button">
              {item}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="status-badge">{user?.role?.replaceAll("_", " ") ?? "Guest"}</span>
          <strong>{user?.name ?? "Unassigned user"}</strong>
          <span className="sidebar-subtle">{user?.email ?? "No active session"}</span>
        </div>
      </aside>

      <div className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Workspace</p>
            <h1 className="page-title">{tenant?.company_name ?? "Northstar Inventory"}</h1>
          </div>

          <div className="topbar-actions">
            <input className="search-input" placeholder="Search products, orders, vendors..." />
            <button className="ghost-button" type="button" onClick={() => logout()}>
              Sign out
            </button>
          </div>
        </header>

        <main className="content-area">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
