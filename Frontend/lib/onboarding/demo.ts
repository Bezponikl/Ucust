import { pickPreset } from "./presets";
import { loadOnboarding, saveOnboarding } from "./storage";
import { EMPTY_INPUT } from "./types";

/**
 * Сеет демо-проект в sessionStorage, чтобы «вход» сразу вёл в дашборд с готовым
 * проектом. Не затирает уже пройденный онбординг (если профиль есть — оставляем).
 * ПОЗЖЕ заменяется реальной загрузкой проектов пользователя после авторизации.
 */
export function seedDemoProject(): void {
  if (loadOnboarding()?.profile) return;

  const name = "Кофейня «Тёплый день»";
  const preset = pickPreset("кофейня спешелти кофе выпечка");

  saveOnboarding({
    input: {
      ...EMPTY_INPUT,
      name,
      aboutMode: "manual",
      activity: "Городская кофейня со своей обжаркой",
      socials: ["vk", "telegram"],
    },
    profile: { name, ...preset },
  });
}
