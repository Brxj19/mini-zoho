import { useEffect, useRef, useState } from "react";

export function useDropdown(initialOpen = false) {
  const [open, setOpen] = useState(initialOpen);
  const ref = useRef(null);

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    function handlePointerDown(event) {
      if (ref.current && !ref.current.contains(event.target)) {
        setOpen(false);
      }
    }

    window.addEventListener("pointerdown", handlePointerDown);
    return () => window.removeEventListener("pointerdown", handlePointerDown);
  }, [open]);

  return {
    open,
    setOpen,
    ref,
    toggle() {
      setOpen((value) => !value);
    },
    close() {
      setOpen(false);
    },
  };
}
