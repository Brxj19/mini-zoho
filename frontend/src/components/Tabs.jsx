export function Tabs({ items, activeKey, onChange }) {
  return (
    <div className="tabs">
      {items.map((item) => (
        <button
          key={item.key}
          className={`tab-button ${activeKey === item.key ? "is-active" : ""}`}
          type="button"
          onClick={() => onChange(item.key)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
