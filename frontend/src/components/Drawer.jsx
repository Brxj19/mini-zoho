export function Drawer({ open, onClose, children }) {
  return (
    <div className={`drawer ${open ? "is-open" : ""}`} aria-hidden={!open}>
      <button className="drawer-backdrop" type="button" aria-label="Close navigation" onClick={onClose} />
      <div className="drawer-panel">{children}</div>
    </div>
  );
}
