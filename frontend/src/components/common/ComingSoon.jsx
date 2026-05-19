import { EmptyState } from "./EmptyState";

export function ComingSoon({
  title = "Coming soon",
  description = "This workflow is being prepared for a future release.",
  animationKey = "comingSoon",
}) {
  return <EmptyState animationKey={animationKey} title={title} description={description} />;
}
