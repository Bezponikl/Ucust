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

/**
 * Сброс рабочей области под нового пользователя: профиль проекта и следы прошлой
 * сессии (подсказки, трекер настройки). Нужен после регистрации — иначе демо-проект,
 * засеянный входом в той же вкладке, покажет новому аккаунту чужой дашборд.
 */
export function clearWorkspace(): void {
  if (typeof window === "undefined") return;
  clearOnboarding();
  try {
    ["uc_tour", "uc_setup_done", "uc_setup_dismissed"].forEach((k) =>
      window.sessionStorage.removeItem(k),
    );
  } catch {
    /* ignore */
  }
}
