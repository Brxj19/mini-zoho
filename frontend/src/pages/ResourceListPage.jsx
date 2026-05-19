import { useEffect, useState } from "react";

import { DataTable } from "../components/DataTable";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";
import { normalizeItems } from "../lib/format";
import { resourceConfigs } from "../lib/uiConfig";

export function ResourceListPage({ resourceKey }) {
  const config = resourceConfigs[resourceKey];
  const { user } = useAuth();
  const [state, setState] = useState({
    loading: true,
    error: "",
    items: [],
  });
  const canCreate = !config.createRoles || config.createRoles.includes(user?.role);

  useEffect(() => {
    let active = true;

    async function loadRows() {
      setState((current) => ({ ...current, loading: true, error: "" }));
      try {
        const response = await api.get(config.endpoint, { params: { page_size: 100 } });
        if (!active) {
          return;
        }
        setState({
          loading: false,
          error: "",
          items: normalizeItems(response.data),
        });
      } catch (error) {
        if (!active) {
          return;
        }
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load this workspace view.",
          items: [],
        });
      }
    }

    loadRows();
    return () => {
      active = false;
    };
  }, [config.endpoint]);

  return (
    <div className="page-stack">
      {state.error ? <div className="form-error">{state.error}</div> : null}
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
