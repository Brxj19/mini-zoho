import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useUiStore = create(
  persist(
    (set, get) => ({
      isSidebarCollapsed: false,
      isMobileSidebarOpen: false,
      recentHistory: [],
      notifications: [
        {
          id: "notif-1",
          title: "Low-stock review pending",
          detail: "Three items are below reorder level in Central Warehouse.",
          time: "10m ago",
          unread: true,
        },
        {
          id: "notif-2",
          title: "Purchase order requires receiving",
          detail: "PO-204 has arrived and is ready for receive workflow.",
          time: "1h ago",
          unread: true,
        },
        {
          id: "notif-3",
          title: "Weekly report export is ready",
          detail: "Inventory movement export completed successfully.",
          time: "Today",
          unread: false,
        },
      ],
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
      markNotificationRead(notificationId) {
        set((state) => ({
          notifications: state.notifications.map((notification) =>
            notification.id === notificationId ? { ...notification, unread: false } : notification,
          ),
        }));
      },
      markAllNotificationsRead() {
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
        notifications: state.notifications,
      }),
    },
  ),
);
