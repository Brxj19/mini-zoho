import { create } from "zustand";
import { persist } from "zustand/middleware";

import api from "../lib/api";

function applyAuthPayload(set, payload) {
  const organization = payload.organization;
  set({
    token: payload.access_token,
    user: payload.user,
    organizations: organization ? [organization] : [],
    activeOrganizationId: organization?.id ?? null,
    isSetupComplete: !payload.setup_required,
  });
}

export const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      organizations: [],
      activeOrganizationId: null,
      isSetupComplete: false,
      async login(credentials) {
        const { data } = await api.post("/auth/login", credentials);
        applyAuthPayload(set, data);
        return data;
      },
      async register(payload) {
        const { data } = await api.post("/auth/register", {
          company_name: payload.companyName,
          email: payload.email,
          password: payload.password,
          country: payload.country,
          phone: payload.phone,
        });
        applyAuthPayload(set, data);
        return data;
      },
      async completeSetup(payload) {
        const { data } = await api.post("/auth/setup", {
          organization_name: payload.organizationName,
          industry: payload.industry,
          address: payload.address,
          currency: payload.currency,
          timezone: payload.timezone,
        });
        applyAuthPayload(set, data);
        return data;
      },
      async loadProfile() {
        const { data } = await api.get("/auth/me");
        applyAuthPayload(set, data);
        return data;
      },
      switchOrganization(organizationId) {
        set({ activeOrganizationId: organizationId });
      },
      logout() {
        set({
          token: null,
          user: null,
          organizations: [],
          activeOrganizationId: null,
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
    state.organizations.find((organization) => organization.id === state.activeOrganizationId) ?? null,
  );
}
