export function Tabs({ items, activeKey, onChange }) {
  return (
    <div className="tabs" role="tablist" aria-label="Section tabs">
      {items.map((item) => (
        <button
          key={item.key}
          className={`tab-button ${activeKey === item.key ? "is-active" : ""}`}
          type="button"
          role="tab"
          aria-selected={activeKey === item.key}
          onClick={() => onChange(item.key)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
