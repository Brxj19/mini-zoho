export const ONBOARDING_STATUS_PENDING = "pending";
export const ONBOARDING_STATUS_SKIPPED = "skipped";
export const ONBOARDING_STATUS_COMPLETED = "completed";

export function getOnboardingPrefsStorageKey(tenantId) {
  return `northstar.inventory.onboarding.prefs.${tenantId}`;
}

export function getOnboardingStatusStorageKey(tenantId) {
  return `northstar.inventory.onboarding.status.${tenantId}`;
}

export function getLegacyOnboardingCompletionKey(tenantId) {
  return `northstar.inventory.onboarding.complete.${tenantId}`;
}

function hasWindow() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function getOnboardingStatus(tenantId) {
  if (!tenantId || !hasWindow()) {
    return ONBOARDING_STATUS_PENDING;
  }

  const statusKey = getOnboardingStatusStorageKey(tenantId);
  const storedStatus = window.localStorage.getItem(statusKey);
  if (storedStatus === ONBOARDING_STATUS_COMPLETED || storedStatus === ONBOARDING_STATUS_SKIPPED || storedStatus === ONBOARDING_STATUS_PENDING) {
    return storedStatus;
  }

  const legacyComplete = window.localStorage.getItem(getLegacyOnboardingCompletionKey(tenantId));
  if (legacyComplete === "true") {
    window.localStorage.setItem(statusKey, ONBOARDING_STATUS_COMPLETED);
    return ONBOARDING_STATUS_COMPLETED;
  }

  return ONBOARDING_STATUS_PENDING;
}

export function setOnboardingStatus(tenantId, status) {
  if (!tenantId || !hasWindow()) {
    return;
  }

  window.localStorage.setItem(getOnboardingStatusStorageKey(tenantId), status);
  window.localStorage.setItem(
    getLegacyOnboardingCompletionKey(tenantId),
    status === ONBOARDING_STATUS_COMPLETED ? "true" : "false",
  );
}

export function isOnboardingCompleted(tenantId) {
  return getOnboardingStatus(tenantId) === ONBOARDING_STATUS_COMPLETED;
}

export function isOnboardingSkipped(tenantId) {
  return getOnboardingStatus(tenantId) === ONBOARDING_STATUS_SKIPPED;
}
