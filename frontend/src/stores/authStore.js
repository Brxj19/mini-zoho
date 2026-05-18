import { create } from "zustand";
import { persist } from "zustand/middleware";

const DEFAULT_ORGANIZATIONS = [
  { id: "org-northstar", name: "Northstar Retail", plan: "Growth" },
  { id: "org-riverline", name: "Riverline Home", plan: "Starter" },
];

const DEFAULT_USER = {
  id: "user-super-admin",
  name: "Brajesh Kumar",
  email: "superadmin@example.com",
  role: "SUPER_ADMIN",
};

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      organizations: DEFAULT_ORGANIZATIONS,
      activeOrganizationId: DEFAULT_ORGANIZATIONS[0].id,
      isSetupComplete: false,
      login(email) {
        const user =
          email === "superadmin@example.com"
            ? DEFAULT_USER
            : {
                id: "user-tenant-admin",
                name: email.split("@")[0].replace(/[._-]/g, " "),
                email,
                role: "TENANT_ADMIN",
              };

        set({
          token: `northstar-token:${email}`,
          user,
          activeOrganizationId: DEFAULT_ORGANIZATIONS[0].id,
        });
      },
      register(payload) {
        const organization = {
          id: `org-${payload.companyName.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`,
          name: payload.companyName,
          plan: "Starter",
        };

        set({
          token: `northstar-token:${payload.email}`,
          user: {
            id: "user-tenant-admin",
            name: payload.companyName,
            email: payload.email,
            role: "TENANT_ADMIN",
          },
          organizations: [organization, ...DEFAULT_ORGANIZATIONS],
          activeOrganizationId: organization.id,
          isSetupComplete: false,
        });
      },
      completeSetup(payload) {
        const { organizations, activeOrganizationId } = get();
        set({
          organizations: organizations.map((organization) =>
            organization.id === activeOrganizationId
              ? {
                  ...organization,
                  name: payload.organizationName,
                  industry: payload.industry,
                  currency: payload.currency,
                  timezone: payload.timezone,
                }
              : organization,
          ),
          isSetupComplete: true,
        });
      },
      switchOrganization(organizationId) {
        set({ activeOrganizationId: organizationId });
      },
      logout() {
        set({
          token: null,
          user: null,
          activeOrganizationId: DEFAULT_ORGANIZATIONS[0].id,
          isSetupComplete: false,
        });
      },
    }),
    {
      name: "northstar-auth-store",
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        organizations: state.organizations,
        activeOrganizationId: state.activeOrganizationId,
        isSetupComplete: state.isSetupComplete,
      }),
    },
  ),
);

export function useActiveOrganization() {
  return useAuthStore((state) =>
    state.organizations.find((organization) => organization.id === state.activeOrganizationId),
  );
}
