import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useActiveOrganization, useAuthStore } from "../stores/authStore";
import { useUiStore } from "../stores/uiStore";
import { Icon } from "./Icon";
import { OrganizationSwitcher } from "./OrganizationSwitcher";
import { QuickCreateMenu } from "./QuickCreateMenu";
import { RecentHistoryMenu } from "./RecentHistoryMenu";
import { SearchInput } from "./SearchInput";

export function Topbar() {
  const [query, setQuery] = useState("");
  const [helpOpen, setHelpOpen] = useState(false);
  const activeOrganization = useActiveOrganization();
  const notifications = useUiStore((state) => state.notifications);
  const markNotificationRead = useUiStore((state) => state.markNotificationRead);
  const markAllNotificationsRead = useUiStore((state) => state.markAllNotificationsRead);
  const openMobileSidebar = useUiStore((state) => state.openMobileSidebar);
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const unreadCount = notifications.filter((notification) => notification.unread).length;

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="icon-button mobile-only" type="button" onClick={openMobileSidebar}>
          <Icon name="menu" size={18} />
        </button>
        <div className="topbar-brand">
          <span className="topbar-label">Northstar Inventory</span>
          <small>{activeOrganization?.plan ?? "Workspace"} plan</small>
        </div>
      </div>

      <div className="topbar-search">
        <SearchInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search items, orders, customers, vendors..."
        />
      </div>

      <div className="topbar-actions">
        <QuickCreateMenu />
        <RecentHistoryMenu />

        <div className="menu-shell">
          <button className="icon-button" type="button">
            <Icon name="bell" size={16} />
            {unreadCount ? <span className="notification-count">{unreadCount}</span> : null}
          </button>
          <div className="menu-popover notifications-menu">
            <div className="menu-row">
              <div className="menu-title">Notifications</div>
              <button className="text-button" type="button" onClick={markAllNotificationsRead}>
                Mark all read
              </button>
            </div>
            {notifications.map((notification) => (
              <button
                key={notification.id}
                className={`menu-item notification-item ${notification.unread ? "is-unread" : ""}`}
                type="button"
                onClick={() => markNotificationRead(notification.id)}
              >
                <span>{notification.title}</span>
                <small>{notification.detail}</small>
              </button>
            ))}
          </div>
        </div>

        <Link className="icon-button" to="/settings">
          <Icon name="settings" size={16} />
        </Link>

        <div className="menu-shell">
          <button className="icon-button" type="button" onClick={() => setHelpOpen((value) => !value)}>
            <Icon name="help" size={16} />
          </button>
          {helpOpen ? (
            <div className="menu-popover">
              <div className="menu-title">Need help?</div>
              <div className="menu-empty">
                UI support placeholders live here until the help center module is connected.
              </div>
            </div>
          ) : null}
        </div>

        <OrganizationSwitcher />

        <div className="menu-shell">
          <button className="user-chip" type="button">
            <span className="avatar-circle">
              <Icon name="avatar" size={16} />
            </span>
            <span>{user?.name ?? "User"}</span>
          </button>
          <div className="menu-popover">
            <button className="menu-item" type="button" onClick={() => navigate("/settings")}>
              Settings
            </button>
            <button className="menu-item" type="button" onClick={() => navigate("/setup")}>
              Organization setup
            </button>
            <button className="menu-item is-danger" type="button" onClick={logout}>
              Sign out
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
