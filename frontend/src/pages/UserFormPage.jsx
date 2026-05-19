import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";

const userStatuses = ["ACTIVE", "INACTIVE"];

const allRoles = [
  "SUPER_ADMIN",
  "TENANT_ADMIN",
  "INVENTORY_MANAGER",
  "SALES_STAFF",
  "PURCHASE_STAFF",
  "VIEWER",
];

const initialForm = {
  name: "",
  email: "",
  password: "",
  role: "VIEWER",
  status: "ACTIVE",
  tenant_id: "",
};

export function UserFormPage() {
  const navigate = useNavigate();
  const { userId } = useParams();
  const { user: actor } = useAuth();
  const isEditing = Boolean(userId);
  const isSuperAdmin = actor?.role === "SUPER_ADMIN";
  const roleOptions = useMemo(() => (isSuperAdmin ? allRoles : allRoles.filter((role) => role !== "SUPER_ADMIN")), [isSuperAdmin]);
  const [form, setForm] = useState(initialForm);
  const [tenants, setTenants] = useState([]);
  const [originalUser, setOriginalUser] = useState(null);
  const [state, setState] = useState({ loading: true, saving: false, error: "" });

  useEffect(() => {
    let active = true;

    Promise.all([
      isSuperAdmin ? api.get("/tenants", { params: { page_size: 100 } }) : Promise.resolve({ data: { items: [] } }),
      isEditing ? api.get(`/users/${userId}`) : Promise.resolve({ data: null }),
    ])
      .then(([tenantResponse, userResponse]) => {
        if (!active) return;
        setTenants(tenantResponse.data.items ?? []);

        if (userResponse.data) {
          const record = userResponse.data;
          setOriginalUser(record);
          setForm({
            name: record.name ?? "",
            email: record.email ?? "",
            password: "",
            role: record.role ?? "VIEWER",
            status: record.status ?? "ACTIVE",
            tenant_id: record.tenant_id ? String(record.tenant_id) : "",
          });
        }

        setState({ loading: false, saving: false, error: "" });
      })
      .catch((error) => {
        if (!active) return;
        setState({
          loading: false,
          saving: false,
          error: error?.response?.data?.detail ?? "Unable to prepare the user form.",
        });
      });

    return () => {
      active = false;
    };
  }, [isEditing, isSuperAdmin, userId]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, saving: true, error: "" }));

    try {
      if (isEditing) {
        await api.patch(`/users/${userId}`, {
          name: form.name,
          email: form.email,
        });

        if (originalUser?.role !== form.role) {
          await api.patch(`/users/${userId}/role`, { role: form.role });
        }

        if (originalUser?.status !== form.status) {
          await api.patch(`/users/${userId}/status`, { status: form.status });
        }

        navigate(`/users/${userId}`);
        return;
      }

      const payload = {
        name: form.name,
        email: form.email,
        password: form.password,
        role: form.role,
        status: form.status,
        tenant_id: form.role === "SUPER_ADMIN" ? null : isSuperAdmin ? Number(form.tenant_id) : null,
      };
      const response = await api.post("/users", payload);
      navigate(`/users/${response.data.id}`);
    } catch (error) {
      setState((current) => ({
        ...current,
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to save this user.",
      }));
    }
  }

  const showTenantField = isSuperAdmin && form.role !== "SUPER_ADMIN" && !isEditing;

  return (
    <div className="view-stack">
      <section className="page-intro">
        <div>
          <p className="page-kicker">Admin Workspace</p>
          <h2>{isEditing ? "Edit User" : "Create User"}</h2>
          <p>Manage user identity, workspace role, status, and tenant access from one form.</p>
        </div>
        <BackButton fallbackTo={isEditing ? `/users/${userId}` : "/users"} />
      </section>

      <form className="workspace-card form-shell" onSubmit={handleSubmit}>
        {state.loading ? <div className="surface-placeholder">Loading user form…</div> : null}
        {state.error ? <div className="surface-error">{state.error}</div> : null}

        {!state.loading ? (
          <>
            <div className="form-grid-wide">
              <label>
                Full name
                <input className="field-input" value={form.name} onChange={(event) => update("name", event.target.value)} required />
              </label>
              <label>
                Email
                <input className="field-input" type="email" value={form.email} onChange={(event) => update("email", event.target.value)} required />
              </label>
              {!isEditing ? (
                <label>
                  Temporary password
                  <input className="field-input" type="password" value={form.password} onChange={(event) => update("password", event.target.value)} required />
                </label>
              ) : null}
              <label>
                Role
                <select className="field-input" value={form.role} onChange={(event) => update("role", event.target.value)} required>
                  {roleOptions.map((role) => (
                    <option key={role} value={role}>
                      {role.replaceAll("_", " ")}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Status
                <select className="field-input" value={form.status} onChange={(event) => update("status", event.target.value)} required>
                  {userStatuses.map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </label>
              {showTenantField ? (
                <label>
                  Tenant
                  <select className="field-input" value={form.tenant_id} onChange={(event) => update("tenant_id", event.target.value)} required>
                    <option value="">Select tenant</option>
                    {tenants.map((tenant) => (
                      <option key={tenant.id} value={tenant.id}>
                        {tenant.company_name}
                      </option>
                    ))}
                  </select>
                </label>
              ) : null}
              {isEditing && originalUser?.tenant ? (
                <label>
                  Tenant
                  <input className="field-input" value={originalUser.tenant.company_name} disabled />
                </label>
              ) : null}
            </div>
            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={state.saving}>
                {state.saving ? "Saving…" : isEditing ? "Save User" : "Create User"}
              </button>
            </div>
          </>
        ) : null}
      </form>
    </div>
  );
}
