/**
 * Интерактивный тур по дашборду: мягкие поповеры у элементов, без затемнения.
 * Цели помечаются атрибутом data-tour="<id>" — движок ищет ПЕРВЫЙ ВИДИМЫЙ элемент
 * с таким атрибутом, поэтому один и тот же id можно ставить и в десктопном
 * сайдбаре, и в мобильной нижней навигации.
 */

export interface TourStep {
  /** Значение data-tour у подсвечиваемого элемента. */
  target: string;
  title: string;
  text: string;
}

export const TOUR_STEPS: TourStep[] = [
  {
    target: "overview",
    title: "Это ваш центр управления",
    text: "Здесь видно, что происходит с соцсетями: охваты, реакции и что стоит сделать сегодня.",
  },
  {
    target: "ai-prompt",
    title: "Пост за одну фразу",
    text: "Опишите идею своими словами — или прикрепите фото — и UCust напишет пост под каждую сеть.",
  },
  {
    target: "nav-content",
    title: "Контент-план",
    text: "Все публикации: черновики, запланированные и вышедшие. Отсюда правят тексты и время выхода.",
  },
  {
    target: "nav-promos",
    title: "Акции",
    text: "Скидки, подарки и промокоды. ИИ придумает оффер, а карточка сама закроется в конце периода.",
  },
  {
    target: "nav-inbox",
    title: "Входящие",
    text: "Сообщения и отзывы из всех сетей в одном месте — с готовыми вариантами ответа.",
  },
  {
    target: "help",
    title: "Подсказки всегда здесь",
    text: "Откройте меню профиля — там «Как работает платформа» и поддержка.",
  },
];

export type TourState = "pending" | "done" | "skipped";

const TOUR_KEY = "uc_tour";

export function getTourState(): TourState | null {
  if (typeof window === "undefined") return null;
  try {
    const v = window.sessionStorage.getItem(TOUR_KEY);
    return v === "pending" || v === "done" || v === "skipped" ? v : null;
  } catch {
    return null;
  }
}

export function setTourState(state: TourState): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(TOUR_KEY, state);
  } catch {
    /* хранилище недоступно — тур просто не запомнится */
  }
}

/** Событие для запуска тура из любого места (пункт в меню профиля). */
export const TOUR_EVENT = "uc:tour-start";

export function startTour(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(TOUR_EVENT));
}
