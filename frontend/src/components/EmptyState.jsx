import { EmptyState as CommonEmptyState } from "./common/EmptyState";

export function EmptyState({ title, description, actionLabel, actionTo, onAction, animationKey = "emptyData" }) {
  return (
    <CommonEmptyState
      animationKey={animationKey}
      title={title}
      description={description}
      primaryActionLabel={actionLabel}
      primaryActionTo={actionTo}
      onPrimaryAction={onAction}
      compact
    />
  );
}
