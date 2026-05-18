import { Link } from "react-router-dom";

import { useDropdown } from "../hooks/useDropdown";
import { Icon } from "./Icon";

export function ActionMenu({ items = [] }) {
  const { open, ref, toggle, close } = useDropdown();

  return (
    <div className="menu-shell" ref={ref}>
      <button className="icon-button" type="button" onClick={toggle} aria-expanded={open}>
        <Icon name="more" size={16} />
      </button>

      {open ? (
        <div className="menu-popover is-open">
          {items.map((item) =>
            item.to ? (
              <Link key={item.label} className="menu-item" to={item.to} onClick={close}>
                {item.label}
              </Link>
            ) : (
              <button
                key={item.label}
                className={`menu-item ${item.destructive ? "is-danger" : ""}`}
                type="button"
                onClick={() => {
                  item.onClick?.();
                  close();
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
