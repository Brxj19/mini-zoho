import { Link } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { useDropdown } from "../hooks/useDropdown";
import { quickCreateItems } from "../lib/navigation";
import { hasAnyRole } from "../lib/permissions";
import { Icon } from "./Icon";

export function QuickCreateMenu() {
  const { user } = useAuth();
  const { open, ref, toggle, close } = useDropdown();
  const visibleItems = quickCreateItems.filter((item) => hasAnyRole(user, item.roles));

  if (!visibleItems.length) {
    return null;
  }

  return (
    <div className="menu-shell" ref={ref}>
      <button className="quick-create-button" type="button" onClick={toggle}>
        <Icon name="plus" size={16} />
      </button>

      {open ? (
        <div className="menu-popover quick-create-menu is-open">
          <div className="menu-title">Quick Create</div>
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
