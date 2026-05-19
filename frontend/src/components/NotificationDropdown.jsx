import { Link } from "react-router-dom";

import { useDropdown } from "../hooks/useDropdown";
import { useUiStore } from "../stores/uiStore";
import { Icon } from "./Icon";

export function NotificationDropdown() {
  const { open, ref, toggle, close } = useDropdown();
  const notifications = useUiStore((state) => state.notifications);
  const markNotificationRead = useUiStore((state) => state.markNotificationRead);
  const markAllNotificationsRead = useUiStore((state) => state.markAllNotificationsRead);
  const unreadCount = notifications.filter((notification) => notification.unread).length;

  async function handleRead(notificationId) {
    await markNotificationRead(notificationId);
  }

  return (
    <div className="menu-shell" ref={ref}>
      <button className="icon-button topbar-icon-button" type="button" onClick={toggle} aria-label="Open notifications">
        <Icon name="bell" size={16} />
        {unreadCount ? <span className="notification-count">{unreadCount}</span> : null}
      </button>

      {open ? (
        <div className="menu-popover notifications-menu is-open">
          <div className="menu-row">
            <div>
              <div className="menu-title">Notifications</div>
              <div className="menu-caption">Recent alerts and system updates</div>
            </div>
            <button className="text-button menu-action-link" type="button" onClick={() => markAllNotificationsRead()}>
              Mark all read
            </button>
          </div>

          {notifications.length ? (
            <>
              <div className="menu-scroll">
                {notifications.map((notification) => (
                  <button
                    key={notification.id}
                    className={`menu-item notification-item ${notification.unread ? "is-unread" : ""}`}
                    type="button"
                    onClick={() => handleRead(notification.id)}
                  >
                    <span>{notification.title}</span>
                    <small>{notification.detail}</small>
                  </button>
                ))}
              </div>
              <Link className="menu-footer-link" to="/notifications" onClick={close}>
                View all notifications
              </Link>
            </>
          ) : (
            <div className="menu-empty">No notifications yet. Low stock and order events will appear here.</div>
          )}
        </div>
      ) : null}
    </div>
  );
}
