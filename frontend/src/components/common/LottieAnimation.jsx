import { DotLottieReact } from "@lottiefiles/dotlottie-react";
import { useEffect, useMemo, useState } from "react";

import { animations } from "../../config/animations";

function prefersReducedMotion() {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return false;
  }

  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function LottieAnimation({
  animationKey,
  src,
  width,
  height,
  size,
  loop = true,
  autoplay = true,
  className = "",
  ariaLabel,
  decorative = true,
}) {
  const [reducedMotion, setReducedMotion] = useState(prefersReducedMotion);

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
      return undefined;
    }

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handleChange = (event) => setReducedMotion(event.matches);

    setReducedMotion(mediaQuery.matches);

    if (typeof mediaQuery.addEventListener === "function") {
      mediaQuery.addEventListener("change", handleChange);
      return () => mediaQuery.removeEventListener("change", handleChange);
    }

    mediaQuery.addListener(handleChange);
    return () => mediaQuery.removeListener(handleChange);
  }, []);

  const resolvedSrc = src || animations[animationKey]?.src || "";
  const resolvedLabel = ariaLabel || animations[animationKey]?.label || "Animation";
  const resolvedWidth = width ?? size ?? 240;
  const resolvedHeight = height ?? size ?? resolvedWidth;

  const style = useMemo(
    () => ({
      width: typeof resolvedWidth === "number" ? `${resolvedWidth}px` : resolvedWidth,
      height: typeof resolvedHeight === "number" ? `${resolvedHeight}px` : resolvedHeight,
    }),
    [resolvedHeight, resolvedWidth],
  );

  if (!resolvedSrc) {
    return (
      <div
        className={`lottie-animation lottie-animation--fallback ${className}`.trim()}
        style={style}
        aria-hidden={decorative ? "true" : undefined}
        aria-label={decorative ? undefined : resolvedLabel}
        role={decorative ? undefined : "img"}
      >
        <span className="lottie-animation__fallback-orb" />
        <span className="lottie-animation__fallback-orb is-offset" />
      </div>
    );
  }

  return (
    <div
      className={`lottie-animation ${className}`.trim()}
      style={style}
      aria-hidden={decorative ? "true" : undefined}
      aria-label={decorative ? undefined : resolvedLabel}
      role={decorative ? undefined : "img"}
    >
      <DotLottieReact
        src={resolvedSrc}
        loop={loop}
        autoplay={autoplay && !reducedMotion}
      />
    </div>
  );
}
