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
  const { logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand-mark">Northstar</div>
          <p className="brand-copy">Inventory operations for modern retail teams.</p>
        </div>

        <nav className="sidebar-nav" aria-label="Primary">
          {primaryNavigation.map((item) => (
            <button className="nav-link" key={item} type="button">
              {item}
            </button>
          ))}
        </nav>
      </aside>

      <div className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Workspace</p>
            <h1 className="page-title">Northstar Inventory</h1>
          </div>

          <div className="topbar-actions">
            <input className="search-input" placeholder="Search products, orders, vendors..." />
            <button className="ghost-button" type="button" onClick={logout}>
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

