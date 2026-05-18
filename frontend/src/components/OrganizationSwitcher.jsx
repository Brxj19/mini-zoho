import { useDropdown } from "../hooks/useDropdown";
import { useActiveOrganization, useAuthStore } from "../stores/authStore";
import { Icon } from "./Icon";

export function OrganizationSwitcher() {
  const { open, ref, toggle, close } = useDropdown();
  const organizations = useAuthStore((state) => state.organizations);
  const switchOrganization = useAuthStore((state) => state.switchOrganization);
  const activeOrganization = useActiveOrganization();

  return (
    <div className="menu-shell" ref={ref}>
      <button className="utility-button with-text" type="button" onClick={toggle}>
        <span>{activeOrganization?.name ?? "Organization"}</span>
        <Icon name="chevronDown" size={14} />
      </button>

      {open ? (
        <div className="menu-popover is-open">
          {organizations.map((organization) => (
            <button
              key={organization.id}
              className="menu-item"
              type="button"
              onClick={() => {
                switchOrganization(organization.id);
                close();
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
