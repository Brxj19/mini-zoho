import { useState } from "react";
import { Link } from "react-router-dom";

import { useUiStore } from "../stores/uiStore";
import { Icon } from "./Icon";

export function RecentHistoryMenu() {
  const [open, setOpen] = useState(false);
  const recentHistory = useUiStore((state) => state.recentHistory);

  return (
    <div className="menu-shell">
      <button className="icon-button" type="button" onClick={() => setOpen((value) => !value)}>
        <Icon name="clock" size={16} />
      </button>

      {open ? (
        <div className="menu-popover recent-history-menu">
          <div className="menu-title">Recent history</div>
          {recentHistory.length ? (
            recentHistory.map((entry) => (
              <Link key={entry.path} className="menu-item" to={entry.path} onClick={() => setOpen(false)}>
                <span>{entry.label}</span>
                <small>{entry.meta}</small>
              </Link>
            ))
          ) : (
            <div className="menu-empty">
              Placeholder history appears here as you move through records.
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
