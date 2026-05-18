import { Link } from "react-router-dom";

import { useDropdown } from "../hooks/useDropdown";
import { quickCreateItems } from "../lib/navigation";
import { Icon } from "./Icon";

export function QuickCreateMenu() {
  const { open, ref, toggle, close } = useDropdown();

  return (
    <div className="menu-shell" ref={ref}>
      <button className="quick-create-button" type="button" onClick={toggle}>
        <Icon name="plus" size={16} />
      </button>

      {open ? (
        <div className="menu-popover quick-create-menu is-open">
          <div className="menu-title">Quick Create</div>
          {quickCreateItems.map((item) => (
            <Link key={item.path} className="menu-item menu-item-with-icon" to={item.path} onClick={close}>
              <Icon name={item.icon} size={16} />
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  );
}
