import type { BrandProfile, WizardInput } from "./types";
import { pickPreset } from "./presets";

/**
 * Заглушка анализа бизнеса. Имитирует задержку и собирает профиль из нишевого
 * пресета, подставляя введённое название. ПОЗЖЕ заменяется на реальный fetch к API —
 * меняется только тело этой функции, сигнатура остаётся.
 */
export function analyzeBusiness(input: WizardInput): Promise<BrandProfile> {
  const text = [input.name, input.activity, input.difference, input.link].join(" ");
  const preset = pickPreset(text);
  const name = input.name.trim() || "Ваш бизнес";
  return new Promise((resolve) => {
    setTimeout(() => resolve({ name, ...preset }), 2500);
  });
}
