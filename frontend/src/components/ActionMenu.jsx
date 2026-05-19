import { useEffect, useLayoutEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Link } from "react-router-dom";

import { useDropdown } from "../hooks/useDropdown";
import { Icon } from "./Icon";

export function ActionMenu({ items = [] }) {
  const { open, ref, toggle, close } = useDropdown();
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useLayoutEffect(() => {
    if (!open || !ref.current) {
      return;
    }

    function updatePosition() {
      const rect = ref.current.getBoundingClientRect();
      setPosition({
        top: rect.bottom + 8,
        left: Math.max(12, rect.right - 220),
      });
    }

    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);
    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [open, ref]);

  useEffect(() => {
    if (!open) {
      return;
    }

    function handleEscape(event) {
      if (event.key === "Escape") {
        close();
      }
    }

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [close, open]);

  return (
    <div className="menu-shell" ref={ref}>
      <button className="icon-button" type="button" onClick={toggle} aria-expanded={open}>
        <Icon name="more" size={16} />
      </button>

      {open ? (
        createPortal(
          <div className="menu-popover floating-menu is-open" style={{ position: "fixed", top: position.top, left: position.left }}>
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
          </div>,
          document.body,
        )
      ) : null}
    </div>
  );
}
