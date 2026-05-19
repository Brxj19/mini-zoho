import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { EmptyState } from "../components/EmptyState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { Tabs } from "../components/Tabs";
import api from "../lib/api";
import { formatNumber } from "../lib/format";

const tabs = [
  { key: "categories", label: "Categories" },
  { key: "brands", label: "Brands" },
];

function buildCategoryRows(categories, products) {
  return categories.map((category) => {
    const categoryProducts = products.filter((product) => product.category_id === category.id);
    const activeItems = categoryProducts.filter((product) => product.status === "ACTIVE").length;
    const lowStockSignals = categoryProducts.filter((product) => Number(product.reorder_level ?? 0) > 0).length;
    return {
      id: category.id,
      group_name: category.name,
      item_count: categoryProducts.length,
      active_items: activeItems,
      low_stock_signals: lowStockSignals,
      status: category.status,
    };
  });
}

function buildBrandRows(brands, products) {
  return brands.map((brand) => {
    const brandProducts = products.filter((product) => product.brand_id === brand.id);
    return {
      id: brand.id,
      group_name: brand.name,
      item_count: brandProducts.length,
      active_items: brandProducts.filter((product) => product.status === "ACTIVE").length,
      low_stock_signals: brandProducts.filter((product) => Number(product.reorder_level ?? 0) > 0).length,
      status: brand.status,
    };
  });
}

export function ItemGroupsPage() {
  const [activeTab, setActiveTab] = useState("categories");
  const [state, setState] = useState({
    loading: true,
    error: "",
    categories: [],
    brands: [],
    products: [],
  });

  useEffect(() => {
    let active = true;

    async function load() {
      setState({ loading: true, error: "", categories: [], brands: [], products: [] });
      try {
        const [categoriesResponse, brandsResponse, productsResponse] = await Promise.all([
          api.get("/categories", { params: { page_size: 100 } }),
          api.get("/brands", { params: { page_size: 100 } }),
          api.get("/products", { params: { page_size: 100 } }),
        ]);

        if (!active) return;

        setState({
          loading: false,
          error: "",
          categories: categoriesResponse.data.items ?? [],
          brands: brandsResponse.data.items ?? [],
          products: productsResponse.data.items ?? [],
        });
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          error: error?.response?.data?.detail ?? "Unable to load item grouping data.",
          categories: [],
          brands: [],
          products: [],
        });
      }
    }

    load();
    return () => {
      active = false;
    };
  }, []);

  const categoryRows = useMemo(() => buildCategoryRows(state.categories, state.products), [state.categories, state.products]);
  const brandRows = useMemo(() => buildBrandRows(state.brands, state.products), [state.brands, state.products]);
  const currentRows = activeTab === "categories" ? categoryRows : brandRows;
  const uncategorizedItems = useMemo(
    () => state.products.filter((product) => !product.category_id),
    [state.products],
  );

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Inventory"
        title="Item Groups"
        description="Use real categories and brands as grouping surfaces until richer item-group entities are introduced."
        backTo="/items"
      />

      <div className="metric-grid">
        <MetricCard label="Categories" value={formatNumber(state.categories.length)} delta="Catalog grouping buckets" tone="info" />
        <MetricCard label="Brands" value={formatNumber(state.brands.length)} delta="Brand clusters in use" tone="positive" />
        <MetricCard label="Grouped Items" value={formatNumber(state.products.filter((product) => product.category_id || product.brand_id).length)} delta="Catalog already grouped" tone="warning" />
        <MetricCard label="Ungrouped Items" value={formatNumber(uncategorizedItems.length)} delta="Needs structure cleanup" tone="danger" />
      </div>

      <div className="workspace-card">
        <Tabs items={tabs} activeKey={activeTab} onChange={setActiveTab} />
      </div>

      <DataTable
        title={activeTab === "categories" ? "Category Overview" : "Brand Overview"}
        description="These groupings are calculated from the live catalog in your database."
        rows={currentRows}
        columns={[
          { key: "group_name", label: activeTab === "categories" ? "Category" : "Brand" },
          { key: "item_count", label: "Items" },
          { key: "active_items", label: "Active Items" },
          { key: "low_stock_signals", label: "Reorder Signals" },
          { key: "status", label: "Status", kind: "status" },
        ]}
        filters={[{ label: "All Groups", value: "all" }]}
        searchPlaceholder={`Search ${activeTab}`}
        createLabel="+ New Item"
        createTo="/items/new"
        isLoading={state.loading}
        hideHeaderCopy
        emptyState={{
          icon: activeTab === "categories" ? "layers" : "stars",
          title: `No ${activeTab} found`,
          description: "Create more master data or assign items to these structures to make grouping more useful.",
          actionLabel: "Open Items",
          actionTo: "/items",
        }}
      />

      <section className="workspace-card">
        <div className="card-header-row">
          <h3>Ungrouped Items</h3>
        </div>
        {uncategorizedItems.length ? (
          <div className="mini-list">
            {uncategorizedItems.slice(0, 8).map((item) => (
              <div className="mini-list-row" key={item.id}>
                <div>
                  <strong>{item.name}</strong>
                  <span>{item.sku}</span>
                </div>
                <Link className="inline-link" to={`/items/${item.id}`}>
                  Open Item
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon="box"
            title="All sampled items are grouped"
            description="Your visible catalog already has category coverage in this workspace."
            actionLabel="Open Items"
            actionTo="/items"
          />
        )}
      </section>
    </div>
  );
}
