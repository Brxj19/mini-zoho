import { Link } from "react-router-dom";

import { useDropdown } from "../hooks/useDropdown";
import { useUiStore } from "../stores/uiStore";
import { Icon } from "./Icon";

export function RecentHistoryMenu() {
  const { open, ref, toggle, close } = useDropdown();
  const recentHistory = useUiStore((state) => state.recentHistory);

  return (
    <div className="menu-shell" ref={ref}>
      <button className="icon-button" type="button" onClick={toggle}>
        <Icon name="clock" size={16} />
      </button>

      {open ? (
        <div className="menu-popover recent-history-menu is-open">
          <div className="menu-title">Recent history</div>
          {recentHistory.length ? (
            recentHistory.map((entry) => (
              <Link key={entry.path} className="menu-item" to={entry.path} onClick={close}>
                <span>{entry.label}</span>
                <small>{entry.meta}</small>
              </Link>
            ))
          ) : (
            <div className="menu-empty">Recent records will appear here as you navigate the app.</div>
          )}
        </div>
      ) : null}
    </div>
  );
}
