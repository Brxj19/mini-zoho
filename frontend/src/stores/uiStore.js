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
        const { data } = await api.get("/notifications", { params: { page_size: 8 } });
        set({
          notifications: (data.items ?? []).map((item) => ({
            id: item.id,
            title: item.title,
            detail: item.message,
            unread: !item.is_read,
            createdAt: item.created_at,
            type: item.type,
          })),
        });
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
        await api.post(`/notifications/${notificationId}/read`);
        set((state) => ({
          notifications: state.notifications.map((notification) =>
            notification.id === notificationId ? { ...notification, unread: false } : notification,
          ),
        }));
      },
      async markAllNotificationsRead() {
        await api.post("/notifications/read-all");
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
