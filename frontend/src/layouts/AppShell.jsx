import { useEffect } from "react";
import { Outlet, useLocation, useMatches } from "react-router-dom";

import { Breadcrumbs } from "../components/Breadcrumbs";
import { Drawer } from "../components/Drawer";
import { Sidebar } from "../components/Sidebar";
import { Topbar } from "../components/Topbar";
import { useAuthStore } from "../stores/authStore";
import { useUiStore } from "../stores/uiStore";

export function AppShell() {
  const location = useLocation();
  const matches = useMatches();
  const addRecentHistory = useUiStore((state) => state.addRecentHistory);
  const isMobileSidebarOpen = useUiStore((state) => state.isMobileSidebarOpen);
  const closeMobileSidebar = useUiStore((state) => state.closeMobileSidebar);
  const loadProfile = useAuthStore((state) => state.loadProfile);

  useEffect(() => {
    const currentMatch = [...matches].reverse().find((match) => match.handle?.title);

    if (!currentMatch?.handle?.title) {
      return;
    }

    addRecentHistory({
      path: location.pathname,
      label:
        typeof currentMatch.handle.title === "function"
          ? currentMatch.handle.title(currentMatch.params)
          : currentMatch.handle.title,
      meta: typeof currentMatch.handle.section === "string" ? currentMatch.handle.section : "Page",
    });
  }, [addRecentHistory, location.pathname, matches]);

  useEffect(() => {
    loadProfile().catch(() => undefined);
  }, [loadProfile]);

  return (
    <div className="app-shell">
      <Sidebar />
      <Drawer open={isMobileSidebarOpen} onClose={closeMobileSidebar}>
        <Sidebar mobile />
      </Drawer>

      <div className="shell-main">
        <Topbar />
        <div className="shell-content">
          <div className="content-backdrop" />
          <div className="content-inner">
            <Breadcrumbs />
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  );
}
