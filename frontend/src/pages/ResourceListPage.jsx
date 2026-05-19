import { useEffect, useState } from "react";

import { DataTable } from "../components/DataTable";
import { PageHeader } from "../components/PageHeader";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";
import { normalizeItems } from "../lib/format";
import { hasAnyRole } from "../lib/permissions";
import { resourceConfigs } from "../lib/uiConfig";

export function ResourceListPage({ resourceKey }) {
  const config = resourceConfigs[resourceKey];
  const { user } = useAuth();
  const [state, setState] = useState({
    loading: true,
    error: "",
    items: [],
    meta: { page: 1, page_size: 12, total: 0 },
  });
  const canCreate = hasAnyRole(user, config.createRoles);
  const [query, setQuery] = useState("");
  const [filterValue, setFilterValue] = useState(config.filters?.[0]?.value ?? "all");
  const [sortValue, setSortValue] = useState(config.columns?.[0]?.key ?? "");
  const [page, setPage] = useState(1);

  useEffect(() => {
    let active = true;

    async function loadRows() {
      setState((current) => ({ ...current, loading: true, error: "" }));
      try {
        const params = {
          page,
          page_size: state.meta.page_size,
        };
        if (config.searchParam && query.trim()) {
          params[config.searchParam] = query.trim();
        }
        if (config.filterParam && filterValue && filterValue !== "all") {
          params[config.filterParam] = filterValue;
        }
        const response = await api.get(config.endpoint, { params });
        if (!active) {
          return;
        }
        setState({
          loading: false,
          error: "",
          items: normalizeItems(response.data),
          meta: response.data.meta ?? state.meta,
        });
      } catch (error) {
        if (!active) {
          return;
        }
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load this workspace view.",
          items: [],
          meta: { ...state.meta, total: 0 },
        });
      }
    }

    loadRows();
    return () => {
      active = false;
    };
  }, [config.endpoint, config.filterParam, config.searchParam, filterValue, page, query, state.meta.page_size]);

  return (
    <div className="page-stack">
      {state.error ? <div className="form-error">{state.error}</div> : null}
      <PageHeader eyebrow={config.eyebrow ?? "Workspace"} title={config.title} description={config.description} backTo="/" />
      <DataTable
        title={config.title}
        description={config.description}
        rows={state.items}
        columns={config.columns}
        filters={config.filters}
        createLabel={canCreate ? config.createLabel : undefined}
        createTo={canCreate ? config.createPath : undefined}
        searchPlaceholder={config.searchPlaceholder}
        rowLink={config.detailPath}
        isLoading={state.loading}
        query={query}
        onQueryChange={setQuery}
        filterValue={filterValue}
        onFilterChange={(value) => {
          setFilterValue(value);
          setPage(1);
        }}
        sortValue={sortValue}
        onSortChange={setSortValue}
        page={page}
        onPageChange={setPage}
        totalCount={state.meta.total}
        pageSize={state.meta.page_size}
        serverSide
        hideHeaderCopy
        emptyState={{
          icon: "box",
          title: `No ${config.title.toLowerCase()} yet`,
          description: "This screen is live and ready. Add records or broaden your filters to populate the view.",
          actionLabel: canCreate && config.createPath ? config.createLabel : undefined,
          actionTo: canCreate ? config.createPath : undefined,
        }}
      />
    </div>
  );
}
