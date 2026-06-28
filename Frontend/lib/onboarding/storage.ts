import type { BrandProfile, WizardInput } from "./types";

export interface OnboardingState {
  input: WizardInput;
  profile: BrandProfile | null;
}

const KEY = "ucust:onboarding";

export function loadOnboarding(): OnboardingState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as OnboardingState) : null;
  } catch {
    return null;
  }
}

export function saveOnboarding(state: OnboardingState): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* sessionStorage недоступен — игнорируем */
  }
}

export function clearOnboarding(): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.removeItem(KEY);
  } catch {
    /* ignore */
  }
}
