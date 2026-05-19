import { forwardRef } from "react";

import { Icon } from "./Icon";

export const SearchInput = forwardRef(function SearchInput(
  { value, onChange, placeholder = "Search...", variant = "table", showShortcut = false, onFocus, onBlur, onKeyDown },
  ref,
) {
  return (
    <label className={`search-field search-field-${variant}`}>
      <Icon name="search" size={16} />
      <input
        ref={ref}
        value={value}
        onChange={onChange}
        onFocus={onFocus}
        onBlur={onBlur}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
      />
      {showShortcut ? <span className="search-hint">/</span> : null}
    </label>
  );
});
