import { EmptyState } from "./EmptyState";

export function SuccessState({
  title = "Success",
  description = "The action completed successfully.",
  animationKey = "onboarding",
}) {
  return <EmptyState animationKey={animationKey} title={title} description={description} />;
}
