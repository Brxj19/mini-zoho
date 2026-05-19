import { Link } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { useDropdown } from "../hooks/useDropdown";
import { getQuickCreateItems } from "../lib/navigation";
import { Icon } from "./Icon";

export function QuickCreateMenu() {
  const { user } = useAuth();
  const { open, ref, toggle, close } = useDropdown();
  const visibleItems = getQuickCreateItems(user?.role);

  if (!visibleItems.length) {
    return null;
  }

  return (
    <div className="menu-shell" ref={ref}>
      <button className="quick-create-button" type="button" onClick={toggle} aria-label="Open quick create menu">
        <Icon name="plus" size={16} />
      </button>

      {open ? (
        <div className="menu-popover quick-create-menu is-open">
          <div className="menu-row">
            <div>
              <div className="menu-title">Quick Create</div>
              <div className="menu-caption">Jump into common workflows</div>
            </div>
          </div>
          {visibleItems.map((item) => (
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
