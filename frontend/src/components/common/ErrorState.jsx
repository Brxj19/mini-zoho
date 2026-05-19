import { LottieAnimation } from "./LottieAnimation";

export function ErrorState({
  animationKey = "emptyData",
  title = "Something went wrong",
  description = "We could not load this view right now.",
  retryLabel = "Try Again",
  onRetry,
}) {
  return (
    <div className="error-state" role="alert">
      <LottieAnimation
        animationKey={animationKey}
        size={220}
        className="lottie-animation--default"
        ariaLabel={title}
        decorative={false}
      />
      <h3 className="empty-state__title">{title}</h3>
      <p className="empty-state__description">{description}</p>
      {onRetry ? (
        <div className="empty-state__actions">
          <button className="button button-primary" type="button" onClick={onRetry}>
            {retryLabel}
          </button>
        </div>
      ) : null}
    </div>
  );
}
