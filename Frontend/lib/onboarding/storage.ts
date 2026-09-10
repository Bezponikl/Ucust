import type { ChannelId } from "@/lib/channels";
import { CONNECTIBLE_CHANNELS } from "@/lib/channels";
import type { BrandProfile, WizardInput } from "./types";
import { EMPTY_INPUT } from "./types";

export interface OnboardingState {
  input: WizardInput;
  profile: BrandProfile | null;
}

const KEY = "ucust:onboarding";

export function loadOnboarding(): OnboardingState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<OnboardingState>;
    // Бережно к старым сессиям: типы могли пополниться полями (channelHandles,
    // fileData), а их в сохранённом JSON нет — слияние с дефолтами лечит расхождение.
    // Из уже отмеченных соцсетей оставляем только доступные к подключению: в старых
    // версиях можно было «выбрать» любую, сейчас проверкой занимается бэк.
    const rawInput: WizardInput = { ...EMPTY_INPUT, ...(parsed.input ?? {}) };
    const keep = new Set<string>(CONNECTIBLE_CHANNELS);
    const input: WizardInput = {
      ...rawInput,
      socials: rawInput.socials.filter((id) => keep.has(id)),
      channelHandles: Object.fromEntries(
        Object.entries(rawInput.channelHandles ?? {}).filter(([id]) => keep.has(id)),
      ) as Partial<Record<ChannelId, string>>,
    };
    return { input, profile: parsed.profile ?? null };
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
