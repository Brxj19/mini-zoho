import { useEffect, useState } from "react";

import { ConfirmDialog } from "../components/ConfirmDialog";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import api from "../lib/api";
import { formatDateTime } from "../lib/format";

export function NotificationsPage() {
  const [state, setState] = useState({ loading: true, error: "", items: [], unread: 0, confirming: false });

  async function load() {
    setState((current) => ({ ...current, loading: true, error: "" }));
    try {
      const response = await api.get("/notifications", { params: { page_size: 50 } });
      setState((current) => ({
        ...current,
        loading: false,
        error: "",
        items: response.data.items ?? [],
        unread: response.data.unread_count ?? 0,
      }));
    } catch (error) {
      setState((current) => ({
        ...current,
        loading: false,
        error: error?.response?.data?.detail ?? "Unable to load notifications.",
      }));
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function markRead(notificationId) {
    await api.post(`/notifications/${notificationId}/read`);
    load();
  }

  async function markAllRead() {
    await api.post("/notifications/read-all");
    setState((current) => ({ ...current, confirming: false }));
    load();
  }

  return (
    <div className="view-stack">
      <PageHeader
        eyebrow="Inbox"
        title="Workspace Notifications"
        description="Stay on top of low stock, receiving events, and order-status movement."
        backTo="/"
        actions={
          <button className="ghost-button" type="button" onClick={() => setState((current) => ({ ...current, confirming: true }))}>
            Mark All Read
          </button>
        }
      />

      <section className="workspace-card">
        <div className="card-header-row">
          <h3>Unread {state.unread}</h3>
        </div>
        {state.loading ? <LoadingState animationKey="appLoading" message="Loading notifications…" compact /> : null}
        {state.error ? (
          <ErrorState
            animationKey="emptyData"
            title="Unable to load notifications"
            description={state.error}
            onRetry={load}
          />
        ) : null}
        {!state.loading && !state.error && state.items.length === 0 ? (
          <EmptyState
            animationKey="emptyData"
            title="No notifications yet"
            description="Your workspace feed will show operational alerts here."
            compact
          />
        ) : null}
        {!state.loading && !state.error && state.items.length > 0 ? (
          <div className="notification-list">
            {state.items.map((item) => (
              <article className={`notification-card ${item.is_read ? "notification-card-read" : ""}`} key={item.id}>
                <div className="notification-copy">
                  <div className="notification-row">
                    <strong>{item.title}</strong>
                    <StatusBadge value={item.type} />
                  </div>
                  <p>{item.message}</p>
                  <span>{formatDateTime(item.created_at)}</span>
                </div>
                {!item.is_read ? (
                  <button className="ghost-button" type="button" onClick={() => markRead(item.id)}>
                    Mark Read
                  </button>
                ) : null}
              </article>
            ))}
          </div>
        ) : null}
      </section>

      <ConfirmDialog
        open={state.confirming}
        title="Mark all notifications as read?"
        description="This clears the unread count in your workspace feed."
        confirmLabel="Mark All Read"
        onCancel={() => setState((current) => ({ ...current, confirming: false }))}
        onConfirm={markAllRead}
      />
    </div>
  );
}
