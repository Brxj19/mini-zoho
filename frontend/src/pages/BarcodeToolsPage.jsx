import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import api from "../lib/api";

export function BarcodeToolsPage() {
  const [barcode, setBarcode] = useState("");
  const [result, setResult] = useState(null);
  const [batches, setBatches] = useState([]);
  const [serials, setSerials] = useState([]);
  const [state, setState] = useState({ loading: true, searching: false, error: "" });

  useEffect(() => {
    let active = true;
    Promise.all([
      api.get("/inventory/batches", { params: { page_size: 10 } }),
      api.get("/inventory/serials", { params: { page_size: 10 } }),
    ])
      .then(([batchesResponse, serialsResponse]) => {
        if (!active) return;
        setBatches(batchesResponse.data.items ?? []);
        setSerials(serialsResponse.data.items ?? []);
        setState({ loading: false, searching: false, error: "" });
      })
      .catch((error) => {
        if (!active) return;
        setState({
          loading: false,
          searching: false,
          error: error?.response?.data?.detail ?? "Unable to load barcode tools.",
        });
      });
    return () => {
      active = false;
    };
  }, []);

  async function generateBarcode() {
    try {
      const response = await api.get("/inventory/barcode/generate");
      setBarcode(response.data.barcode);
      setState((current) => ({ ...current, error: "" }));
    } catch (error) {
      setState((current) => ({
        ...current,
        error: error?.response?.data?.detail ?? "Unable to generate a barcode.",
      }));
    }
  }

  async function searchBarcode(event) {
    event.preventDefault();
    setState((current) => ({ ...current, searching: true, error: "" }));
    try {
      const response = await api.get("/inventory/barcode-search", { params: { barcode } });
      setResult(response.data);
      setState((current) => ({ ...current, searching: false }));
    } catch (error) {
      setResult(null);
      setState((current) => ({
        ...current,
        searching: false,
        error: error?.response?.data?.detail ?? "Unable to search by barcode.",
      }));
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Advanced Inventory"
        title="Barcode And Tracking Tools"
        description="Generate barcodes, search products instantly, and inspect the latest tracked batches and serials."
        backTo="/items"
      />

      {state.error ? <div className="surface-error">{state.error}</div> : null}

      <div className="detail-grid">
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Barcode Search</h3>
            <button className="ghost-button" type="button" onClick={generateBarcode}>
              Generate Barcode
            </button>
          </div>
          <form className="form-shell" onSubmit={searchBarcode}>
            <label>
              Barcode
              <input className="field-input" value={barcode} onChange={(event) => setBarcode(event.target.value)} placeholder="Scan or paste barcode" />
            </label>
            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={state.searching || !barcode}>
                {state.searching ? "Searching…" : "Search Product"}
              </button>
            </div>
          </form>

          {result ? (
            <div className="kv-grid">
              <div className="kv-item">
                <span>Item</span>
                <strong>{result.name}</strong>
              </div>
              <div className="kv-item">
                <span>SKU</span>
                <strong>{result.sku}</strong>
              </div>
              <div className="kv-item">
                <span>Barcode</span>
                <strong>{result.barcode}</strong>
              </div>
              <div className="kv-item">
                <span>Open</span>
                <strong><Link className="inline-link" to={`/items/${result.product_id}`}>View item detail</Link></strong>
              </div>
            </div>
          ) : null}
        </section>

        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Tracking Snapshot</h3>
          </div>
          {state.loading ? (
            <div className="surface-placeholder">Loading tracked inventory…</div>
          ) : (
            <div className="usage-stack">
              <div className="kv-item">
                <span>Recent batches</span>
                <strong>{batches.length}</strong>
              </div>
              <div className="kv-item">
                <span>Recent serials</span>
                <strong>{serials.length}</strong>
              </div>
              {!batches.length && !serials.length ? (
                <EmptyState
                  icon="package"
                  title="No tracked inventory recorded yet"
                  description="Enable serial or batch tracking on an item, then receive stock through Stock In to populate these ledgers."
                  actionLabel="Record Stock In"
                  actionTo="/inventory/stock-in"
                />
              ) : null}
            </div>
          )}
        </section>
      </div>

      {!state.loading && batches.length ? (
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Recent Batches</h3>
          </div>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Batch</th>
                  <th>Product ID</th>
                  <th>Warehouse ID</th>
                  <th>Available</th>
                  <th>Expiry</th>
                </tr>
              </thead>
              <tbody>
                {batches.map((item) => (
                  <tr key={item.id}>
                    <td>{item.batch_number}</td>
                    <td>{item.product_id}</td>
                    <td>{item.warehouse_id}</td>
                    <td>{item.available_quantity}</td>
                    <td>{item.expiry_date ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {!state.loading && serials.length ? (
        <section className="workspace-card">
          <div className="card-header-row">
            <h3>Recent Serials</h3>
          </div>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Serial</th>
                  <th>Product ID</th>
                  <th>Warehouse ID</th>
                  <th>Status</th>
                  <th>Warranty</th>
                </tr>
              </thead>
              <tbody>
                {serials.map((item) => (
                  <tr key={item.id}>
                    <td>{item.serial_number}</td>
                    <td>{item.product_id}</td>
                    <td>{item.warehouse_id}</td>
                    <td>{item.status}</td>
                    <td>{item.warranty_until ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </div>
  );
}
