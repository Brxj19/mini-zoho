import { create } from "zustand";
import { persist } from "zustand/middleware";

import api from "../lib/api";

export const useUiStore = create(
  persist(
    (set, get) => ({
      isSidebarCollapsed: false,
      isMobileSidebarOpen: false,
      recentHistory: [],
      notifications: [],
      async fetchNotifications() {
        const { data } = await api.get("/app/notifications/list");
        set({ notifications: data.rows ?? [] });
      },
      toggleSidebar() {
        set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed }));
      },
      openMobileSidebar() {
        set({ isMobileSidebarOpen: true });
      },
      closeMobileSidebar() {
        set({ isMobileSidebarOpen: false });
      },
      addRecentHistory(entry) {
        if (!entry?.path || !entry?.label) {
          return;
        }

        const nextHistory = [
          entry,
          ...get().recentHistory.filter((item) => item.path !== entry.path),
        ].slice(0, 8);

        set({ recentHistory: nextHistory });
      },
      async markNotificationRead(notificationId) {
        await api.post(`/app/notifications/${notificationId}/read`);
        set((state) => ({
          notifications: state.notifications.map((notification) =>
            notification.id === notificationId ? { ...notification, unread: false } : notification,
          ),
        }));
      },
      async markAllNotificationsRead() {
        await api.post("/app/notifications/read-all");
        set((state) => ({
          notifications: state.notifications.map((notification) => ({ ...notification, unread: false })),
        }));
      },
    }),
    {
      name: "northstar-ui-store",
      partialize: (state) => ({
        isSidebarCollapsed: state.isSidebarCollapsed,
        recentHistory: state.recentHistory,
      }),
    },
  ),
);
