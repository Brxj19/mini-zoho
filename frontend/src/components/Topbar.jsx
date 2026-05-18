import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useDropdown } from "../hooks/useDropdown";
import { useActiveOrganization, useAuthStore } from "../stores/authStore";
import { useUiStore } from "../stores/uiStore";
import { Icon } from "./Icon";
import { OrganizationSwitcher } from "./OrganizationSwitcher";
import { QuickCreateMenu } from "./QuickCreateMenu";
import { RecentHistoryMenu } from "./RecentHistoryMenu";
import { SearchInput } from "./SearchInput";

export function Topbar() {
  const [query, setQuery] = useState("");
  const helpDropdown = useDropdown();
  const notificationDropdown = useDropdown();
  const userDropdown = useDropdown();
  const activeOrganization = useActiveOrganization();
  const notifications = useUiStore((state) => state.notifications);
  const fetchNotifications = useUiStore((state) => state.fetchNotifications);
  const markNotificationRead = useUiStore((state) => state.markNotificationRead);
  const markAllNotificationsRead = useUiStore((state) => state.markAllNotificationsRead);
  const openMobileSidebar = useUiStore((state) => state.openMobileSidebar);
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const unreadCount = notifications.filter((notification) => notification.unread).length;

  useEffect(() => {
    fetchNotifications().catch(() => undefined);
  }, [fetchNotifications]);

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

        <div className="menu-shell" ref={notificationDropdown.ref}>
          <button className="icon-button" type="button" onClick={notificationDropdown.toggle}>
            <Icon name="bell" size={16} />
            {unreadCount ? <span className="notification-count">{unreadCount}</span> : null}
          </button>
          {notificationDropdown.open ? (
            <div className="menu-popover notifications-menu is-open">
              <div className="menu-row">
                <div className="menu-title">Notifications</div>
                <button className="text-button" type="button" onClick={() => markAllNotificationsRead()}>
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
          ) : null}
        </div>

        <Link className="icon-button" to="/settings">
          <Icon name="settings" size={16} />
        </Link>

        <div className="menu-shell" ref={helpDropdown.ref}>
          <button className="icon-button" type="button" onClick={helpDropdown.toggle}>
            <Icon name="help" size={16} />
          </button>
          {helpDropdown.open ? (
            <div className="menu-popover is-open">
              <div className="menu-title">Need help?</div>
              <div className="menu-empty">Support center wiring can plug in here without another layout change.</div>
            </div>
          ) : null}
        </div>

        <OrganizationSwitcher />

        <div className="menu-shell" ref={userDropdown.ref}>
          <button className="user-chip" type="button" onClick={userDropdown.toggle}>
            <span className="avatar-circle">
              <Icon name="avatar" size={16} />
            </span>
            <span>{user?.name ?? "User"}</span>
          </button>
          {userDropdown.open ? (
            <div className="menu-popover is-open">
              <button className="menu-item" type="button" onClick={() => navigate("/settings")}>
                Settings
              </button>
              {user?.role !== "SUPER_ADMIN" ? (
                <button className="menu-item" type="button" onClick={() => navigate("/setup")}>
                  Organization setup
                </button>
              ) : null}
              <button className="menu-item is-danger" type="button" onClick={logout}>
                Sign out
              </button>
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
}
