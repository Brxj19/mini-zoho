import { Icon } from "./Icon";

function normalizeStepLabel(step) {
  return String(step).replaceAll("_", " ");
}

export function ProgressSteps({ items = [], terminal = null, className = "" }) {
  return (
    <ol className={`progress-steps ${className}`.trim()}>
      {items.map((item, index) => (
        <li
          key={item.key ?? item.label ?? `${index}`}
          className={`progress-step is-${item.state ?? "pending"}`}
        >
          <span className="progress-step-node" aria-hidden="true">
            {item.state === "complete" ? <Icon name="check" size={14} /> : null}
          </span>
          <div className="progress-step-copy">
            <strong>{item.label}</strong>
            {item.caption ? <span>{item.caption}</span> : null}
          </div>
        </li>
      ))}
      {terminal ? (
        <li className="progress-step-terminal">
          {terminal.badge}
        </li>
      ) : null}
    </ol>
  );
}

export function Timeline({ steps = [], currentStep }) {
  const activeIndex = steps.indexOf(currentStep);
  const items = steps.map((step, index) => ({
    key: step,
    label: normalizeStepLabel(step),
    state: step === currentStep ? "active" : index < activeIndex ? "complete" : "pending",
  }));

  return <ProgressSteps items={items} />;
}
