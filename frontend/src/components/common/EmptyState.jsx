import { Link } from "react-router-dom";

import { LottieAnimation } from "./LottieAnimation";

export function EmptyState({
  animationKey = "emptyData",
  title,
  description,
  primaryActionLabel,
  onPrimaryAction,
  primaryActionTo,
  secondaryActionLabel,
  onSecondaryAction,
  secondaryActionTo,
  compact = false,
}) {
  return (
    <div className={`empty-state ${compact ? "empty-state--compact" : ""}`.trim()} role="status" aria-live="polite">
      <LottieAnimation
        animationKey={animationKey}
        size={compact ? 148 : 240}
        className={compact ? "lottie-animation--compact empty-state__animation" : "lottie-animation--default empty-state__animation"}
        ariaLabel={title || "Empty state"}
        decorative={false}
      />
      {title ? <h3 className="empty-state__title">{title}</h3> : null}
      {description ? <p className="empty-state__description">{description}</p> : null}
      {primaryActionLabel || secondaryActionLabel ? (
        <div className="empty-state__actions">
          {primaryActionLabel && primaryActionTo ? (
            <Link className="button button-primary" to={primaryActionTo}>
              {primaryActionLabel}
            </Link>
          ) : null}
          {primaryActionLabel && !primaryActionTo && onPrimaryAction ? (
            <button className="button button-primary" type="button" onClick={onPrimaryAction}>
              {primaryActionLabel}
            </button>
          ) : null}
          {secondaryActionLabel && secondaryActionTo ? (
            <Link className="button button-ghost" to={secondaryActionTo}>
              {secondaryActionLabel}
            </Link>
          ) : null}
          {secondaryActionLabel && !secondaryActionTo && onSecondaryAction ? (
            <button className="button button-ghost" type="button" onClick={onSecondaryAction}>
              {secondaryActionLabel}
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
