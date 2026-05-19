import { useEffect, useState } from "react";
import { useMatches } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { useDropdown } from "../hooks/useDropdown";
import { useUiStore } from "../stores/uiStore";
import { Icon } from "./Icon";
import { NotificationDropdown } from "./NotificationDropdown";
import { OrganizationSwitcher } from "./OrganizationSwitcher";
import { QuickCreateMenu } from "./QuickCreateMenu";
import { RecentHistoryMenu } from "./RecentHistoryMenu";
import { SearchInput } from "./SearchInput";
import { UserMenu } from "./UserMenu";

export function Topbar() {
  const [query, setQuery] = useState("");
  const helpDropdown = useDropdown();
  const matches = useMatches();
  const { user, tenant } = useAuth();
  const fetchNotifications = useUiStore((state) => state.fetchNotifications);
  const openMobileSidebar = useUiStore((state) => state.openMobileSidebar);

  useEffect(() => {
    fetchNotifications().catch(() => undefined);
  }, [fetchNotifications]);

  const currentMatch = [...matches].reverse().find((match) => match.handle?.title);
  const currentTitle =
    typeof currentMatch?.handle?.title === "function"
      ? currentMatch.handle.title(currentMatch.params)
      : currentMatch?.handle?.title ?? "Dashboard";
  const currentSection = currentMatch?.handle?.section ?? "Workspace";

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="icon-button mobile-only" type="button" onClick={openMobileSidebar}>
          <Icon name="menu" size={18} />
        </button>
        <div className="topbar-brand-shell">
          <div className="topbar-brand">
            <span className="topbar-label">{currentTitle}</span>
            <small>{currentSection}</small>
          </div>
          <div className="topbar-workspace-pill">{tenant?.company_name ?? "Northstar Inventory"}</div>
        </div>
      </div>

      <div className="topbar-search">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search items, orders, customers, vendors, warehouses..."
        />
      </div>

      <div className="topbar-actions">
        <QuickCreateMenu />
        <RecentHistoryMenu />
        <NotificationDropdown />

        <div className="menu-shell" ref={helpDropdown.ref}>
          <button className="icon-button topbar-icon-button" type="button" onClick={helpDropdown.toggle}>
            <Icon name="help" size={16} />
          </button>
          {helpDropdown.open ? (
            <div className="menu-popover is-open">
              <div className="menu-row">
                <div>
                  <div className="menu-title">Help & support</div>
                  <div className="menu-caption">Guides, contact points, and onboarding</div>
                </div>
              </div>
              <div className="menu-empty">Support, setup guides, and product-tour actions will live here in the redesigned shell.</div>
            </div>
          ) : null}
        </div>

        <OrganizationSwitcher />
        <UserMenu />
      </div>
    </header>
  );
}
