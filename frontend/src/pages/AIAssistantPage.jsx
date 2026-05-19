import { useEffect, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import api from "../lib/api";

const reportOptions = [
  { value: "inventory-summary", label: "Inventory Summary" },
  { value: "low-stock", label: "Low Stock" },
  { value: "sales-orders", label: "Sales Orders" },
];

export function AIAssistantPage() {
  const [question, setQuestion] = useState("What should I focus on today for inventory and order operations?");
  const [assistant, setAssistant] = useState({ loading: false, error: "", answer: "", facts: [] });
  const [reorderState, setReorderState] = useState({ loading: true, error: "", items: [] });
  const [integrationState, setIntegrationState] = useState({ loading: true, error: "", items: [] });
  const [reportKey, setReportKey] = useState("inventory-summary");
  const [reportSummary, setReportSummary] = useState({ loading: false, error: "", summary: "" });

  useEffect(() => {
    let active = true;

    Promise.all([api.get("/ai/reorder-suggestions"), api.get("/integrations/catalog")])
      .then(([reorderResponse, integrationsResponse]) => {
        if (!active) return;
        setReorderState({ loading: false, error: "", items: reorderResponse.data.items ?? [] });
        setIntegrationState({ loading: false, error: "", items: integrationsResponse.data.items ?? [] });
      })
      .catch((error) => {
        if (!active) return;
        const message = error?.response?.data?.detail ?? "Unable to load AI workspace data.";
        setReorderState((current) => ({ ...current, loading: false, error: message }));
        setIntegrationState((current) => ({ ...current, loading: false, error: message }));
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleAsk(event) {
    event.preventDefault();
    setAssistant({ loading: true, error: "", answer: "", facts: [] });
    try {
      const response = await api.post("/ai/assistant", { question });
      setAssistant({
        loading: false,
        error: "",
        answer: response.data.answer,
        facts: response.data.facts ?? [],
      });
    } catch (error) {
      setAssistant({
        loading: false,
        error: error?.response?.data?.detail ?? "Unable to generate an assistant response right now.",
        answer: "",
        facts: [],
      });
    }
  }

  async function handleSummarizeReport() {
    setReportSummary({ loading: true, error: "", summary: "" });
    try {
      const response = await api.post("/ai/report-summary", { report_key: reportKey });
      setReportSummary({ loading: false, error: "", summary: response.data.summary });
    } catch (error) {
      setReportSummary({
        loading: false,
        error: error?.response?.data?.detail ?? "Unable to summarize this report yet.",
        summary: "",
      });
    }
  }

  return (
    <div className="view-stack">
      <PageHeader
        eyebrow="AI Workspace"
        title="AI Inventory Assistant"
        description="Tenant-safe insights based only on live database facts, reorder signals, and planned integration surfaces."
      />

      <section className="detail-grid">
        <article className="workspace-card">
          <div className="card-header-row">
            <div>
              <h3>Ask the assistant</h3>
              <p>Responses are generated only from live tenant data. If data is missing, the assistant will say so explicitly.</p>
            </div>
          </div>
          <form className="view-stack" onSubmit={handleAsk}>
            <textarea className="field-input field-textarea" value={question} onChange={(event) => setQuestion(event.target.value)} />
            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={assistant.loading}>
                {assistant.loading ? "Analyzing…" : "Ask Assistant"}
              </button>
            </div>
          </form>
          {assistant.error ? <div className="surface-error">{assistant.error}</div> : null}
          {assistant.answer ? (
            <div className="surface-note">
              <p>{assistant.answer}</p>
              {assistant.facts.length ? (
                <div className="kv-grid">
                  {assistant.facts.map((fact) => (
                    <div className="kv-item" key={fact.label}>
                      <span>{fact.label}</span>
                      <strong>{fact.value}</strong>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </article>

        <article className="workspace-card">
          <div className="card-header-row">
            <div>
              <h3>AI report summary placeholder</h3>
              <p>Summaries use the live report surface but keep the language conservative until a richer GenAI layer is added.</p>
            </div>
          </div>
          <div className="stacked-inline">
            <select className="field-input" value={reportKey} onChange={(event) => setReportKey(event.target.value)}>
              {reportOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <button className="ghost-button" type="button" onClick={handleSummarizeReport} disabled={reportSummary.loading}>
              {reportSummary.loading ? "Summarizing…" : "Summarize"}
            </button>
          </div>
          {reportSummary.error ? <div className="surface-error">{reportSummary.error}</div> : null}
          {reportSummary.summary ? <div className="surface-note">{reportSummary.summary}</div> : null}
        </article>
      </section>

      <section className="workspace-card">
        <div className="card-header-row">
          <div>
            <h3>Smart reorder suggestions</h3>
            <p>Suggestions combine live low-stock positions with the last 30 days of sales deduction activity.</p>
          </div>
        </div>
        {reorderState.loading ? <div className="surface-placeholder">Loading reorder suggestions…</div> : null}
        {reorderState.error ? <div className="surface-error">{reorderState.error}</div> : null}
        {!reorderState.loading && !reorderState.error && !reorderState.items.length ? (
          <EmptyState
            icon="sparkles"
            title="No reorder suggestions right now"
            description="The live stock ledger is currently above reorder thresholds for all tracked warehouse positions."
          />
        ) : null}
        {reorderState.items.length ? (
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Warehouse</th>
                  <th>Available</th>
                  <th>Reorder Level</th>
                  <th>30d Demand</th>
                  <th>Suggested Qty</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {reorderState.items.map((item) => (
                  <tr key={`${item.product_id}-${item.warehouse_id}`}>
                    <td>
                      <strong>{item.product_name}</strong>
                      <div className="table-subtext">{item.sku}</div>
                    </td>
                    <td>{item.warehouse_name}</td>
                    <td>{item.available_quantity}</td>
                    <td>{item.reorder_level}</td>
                    <td>{item.last_30d_demand}</td>
                    <td>{item.recommended_quantity}</td>
                    <td>{item.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>

      <section className="workspace-card">
        <div className="card-header-row">
          <div>
            <h3>Integration roadmap</h3>
            <p>Shipping, payment, and marketplace touchpoints are exposed as tenant-visible placeholders for the next rollout.</p>
          </div>
        </div>
        {integrationState.loading ? <div className="surface-placeholder">Loading integrations…</div> : null}
        {integrationState.error ? <div className="surface-error">{integrationState.error}</div> : null}
        {integrationState.items.length ? (
          <div className="detail-grid">
            {integrationState.items.map((item) => (
              <article className="workspace-card integration-card" key={item.key}>
                <div className="card-header-row">
                  <h3>{item.name}</h3>
                  <span className="status-chip">{item.status}</span>
                </div>
                <p>{item.description}</p>
                <div className="kv-grid">
                  <div className="kv-item">
                    <span>Category</span>
                    <strong>{item.category}</strong>
                  </div>
                  <div className="kv-item">
                    <span>Configured</span>
                    <strong>{item.configured ? "Yes" : "No"}</strong>
                  </div>
                </div>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}
