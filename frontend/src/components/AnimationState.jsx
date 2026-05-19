import { animations } from "../config/animations";
import { LottieAnimation } from "./common/LottieAnimation";

export function AnimationState({ animationKey = "emptyData", compact = false }) {
  const config = animations[animationKey] ?? animations.emptyData;

  return (
    <div className={`animation-state ${compact ? "is-compact" : ""}`} aria-hidden="true">
      <div className="animation-state-stage">
        <LottieAnimation
          animationKey={animationKey}
          size={compact ? 148 : 240}
          className={compact ? "lottie-animation--compact animation-player" : "lottie-animation--default animation-player"}
          ariaLabel={config.label}
          decorative={false}
        />
      </div>
      {!compact ? (
        <div className="animation-state-copy">
          <strong>{config.label}</strong>
          <span>{config.usage}</span>
        </div>
      ) : null}
    </div>
  );
}
