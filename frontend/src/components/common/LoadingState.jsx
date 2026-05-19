import { LottieAnimation } from "./LottieAnimation";

export function LoadingState({
  animationKey = "appLoading",
  message = "Loading workspace…",
  fullPage = false,
  compact = false,
}) {
  return (
    <div className={`loading-state ${fullPage ? "loading-state--full-page" : ""} ${compact ? "loading-state--compact" : ""}`.trim()} role="status" aria-live="polite">
      <LottieAnimation
        animationKey={animationKey}
        size={compact ? 132 : fullPage ? 184 : 148}
        className={compact ? "lottie-animation--compact" : "lottie-animation--default"}
        ariaLabel={message}
        decorative={false}
      />
      <p>{message}</p>
    </div>
  );
}
