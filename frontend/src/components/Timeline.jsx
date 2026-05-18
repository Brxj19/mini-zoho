export function Timeline({ steps = [], currentStep }) {
  return (
    <ol className="timeline">
      {steps.map((step, index) => {
        const activeIndex = steps.indexOf(currentStep);
        const state =
          step === currentStep ? "current" : index < activeIndex ? "complete" : "upcoming";

        return (
          <li key={step} className={`timeline-step is-${state}`}>
            <span className="timeline-dot" />
            <span className="timeline-label">{step.replaceAll("_", " ")}</span>
          </li>
        );
      })}
    </ol>
  );
}
