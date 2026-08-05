import type { SurfaceStyle } from "@/components/dashboard/DashboardProvider";

/**
 * Классы заливки для выпадающих меню/поповеров (дропдауны, панель уведомлений, профиль-меню и т.п.).
 * Solid: непрозрачная карточка (как сейчас). Glass: полупрозрачная, в тон окнам/сайдбару.
 */
export function menuSurfaceClass(surfaceStyle: SurfaceStyle): string {
  return surfaceStyle === "glass" ? "bg-card/78 dark:bg-card/55 backdrop-blur-xl" : "bg-card";
}

/**
 * Классы заливки для больших модальных окон (пост, день календаря, подтверждения).
 */
export function modalSurfaceClass(surfaceStyle: SurfaceStyle): string {
  return surfaceStyle === "glass" ? "bg-card/85 dark:bg-card/70 backdrop-blur-2xl" : "bg-card";
}

/**
 * Классы кнопки-иконки в топбаре (тема/уведомления/профиль):
 * стекло — только в режиме «Жидкое стекло», иначе обычная сплошная кнопка.
 */
export function topbarButtonClass(surfaceStyle: SurfaceStyle): string {
  return surfaceStyle === "glass" ? "btn-glass" : "btn-solid";
}
