import { useState } from "react";
import { Link } from "react-router-dom";

import { quickCreateItems } from "../lib/navigation";
import { Icon } from "./Icon";

export function QuickCreateMenu() {
  const [open, setOpen] = useState(false);

  return (
    <div className="menu-shell">
      <button className="quick-create-button" type="button" onClick={() => setOpen((value) => !value)}>
        <Icon name="plus" size={16} />
      </button>

      {open ? (
        <div className="menu-popover quick-create-menu">
          <div className="menu-title">Quick Create</div>
          {quickCreateItems.map((item) => (
            <Link key={item.path} className="menu-item menu-item-with-icon" to={item.path} onClick={() => setOpen(false)}>
              <Icon name={item.icon} size={16} />
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  );
}
