import { useState } from "react";
import { Link } from "react-router-dom";

import { Icon } from "./Icon";

export function ActionMenu({ items = [] }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="menu-shell">
      <button
        className="icon-button"
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
      >
        <Icon name="more" size={16} />
      </button>

      {open ? (
        <div className="menu-popover">
          {items.map((item) =>
            item.to ? (
              <Link key={item.label} className="menu-item" to={item.to} onClick={() => setOpen(false)}>
                {item.label}
              </Link>
            ) : (
              <button
                key={item.label}
                className={`menu-item ${item.destructive ? "is-danger" : ""}`}
                type="button"
                onClick={() => {
                  item.onClick?.();
                  setOpen(false);
                }}
              >
                {item.label}
              </button>
            ),
          )}
        </div>
      ) : null}
    </div>
  );
}
