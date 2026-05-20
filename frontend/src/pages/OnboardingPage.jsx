import { useEffect, useMemo, useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";

import { LottieAnimation } from "../components/common/LottieAnimation";
import { Icon } from "../components/Icon";
import { useAuth } from "../contexts/AuthContext";
import api from "../lib/api";
import {
  ONBOARDING_STATUS_COMPLETED,
  ONBOARDING_STATUS_PENDING,
  ONBOARDING_STATUS_SKIPPED,
  getOnboardingPrefsStorageKey,
  getOnboardingStatus,
  setOnboardingStatus,
} from "../lib/onboarding";

export function OnboardingPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { tenant, user, isLoading, refreshProfile } = useAuth();
  const [form, setForm] = useState({
    company_name: "",
    business_type: "",
    address: "",
    phone: "",
    country: "India",
    currency: "INR",
    time_zone: "Asia/Kolkata",
  });
  const [state, setState] = useState({ saving: false, error: "", success: "" });
  const [currentStep, setCurrentStep] = useState(0);

  const tenantId = tenant?.id ?? null;
  const preferencesKey = tenantId ? getOnboardingPrefsStorageKey(tenantId) : null;
  const onboardingStatus = tenantId ? getOnboardingStatus(tenantId) : ONBOARDING_STATUS_PENDING;
  const isSetupComplete = onboardingStatus === ONBOARDING_STATUS_COMPLETED;
  const isSkipped = onboardingStatus === ONBOARDING_STATUS_SKIPPED;
  const isResumeMode = searchParams.get("resume") === "1";

  const setupSteps = [
    {
      key: "profile",
      eyebrow: "Step 1",
      title: "Workspace profile",
      description: "Start with the company details your team will recognize across Northstar.",
      icon: "building",
      accent: "onboarding-accent-blue",
      previewLabel: "Company and contact setup",
      highlights: ["Organization name", "Industry", "Address", "Primary phone"],
    },
    {
      key: "preferences",
      eyebrow: "Step 2",
      title: "Operating preferences",
      description: "Set the defaults that shape your workspace experience and day-one reports.",
      icon: "sliders",
      accent: "onboarding-accent-amber",
      previewLabel: "Regional defaults and display rules",
      highlights: ["Country", "Currency", "Time zone", "Workspace defaults"],
    },
  ];

  const profileStepReady = Boolean(form.company_name?.trim() && form.business_type?.trim());

  const checklistItems = useMemo(
    () => [
      {
        title: "Complete company profile",
        description: "Add your organization name and business type.",
        done: Boolean(form.company_name?.trim() && form.business_type?.trim()),
      },
      {
        title: "Add contact details",
        description: "Save your business address and primary phone.",
        done: Boolean(form.address?.trim() && form.phone?.trim()),
      },
      {
        title: "Set operating defaults",
        description: "Review your country, currency, and time zone.",
        done: Boolean(form.country && form.currency && form.time_zone),
      },
      {
        title: "Finish workspace setup",
        description: "Save your setup and move into daily operations.",
        done: isSetupComplete,
      },
    ],
    [form.address, form.business_type, form.company_name, form.country, form.currency, form.phone, form.time_zone, isSetupComplete],
  );

  const completedChecklistCount = checklistItems.filter((item) => item.done).length;
  const checklistProgress = Math.round((completedChecklistCount / checklistItems.length) * 100);

  const quickActions = useMemo(() => {
    if (user?.role === "INVENTORY_MANAGER") {
      return [
        {
          title: "Add inventory items",
          description: "Create your first SKUs and product records before receiving stock.",
          icon: "box",
          action: "Open items",
          onClick: () => navigate("/items/new"),
        },
        {
          title: "Set up warehouses",
          description: "Create storage locations so transfers and receiving stay accurate.",
          icon: "warehouse",
          action: "Create warehouse",
          onClick: () => navigate("/warehouses/new"),
        },
      ];
    }

    if (user?.role === "SALES_STAFF") {
      return [
        {
          title: "Add customers",
          description: "Save customer records so estimates, orders, and invoices flow cleanly.",
          icon: "users",
          action: "Create customer",
          onClick: () => navigate("/customers/new"),
        },
        {
          title: "Create your first order",
          description: "Start with a sales order and move it through packaging and invoicing.",
          icon: "cart",
          action: "New sales order",
          onClick: () => navigate("/sales-orders/new"),
        },
      ];
    }

    if (user?.role === "PURCHASE_STAFF") {
      return [
        {
          title: "Add vendors",
          description: "Set up supplier records before placing purchase orders and receives.",
          icon: "briefcase",
          action: "Create vendor",
          onClick: () => navigate("/vendors/new"),
        },
        {
          title: "Create purchase order",
          description: "Start inbound stock flows with your first supplier order.",
          icon: "clipboard",
          action: "New purchase order",
          onClick: () => navigate("/purchase-orders/new"),
        },
      ];
    }

    if (user?.role === "VIEWER") {
      return [
        {
          title: "Review item catalog",
          description: "Browse the current inventory catalog before the team starts transacting.",
          icon: "box",
          action: "Open items",
          onClick: () => navigate("/items"),
        },
        {
          title: "Review warehouse stock",
          description: "Check warehouse visibility so stock positions and low-stock signals are clear.",
          icon: "warehouse",
          action: "Open warehouses",
          onClick: () => navigate("/warehouses"),
        },
      ];
    }

    return [
      {
        title: "Add your first item",
        description: "Build the catalog foundation for purchasing, stock movement, and sales.",
        icon: "box",
        action: "Create item",
        onClick: () => navigate("/items/new"),
      },
      {
        title: "Create a warehouse",
        description: "Assign where stock lives so receiving, low stock, and transfers stay accurate.",
        icon: "warehouse",
        action: "New warehouse",
        onClick: () => navigate("/warehouses/new"),
      },
      {
        title: "Add vendors and customers",
        description: "Set up both sides of the workflow before you start purchasing and selling.",
        icon: "users",
        action: "Open contacts",
        onClick: () => navigate("/vendors"),
      },
    ];
  }, [navigate, user?.role]);

  const supportLinks = useMemo(() => {
    const links = [
      { label: "Open reports workspace", icon: "chart", onClick: () => navigate("/reports") },
      { label: "Review notification center", icon: "bell", onClick: () => navigate("/notifications") },
      { label: "Go to dashboard", icon: "dashboard", onClick: () => navigate("/dashboard") },
    ];

    if (user?.role === "TENANT_ADMIN") {
      links.splice(2, 0, {
        label: "Manage workspace settings",
        icon: "settings",
        onClick: () => navigate("/settings"),
      });
    }

    return links;
  }, [navigate, user?.role]);

  useEffect(() => {
    if (!tenant) {
      return;
    }

    let preferences = {};
    if (preferencesKey) {
      try {
        preferences = JSON.parse(window.localStorage.getItem(preferencesKey) ?? "{}");
      } catch {
        preferences = {};
      }
    }

    setForm({
      company_name: tenant.company_name ?? "",
      business_type: tenant.business_type ?? "",
      address: tenant.address ?? "",
      phone: tenant.phone ?? "",
      country: preferences.country ?? "India",
      currency: preferences.currency ?? "INR",
      time_zone: preferences.time_zone ?? "Asia/Kolkata",
    });
  }, [tenant, preferencesKey]);

  if (!isLoading && !user) {
    return <Navigate to="/login" replace />;
  }

  if (!isLoading && (!tenant || user?.role === "SUPER_ADMIN")) {
    return <Navigate to="/dashboard" replace />;
  }

  if (!isLoading && isSetupComplete) {
    return <Navigate to="/dashboard" replace />;
  }

  if (!isLoading && isSkipped && !isResumeMode) {
    return <Navigate to="/dashboard" replace />;
  }

  function updateField(field, value) {
    setState((current) => ({ ...current, error: "", success: "" }));
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (currentStep === 0) {
      handleNextStep();
      return;
    }

    if (!tenantId || !preferencesKey) {
      return;
    }

    setState({ saving: true, error: "", success: "" });

    try {
      await api.patch(`/tenants/${tenantId}`, {
        company_name: form.company_name,
        business_type: form.business_type || null,
        address: form.address || null,
        phone: form.phone || null,
      });

      window.localStorage.setItem(
        preferencesKey,
        JSON.stringify({
          country: form.country,
          currency: form.currency,
          time_zone: form.time_zone,
        }),
      );
      setOnboardingStatus(tenantId, ONBOARDING_STATUS_COMPLETED);

      await refreshProfile();

      setState({ saving: false, error: "", success: "Workspace details saved successfully." });
      navigate("/dashboard", { replace: true });
    } catch (error) {
      setState({
        saving: false,
        error: error?.response?.data?.detail ?? "Unable to finish workspace setup right now.",
        success: "",
      });
    }
  }

  function handleSkip() {
    if (tenantId) {
      setOnboardingStatus(tenantId, ONBOARDING_STATUS_SKIPPED);
    }
    navigate("/dashboard", { replace: true });
  }

  function handleNextStep() {
    if (!profileStepReady) {
      setState((current) => ({
        ...current,
        error: "Add the company name and business type before moving to operating preferences.",
      }));
      return;
    }

    setState((current) => ({ ...current, error: "" }));
    setCurrentStep(1);
  }

  function handlePreviousStep() {
    setState((current) => ({ ...current, error: "" }));
    setCurrentStep(0);
  }

  function handleStepChange(nextStep) {
    if (nextStep > currentStep && !profileStepReady) {
      handleNextStep();
      return;
    }
    setState((current) => ({ ...current, error: "" }));
    setCurrentStep(nextStep);
  }

  function goToPreviousPanel() {
    if (currentStep === 0) {
      return;
    }
    handleStepChange(currentStep - 1);
  }

  function goToNextPanel() {
    if (currentStep >= setupSteps.length - 1) {
      return;
    }
    handleStepChange(currentStep + 1);
  }

  function scrollToSetupForm() {
    document.getElementById("workspace-setup-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  const previousStep = currentStep > 0 ? setupSteps[currentStep - 1] : null;
  const nextStep = currentStep < setupSteps.length - 1 ? setupSteps[currentStep + 1] : null;
  const activeStep = setupSteps[currentStep];

  return (
    <div className="get-started-screen">
      <section className="get-started-shell">
        <header className="get-started-header">
          <div className="get-started-header-copy">
            <p className="eyebrow">Get Started</p>
            <h1>Get Started</h1>
          </div>
          <span className="get-started-mode-badge">Setup mode</span>
        </header>

        <section className="get-started-intro">
          <div>
            <h2>Hi {user?.name?.split(" ")[0] || "there"}, welcome to Northstar.</h2>
            <p>
              Let’s get your inventory workspace ready so your team can start receiving, selling, and moving stock
              without setup friction.
            </p>
          </div>
          {isResumeMode ? (
            <div className="get-started-resume-badge">
              <Icon name="undo" size={16} />
              <span>Resuming setup</span>
            </div>
          ) : null}
        </section>

        <section className="get-started-hero-grid">
          <article className="get-started-checklist-card">
            <div className="get-started-card-copy">
              <div className="get-started-card-header">
                <h3>Setup Checklist</h3>
                <span>
                  {completedChecklistCount} of {checklistItems.length}
                </span>
              </div>
              <div className="get-started-progress-track" aria-hidden="true">
                <span className="get-started-progress-bar" style={{ width: `${checklistProgress}%` }} />
              </div>
              <div className="get-started-checklist-grid">
                {checklistItems.map((item, index) => (
                  <div className={`get-started-checklist-item${item.done ? " is-complete" : ""}`} key={item.title}>
                    <span className="get-started-checklist-index">
                      {item.done ? <Icon name="check" size={14} /> : index + 1}
                    </span>
                    <div>
                      <strong>{item.title}</strong>
                      <p>{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="get-started-checklist-visual">
              <LottieAnimation
                animationKey="onboarding"
                size={260}
                className="lottie-animation--default"
                ariaLabel="Northstar setup illustration"
                decorative={false}
              />
            </div>
          </article>

          <aside className="get-started-video-card">
            <span className="get-started-video-orb get-started-video-orb-top" aria-hidden="true" />
            <span className="get-started-video-orb get-started-video-orb-bottom" aria-hidden="true" />
            <h3>See your setup flow</h3>
            <p>
              Review the setup sequence, finish your organization profile, and move directly into item, vendor, and
              warehouse operations.
            </p>
            <div className="get-started-video-actions">
              <button className="button button-ghost get-started-inline-button" type="button" onClick={scrollToSetupForm}>
                <Icon name="sparkles" size={16} />
                <span>Continue setup</span>
              </button>
              <button className="button button-ghost get-started-inline-button" type="button" onClick={handleSkip}>
                <Icon name="dashboard" size={16} />
                <span>Open dashboard</span>
              </button>
            </div>
          </aside>
        </section>

        <section className="get-started-content-grid">
          <div className="get-started-actions-panel">
            <h3>Quick Actions</h3>
            <div className="get-started-actions-grid">
              {quickActions.map((action) => (
                <article className="get-started-action-card" key={action.title}>
                  <span className="get-started-action-icon">
                    <Icon name={action.icon} size={18} />
                  </span>
                  <h4>{action.title}</h4>
                  <p>{action.description}</p>
                  <button className="primary-button get-started-action-button" type="button" onClick={action.onClick}>
                    {action.action}
                  </button>
                </article>
              ))}
            </div>
          </div>

          <aside className="get-started-support-panel">
            <h3>Resources & Support</h3>
            <p>
              Open the core product areas you’ll rely on most while your workspace is getting configured.
            </p>
            <div className="get-started-support-links">
              {supportLinks.map((link) => (
                <button className="get-started-support-link" key={link.label} type="button" onClick={link.onClick}>
                  <span>
                    <Icon name={link.icon} size={16} />
                    {link.label}
                  </span>
                  <Icon name="chevronRight" size={16} />
                </button>
              ))}
            </div>
          </aside>
        </section>

        <form className="auth-card auth-form auth-card-onboarding get-started-form-card" id="workspace-setup-form" onSubmit={handleSubmit}>
          <div className="auth-card-header">
            <p className="eyebrow">Workspace Profile</p>
            <h2>Tell us how your inventory operation is set up</h2>
            <p>
              {isSetupComplete
                ? "You can update these details anytime from Settings."
                : "Save these details once, then continue with daily stock workflows."}
            </p>
          </div>

          <div className="onboarding-carousel-showcase">
            <button
              type="button"
              className="onboarding-carousel-arrow"
              onClick={goToPreviousPanel}
              disabled={currentStep === 0}
              aria-label="Previous onboarding step"
            >
              <Icon name="chevronRight" size={20} className="onboarding-carousel-arrow-icon is-left" />
            </button>

            <div className="onboarding-carousel-rail">
              <div className="onboarding-carousel-side-panel is-left" aria-hidden={!previousStep}>
                {previousStep ? (
                  <>
                    <span className={`onboarding-carousel-side-icon ${previousStep.accent}`}>
                      <Icon name={previousStep.icon} size={20} />
                    </span>
                    <small>{previousStep.eyebrow}</small>
                    <strong>{previousStep.title}</strong>
                    <p>{previousStep.previewLabel}</p>
                  </>
                ) : (
                  <>
                    <span className="onboarding-carousel-side-placeholder" />
                    <small>Start here</small>
                    <strong>Workspace profile</strong>
                    <p>Begin with the organization details your team will recognize every day.</p>
                  </>
                )}
              </div>

              <div className={`onboarding-carousel-focus-card ${activeStep.accent}`}>
                <div className="onboarding-carousel-focus-top">
                  <span className="onboarding-carousel-focus-icon">
                    <Icon name={activeStep.icon} size={24} />
                  </span>
                  <div className="onboarding-carousel-copy">
                    <p className="eyebrow">{activeStep.eyebrow}</p>
                    <h3>{activeStep.title}</h3>
                    <p>{activeStep.description}</p>
                  </div>
                </div>

                <div className="onboarding-carousel-highlight-list">
                  {activeStep.highlights.map((item) => (
                    <div className="onboarding-carousel-highlight-item" key={item}>
                      <span className="onboarding-carousel-highlight-dot" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="onboarding-carousel-side-panel is-right" aria-hidden={!nextStep}>
                {nextStep ? (
                  <>
                    <span className={`onboarding-carousel-side-icon ${nextStep.accent}`}>
                      <Icon name={nextStep.icon} size={20} />
                    </span>
                    <small>{nextStep.eyebrow}</small>
                    <strong>{nextStep.title}</strong>
                    <p>{nextStep.previewLabel}</p>
                  </>
                ) : (
                  <>
                    <span className="onboarding-carousel-side-placeholder" />
                    <small>Final step</small>
                    <strong>Finish setup</strong>
                    <p>Save your defaults and move into the dashboard with the reminder cleared.</p>
                  </>
                )}
              </div>
            </div>

            <button
              type="button"
              className="onboarding-carousel-arrow"
              onClick={goToNextPanel}
              disabled={currentStep === setupSteps.length - 1}
              aria-label="Next onboarding step"
            >
              <Icon name="chevronRight" size={20} className="onboarding-carousel-arrow-icon" />
            </button>
          </div>

          <div className="onboarding-carousel-dots" role="tablist" aria-label="Onboarding steps">
            {setupSteps.map((step, index) => (
              <button
                key={step.key}
                type="button"
                role="tab"
                aria-selected={currentStep === index}
                className={`onboarding-carousel-dot ${currentStep === index ? "is-active" : ""}`}
                onClick={() => handleStepChange(index)}
              >
                <span className="sr-only">{step.title}</span>
              </button>
            ))}
          </div>

          <div className="onboarding-carousel-stage">

            <div className="onboarding-carousel-track" style={{ transform: `translateX(-${currentStep * 100}%)` }}>
              <section className="form-section onboarding-carousel-slide">
                <div className="form-section-heading">
                  <h3>Organization details</h3>
                  <p>These values are saved to your tenant profile and shown across the workspace.</p>
                </div>
                <div className="form-grid">
                  <label>
                    Organization name
                    <input
                      type="text"
                      value={form.company_name}
                      onChange={(event) => updateField("company_name", event.target.value)}
                      required
                    />
                  </label>
                  <label>
                    Industry
                    <input
                      type="text"
                      value={form.business_type}
                      onChange={(event) => updateField("business_type", event.target.value)}
                      placeholder="Retail, wholesale, manufacturing..."
                    />
                  </label>
                  <label className="field-span-full">
                    Business address
                    <textarea
                      value={form.address}
                      onChange={(event) => updateField("address", event.target.value)}
                      rows={4}
                      placeholder="Street, locality, city, state, PIN code"
                    />
                  </label>
                  <label>
                    Contact phone
                    <input
                      type="text"
                      value={form.phone}
                      onChange={(event) => updateField("phone", event.target.value)}
                      placeholder="+91 98765 43210"
                    />
                  </label>
                </div>
              </section>

              <section className="form-section onboarding-carousel-slide">
                <div className="form-section-heading">
                  <h3>Operating preferences</h3>
                  <p>These preferences help shape the UI while fuller backend-backed settings continue to expand.</p>
                </div>
                <div className="form-grid">
                  <label>
                    Country
                    <select value={form.country} onChange={(event) => updateField("country", event.target.value)}>
                      <option value="India">India</option>
                      <option value="United Arab Emirates">United Arab Emirates</option>
                      <option value="Singapore">Singapore</option>
                      <option value="United States">United States</option>
                    </select>
                  </label>
                  <label>
                    Currency
                    <select value={form.currency} onChange={(event) => updateField("currency", event.target.value)}>
                      <option value="INR">INR - Indian Rupee</option>
                      <option value="USD">USD - US Dollar</option>
                      <option value="AED">AED - UAE Dirham</option>
                      <option value="SGD">SGD - Singapore Dollar</option>
                    </select>
                  </label>
                  <label>
                    Time zone
                    <select value={form.time_zone} onChange={(event) => updateField("time_zone", event.target.value)}>
                      <option value="Asia/Kolkata">Asia/Kolkata</option>
                      <option value="Asia/Dubai">Asia/Dubai</option>
                      <option value="Asia/Singapore">Asia/Singapore</option>
                      <option value="America/New_York">America/New_York</option>
                    </select>
                  </label>
                  <div className="onboarding-preferences-preview">
                    <span>Workspace defaults preview</span>
                    <strong>
                      {form.country} · {form.currency}
                    </strong>
                    <p>{form.time_zone} will be used for date and reporting displays in this browser session.</p>
                  </div>
                </div>
              </section>
            </div>
          </div>

          {state.error ? <p className="form-error">{state.error}</p> : null}
          {state.success ? <p className="surface-success">{state.success}</p> : null}

          <div className="auth-card-footer auth-card-footer-split">
            <div className="onboarding-carousel-actions">
              <button className="button button-ghost" type="button" onClick={handleSkip}>
                Finish later
              </button>
              {currentStep > 0 ? (
                <button className="button button-ghost" type="button" onClick={handlePreviousStep}>
                  Back
                </button>
              ) : null}
            </div>
            {currentStep === 0 ? (
              <button className="primary-button" type="button" onClick={handleNextStep}>
                Continue to preferences
              </button>
            ) : (
              <button className="primary-button" type="submit" disabled={state.saving}>
                {state.saving ? "Saving workspace..." : "Finish setup"}
              </button>
            )}
          </div>

          {isSkipped ? (
            <p className="onboarding-inline-note">
              You previously skipped setup. Save it now to remove the reminder from <Link to="/dashboard">Home → Get Started</Link>.
            </p>
          ) : null}
        </form>
      </section>
    </div>
  );
}
