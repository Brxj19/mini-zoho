import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { useDropdown } from "../hooks/useDropdown";
import api from "../lib/api";
import { getNavigationGroups } from "../lib/navigation";
import { useUiStore } from "../stores/uiStore";
import { Icon } from "./Icon";
import { NotificationDropdown } from "./NotificationDropdown";
import { OrganizationSwitcher } from "./OrganizationSwitcher";
import { QuickCreateMenu } from "./QuickCreateMenu";
import { RecentHistoryMenu } from "./RecentHistoryMenu";
import { SearchInput } from "./SearchInput";
import { UserMenu } from "./UserMenu";

export function Topbar() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [searchState, setSearchState] = useState({ open: false, loading: false, results: [], error: "" });
  const searchInputRef = useRef(null);
  const searchShellRef = useRef(null);
  const helpDropdown = useDropdown();
  const { user, tenant } = useAuth();
  const fetchNotifications = useUiStore((state) => state.fetchNotifications);
  const openMobileSidebar = useUiStore((state) => state.openMobileSidebar);
  const navigationGroups = useMemo(() => getNavigationGroups(user?.role), [user?.role]);

  useEffect(() => {
    fetchNotifications().catch(() => undefined);
  }, [fetchNotifications]);

  useEffect(() => {
    if (!searchState.open) {
      return undefined;
    }

    function handlePointerDown(event) {
      if (searchShellRef.current?.contains(event.target)) {
        return;
      }
      setSearchState((current) => ({ ...current, open: false }));
    }

    window.addEventListener("pointerdown", handlePointerDown);
    return () => window.removeEventListener("pointerdown", handlePointerDown);
  }, [searchState.open]);

  useEffect(() => {
    function handleSlashFocus(event) {
      const activeElement = document.activeElement;
      const tagName = activeElement?.tagName;
      const isTypingContext =
        tagName === "INPUT" ||
        tagName === "TEXTAREA" ||
        tagName === "SELECT" ||
        activeElement?.isContentEditable;

      if (event.key === "/" && !event.metaKey && !event.ctrlKey && !event.altKey && !isTypingContext) {
        event.preventDefault();
        searchInputRef.current?.focus();
        setSearchState((current) => ({ ...current, open: true }));
      }
    }

    window.addEventListener("keydown", handleSlashFocus);
    return () => window.removeEventListener("keydown", handleSlashFocus);
  }, []);

  useEffect(() => {
    if (query.trim().length < 2) {
      setSearchState((current) => ({ ...current, loading: false, results: [], error: "" }));
      return;
    }

    const timer = window.setTimeout(async () => {
      setSearchState((current) => ({ ...current, open: true, loading: true, error: "" }));

      const resources =
        user?.role === "SUPER_ADMIN"
          ? [
              { key: "tenants", label: "Tenant", endpoint: "/tenants", buildPath: (item) => `/tenants/${item.id}`, buildMeta: () => "Platform" },
              { key: "users", label: "User", endpoint: "/users", buildPath: (item) => `/users/${item.id}`, buildMeta: (item) => item.role?.replaceAll("_", " ") ?? "User" },
              { key: "plans", label: "Plan", endpoint: "/subscription-plans", buildPath: () => "/subscription", buildMeta: () => "Subscription" },
            ]
          : [
              { key: "products", label: "Item", endpoint: "/products", buildPath: (item) => `/items/${item.id}`, buildMeta: (item) => item.sku ?? "Inventory" },
              { key: "customers", label: "Customer", endpoint: "/customers", buildPath: (item) => `/customers/${item.id}`, buildMeta: (item) => item.email ?? "Sales" },
              { key: "vendors", label: "Vendor", endpoint: "/vendors", buildPath: (item) => `/vendors/${item.id}`, buildMeta: (item) => item.email ?? "Purchases" },
              { key: "warehouses", label: "Warehouse", endpoint: "/warehouses", buildPath: (item) => `/warehouses/${item.id}`, buildMeta: (item) => item.code ?? "Inventory" },
              { key: "salesOrders", label: "Sales Order", endpoint: "/sales-orders", buildPath: (item) => `/sales-orders/${item.id}`, buildMeta: (item) => item.so_number ?? item.status ?? "Sales" },
              { key: "purchaseOrders", label: "Purchase Order", endpoint: "/purchase-orders", buildPath: (item) => `/purchase-orders/${item.id}`, buildMeta: (item) => item.po_number ?? item.status ?? "Purchases" },
              { key: "stockTransfers", label: "Stock Transfer", endpoint: "/inventory/transfers", buildPath: (item) => `/inventory/transfers/${item.id}`, buildMeta: (item) => item.status ?? "Inventory" },
            ];

      try {
        const responses = await Promise.all(
          resources.map((resource) =>
            api
              .get(resource.endpoint, { params: { search: query.trim(), page_size: 5 } })
              .then((response) => ({ resource, items: response.data.items ?? [] }))
              .catch(() => ({ resource, items: [] })),
          ),
        );

        const nextResults = responses
          .flatMap(({ resource, items }) =>
            items.map((item) => ({
              id: `${resource.key}-${item.id}`,
              label:
                item.name ??
                item.company_name ??
                item.so_number ??
                item.po_number ??
                item.code ??
                item.email ??
                `Record #${item.id}`,
              kind: resource.label,
              meta: resource.buildMeta(item),
              path: resource.buildPath(item),
            })),
          )
          .slice(0, 12);

        setSearchState({ open: true, loading: false, results: nextResults, error: "" });
      } catch {
        setSearchState({ open: true, loading: false, results: [], error: "Unable to search right now." });
      }
    }, 220);

    return () => window.clearTimeout(timer);
  }, [query, user?.role]);

  const quickLinks = useMemo(
    () =>
      navigationGroups
        .flatMap((group) => group.items.map((item) => ({ id: item.path, label: item.label, kind: group.title, meta: "Navigation", path: item.path })))
        .filter((item) => item.label.toLowerCase().includes(query.trim().toLowerCase()))
        .slice(0, 5),
    [navigationGroups, query],
  );

  const mergedResults = searchState.results.length ? searchState.results : query.trim().length >= 2 ? quickLinks : [];

  function openResult(path) {
    setSearchState((current) => ({ ...current, open: false }));
    setQuery("");
    navigate(path);
  }

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="icon-button mobile-only" type="button" onClick={openMobileSidebar}>
          <Icon name="menu" size={18} />
        </button>
        <button className="topbar-brand-lockup" type="button" onClick={() => navigate("/dashboard")}>
          <span className="brand-symbol topbar-brand-symbol">N</span>
          <span className="topbar-brand-copy">
            <strong>Northstar Inventory</strong>
            <small>{user?.role === "SUPER_ADMIN" ? "Platform console" : tenant?.company_name ?? "Workspace"}</small>
          </span>
        </button>
      </div>

      <div className="topbar-search">
        <div className="topbar-search-shell" ref={searchShellRef}>
          <SearchInput
            ref={searchInputRef}
            variant="topbar"
            showShortcut
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setSearchState((current) => ({ ...current, open: true }));
            }}
            onFocus={() => setSearchState((current) => ({ ...current, open: true }))}
            onKeyDown={(event) => {
              if (event.key === "Enter" && mergedResults[0]) {
                event.preventDefault();
                openResult(mergedResults[0].path);
              }
              if (event.key === "Escape") {
                setSearchState((current) => ({ ...current, open: false }));
              }
            }}
            placeholder="Search items, orders, customers, vendors, warehouses..."
          />
          {searchState.open ? (
            <div className="menu-popover topbar-search-popover is-open">
              <div className="menu-row">
                <div>
                  <div className="menu-title">Global search</div>
                  <div className="menu-caption">Use real workspace results or jump to app sections</div>
                </div>
              </div>
              {searchState.loading ? <div className="menu-empty">Searching…</div> : null}
              {!searchState.loading && searchState.error ? <div className="menu-empty">{searchState.error}</div> : null}
              {!searchState.loading && !searchState.error && query.trim().length < 2 ? (
                <div className="menu-empty">Type at least 2 characters. Press <strong>/</strong> anytime to focus search.</div>
              ) : null}
              {!searchState.loading && !searchState.error && query.trim().length >= 2 && mergedResults.length === 0 ? (
                <div className="menu-empty">No matching items, orders, vendors, customers, or sections were found.</div>
              ) : null}
              {!searchState.loading && !searchState.error && mergedResults.length ? (
                <div className="menu-scroll">
                  {mergedResults.map((item) => (
                    <button key={item.id} className="menu-item search-result-item" type="button" onClick={() => openResult(item.path)}>
                      <span>{item.label}</span>
                      <small>
                        {item.kind} • {item.meta}
                      </small>
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>

      <div className="topbar-actions">
        <QuickCreateMenu />
        <RecentHistoryMenu />
        <NotificationDropdown />

        <div className="menu-shell" ref={helpDropdown.ref}>
          <button className="icon-button topbar-icon-button" type="button" onClick={helpDropdown.toggle}>
            <Icon name="help" size={16} />
          </button>
          {helpDropdown.open ? (
            <div className="menu-popover is-open">
              <div className="menu-row">
                <div>
                  <div className="menu-title">Help & support</div>
                  <div className="menu-caption">Guides, contact points, and onboarding</div>
                </div>
              </div>
              <div className="menu-empty">Support, setup guides, and product-tour actions will live here in the redesigned shell.</div>
            </div>
          ) : null}
        </div>

        <OrganizationSwitcher />
        <UserMenu />
      </div>
    </header>
  );
}
