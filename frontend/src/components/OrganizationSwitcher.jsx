import { useState } from "react";

import { useActiveOrganization, useAuthStore } from "../stores/authStore";
import { Icon } from "./Icon";

export function OrganizationSwitcher() {
  const [open, setOpen] = useState(false);
  const organizations = useAuthStore((state) => state.organizations);
  const switchOrganization = useAuthStore((state) => state.switchOrganization);
  const activeOrganization = useActiveOrganization();

  return (
    <div className="menu-shell">
      <button className="utility-button with-text" type="button" onClick={() => setOpen((value) => !value)}>
        <span>{activeOrganization?.name ?? "Organization"}</span>
        <Icon name="chevronDown" size={14} />
      </button>

      {open ? (
        <div className="menu-popover">
          {organizations.map((organization) => (
            <button
              key={organization.id}
              className="menu-item"
              type="button"
              onClick={() => {
                switchOrganization(organization.id);
                setOpen(false);
              }}
            >
              <span>{organization.name}</span>
              <small>{organization.plan}</small>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
