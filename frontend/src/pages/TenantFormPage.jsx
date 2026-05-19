import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";

const initialForm = {
  company_name: "",
  contact_email: "",
  phone: "",
  address: "",
  gst_number: "",
  business_type: "",
  subscription_plan_id: "",
  status: "ACTIVE",
  admin_name: "",
  admin_email: "",
  admin_password: "",
};

export function TenantFormPage() {
  const navigate = useNavigate();
  const { tenantId } = useParams();
  const { user: actor } = useAuth();
  const isEditing = Boolean(tenantId);
  const isSuperAdmin = actor?.role === "SUPER_ADMIN";
  const [form, setForm] = useState(initialForm);
  const [plans, setPlans] = useState([]);
  const [originalStatus, setOriginalStatus] = useState("ACTIVE");
  const [state, setState] = useState({ loading: true, saving: false, error: "" });

  useEffect(() => {
    let active = true;
    const requests = [];
    if (isEditing) {
      requests.push(api.get(`/tenants/${tenantId}`));
    }
    if (isSuperAdmin) {
      requests.push(api.get("/subscription-plans", { params: { page_size: 50 } }));
    }

    if (!requests.length) {
      setState({ loading: false, saving: false, error: "" });
      return () => {
        active = false;
      };
    }

    Promise.all(requests)
      .then((responses) => {
        if (!active) return;
        const tenantResponse = isEditing ? responses[0] : null;
        const planResponse = isSuperAdmin ? responses[responses.length - 1] : null;

        if (tenantResponse) {
          const data = tenantResponse.data;
          setForm({
            ...initialForm,
            company_name: data.company_name ?? "",
            contact_email: data.contact_email ?? "",
            phone: data.phone ?? "",
            address: data.address ?? "",
            gst_number: data.gst_number ?? "",
            business_type: data.business_type ?? "",
            subscription_plan_id: data.subscription_plan_id ? String(data.subscription_plan_id) : "",
            status: data.status ?? "ACTIVE",
          });
          setOriginalStatus(data.status ?? "ACTIVE");
        }

        if (planResponse) {
          setPlans(planResponse.data.items ?? []);
        }

        setState({ loading: false, saving: false, error: "" });
      })
      .catch((error) => {
        if (!active) return;
        setState({
          loading: false,
          saving: false,
          error: error?.response?.data?.detail ?? "Unable to load tenant details.",
        });
      });

    return () => {
      active = false;
    };
  }, [isEditing, isSuperAdmin, tenantId]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, saving: true, error: "" }));

    try {
      if (isEditing) {
        await api.patch(`/tenants/${tenantId}`, {
          company_name: form.company_name,
          contact_email: form.contact_email,
          phone: form.phone || null,
          address: form.address || null,
          gst_number: form.gst_number || null,
          business_type: form.business_type || null,
          subscription_plan_id: isSuperAdmin && form.subscription_plan_id ? Number(form.subscription_plan_id) : undefined,
        });

        if (isSuperAdmin && originalStatus !== form.status) {
          await api.patch(`/tenants/${tenantId}/status`, { status: form.status });
        }

        navigate(`/tenants/${tenantId}`);
        return;
      }

      const response = await api.post("/tenants", {
        company_name: form.company_name,
        contact_email: form.contact_email,
        phone: form.phone || null,
        address: form.address || null,
        gst_number: form.gst_number || null,
        business_type: form.business_type || null,
        subscription_plan_id: isSuperAdmin && form.subscription_plan_id ? Number(form.subscription_plan_id) : null,
        admin_name: form.admin_name || null,
        admin_email: form.admin_email || null,
        admin_password: form.admin_password || null,
      });
      navigate(`/tenants/${response.data.id}`);
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to save this tenant.",
      }));
    }
  }

  return (
    <div className="view-stack">
      <PageHeader
        eyebrow="SaaS Administration"
        title={isEditing ? "Edit Tenant" : "Create Tenant"}
        description="Manage company profile details, contact data, and tenant administrator onboarding."
        backTo={isEditing ? `/tenants/${tenantId}` : "/tenants"}
      />

      <form className="workspace-card form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading tenant form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
            <div className="form-grid-wide">
              <label>
                Company name
                <input className="field-input" value={form.company_name} onChange={(event) => update("company_name", event.target.value)} required />
              </label>
              <label>
                Contact email
                <input className="field-input" type="email" value={form.contact_email} onChange={(event) => update("contact_email", event.target.value)} required />
              </label>
              <label>
                Phone
                <input className="field-input" value={form.phone} onChange={(event) => update("phone", event.target.value)} />
              </label>
              <label>
                Business type
                <input className="field-input" value={form.business_type} onChange={(event) => update("business_type", event.target.value)} />
              </label>
              <label>
                GST number
                <input className="field-input" value={form.gst_number} onChange={(event) => update("gst_number", event.target.value)} />
              </label>
              {isSuperAdmin ? (
                <label>
                  Subscription plan
                  <select className="field-input" value={form.subscription_plan_id} onChange={(event) => update("subscription_plan_id", event.target.value)}>
                    <option value="">Default Starter</option>
                    {plans.map((plan) => (
                      <option key={plan.id} value={plan.id}>
                        {plan.name}
                      </option>
                    ))}
                  </select>
                </label>
              ) : null}
              {isEditing && isSuperAdmin ? (
                <label>
                  Status
                  <select className="field-input" value={form.status} onChange={(event) => update("status", event.target.value)}>
                    <option value="ACTIVE">ACTIVE</option>
                    <option value="DISABLED">DISABLED</option>
                  </select>
                </label>
              ) : null}
              <label className="field-span-full">
                Address
                <textarea className="field-input field-textarea" value={form.address} onChange={(event) => update("address", event.target.value)} />
              </label>

              {!isEditing ? (
                <>
                  <label>
                    Tenant admin name
                    <input className="field-input" value={form.admin_name} onChange={(event) => update("admin_name", event.target.value)} />
                  </label>
                  <label>
                    Tenant admin email
                    <input className="field-input" type="email" value={form.admin_email} onChange={(event) => update("admin_email", event.target.value)} />
                  </label>
                  <label>
                    Tenant admin password
                    <input className="field-input" type="password" value={form.admin_password} onChange={(event) => update("admin_password", event.target.value)} />
                  </label>
                </>
              ) : null}
            </div>

            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={state.saving}>
                {state.saving ? "Saving…" : isEditing ? "Save Tenant" : "Create Tenant"}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
