import { Icon } from "./Icon";

export function SearchInput({ value, onChange, placeholder = "Search..." }) {
  return (
    <label className="search-field">
      <Icon name="search" size={16} />
      <input value={value} onChange={onChange} placeholder={placeholder} />
      <span className="search-hint">/</span>
    </label>
  );
}
