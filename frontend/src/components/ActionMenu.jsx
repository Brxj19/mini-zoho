import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";

import { Icon } from "./Icon";

export function ActionMenu({ items = [] }) {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const triggerRef = useRef(null);
  const menuRef = useRef(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useLayoutEffect(() => {
    if (!open || !triggerRef.current) {
      return;
    }

    function updatePosition() {
      const rect = triggerRef.current.getBoundingClientRect();
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
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }

    function handlePointerDown(event) {
      const target = event.target;
      if (triggerRef.current?.contains(target) || menuRef.current?.contains(target)) {
        return;
      }
      setOpen(false);
    }

    function handleEscape(event) {
      if (event.key === "Escape") {
        setOpen(false);
      }
    }

    window.addEventListener("pointerdown", handlePointerDown);
    window.addEventListener("keydown", handleEscape);
    return () => {
      window.removeEventListener("pointerdown", handlePointerDown);
      window.removeEventListener("keydown", handleEscape);
    };
  }, [open]);

  return (
    <div className="menu-shell" ref={triggerRef}>
      <button className="icon-button" type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
        <Icon name="more" size={16} />
      </button>

      {open ? (
        createPortal(
          <div
            ref={menuRef}
            className="menu-popover floating-menu is-open"
            style={{ position: "fixed", top: position.top, left: position.left }}
          >
            {items.map((item) =>
              item.to ? (
                <button
                  key={item.label}
                  className="menu-item"
                  type="button"
                  onClick={() => {
                    setOpen(false);
                    navigate(item.to);
                  }}
                >
                  {item.label}
                </button>
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
          </div>,
          document.body,
        )
      ) : null}
    </div>
  );
}
