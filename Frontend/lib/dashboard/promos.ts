import type { ChannelId } from "@/lib/channels";
import type { IconName } from "@/lib/icons/solar";

export type PromoStatus = "active" | "scheduled" | "finished";

/** Механика акции — задаёт иконку, цвет и подсказку оффера. */
export type PromoType = "discount" | "gift" | "event" | "code";

export interface Promo {
  id: string;
  title: string;
  description: string;
  type: PromoType;
  status: PromoStatus;
  period: string;
  channels: ChannelId[];
  metricLabel: string;
  metricValue: string;
  image?: string;     // обложка карточки
  discount?: string;  // оверлей на фото: "-20%", "2×1", и т.п.
  code?: string;      // промокод
  uses?: number;      // числовой счётчик для прогресс-бара
  goal?: number;      // цель (для прогресс-бара)
  stats?: PromoStats; // цифры для вкладки «Статистика»
}

/** Показатели акции: в проде приходят из аналитики площадок. */
export interface PromoStats {
  views: number;
  clicks: number;
  /** Использования по дням — для графика. */
  daily: number[];
}

export const PROMO_STATUS_LABEL: Record<PromoStatus, string> = {
  active: "Активна",
  scheduled: "Запланирована",
  finished: "Завершена",
};

/** Оформление механики: иконка, цвета для плейсхолдера обложки и чипа. */
export const PROMO_TYPE: Record<
  PromoType,
  { label: string; icon: IconName; hint: string; chip: string; cover: string; tint: string }
> = {
  discount: {
    label: "Скидка",
    icon: "trending",
    hint: "−20%",
    chip: "bg-brand/10 text-brand",
    cover: "from-brand/25 via-brand/10 to-transparent text-brand",
    tint: "text-brand",
  },
  gift: {
    label: "Подарок",
    icon: "gift",
    hint: "2×1",
    chip: "bg-brand-pink/10 text-brand-pink",
    cover: "from-brand-pink/25 via-brand-pink/10 to-transparent text-brand-pink",
    tint: "text-brand-pink",
  },
  event: {
    label: "Событие",
    icon: "calendar",
    hint: "🎂",
    chip: "bg-brand-orange/10 text-brand-orange",
    cover: "from-brand-orange/25 via-brand-orange/10 to-transparent text-brand-orange",
    tint: "text-brand-orange",
  },
  code: {
    label: "Промокод",
    icon: "link",
    hint: "",
    chip: "bg-brand-purple/10 text-brand-purple",
    cover: "from-brand-purple/25 via-brand-purple/10 to-transparent text-brand-purple",
    tint: "text-brand-purple",
  },
};

export const PROMO_TYPE_ORDER: PromoType[] = ["discount", "gift", "event", "code"];

/** Фотобанк демо-обложек (в проде — медиатека бизнеса). */
export const PROMO_IMAGE_POOL = [
  "/content/latteart.jpg",
  "/content/drinks.jpg",
  "/content/interior.jpg",
  "/content/barista.jpg",
  "/content/newdrink.jpg",
];

export const PROMOS: Promo[] = [
  {
    id: "pr1",
    title: "Счастливые часы",
    description: "Все напитки по будням с 15:00 до 17:00",
    type: "discount",
    status: "active",
    period: "1 фев — 28 фев",
    channels: ["vk", "telegram"],
    metricLabel: "Использований за неделю",
    metricValue: "248",
    image: "/content/latteart.jpg",
    discount: "−20%",
    code: "HAPPY28",
    uses: 248,
    goal: 300,
    stats: { views: 12480, clicks: 1310, daily: [18, 24, 31, 27, 35, 42, 38, 33] },
  },
  {
    id: "pr2",
    title: "Второй кофе в подарок",
    description: "При покупке любого напитка — второй бесплатно по выходным",
    type: "gift",
    status: "active",
    period: "5 фев — 20 фев",
    channels: ["vk"],
    metricLabel: "Использований",
    metricValue: "132",
    image: "/content/drinks.jpg",
    discount: "2×1",
    uses: 132,
    goal: 200,
    stats: { views: 7340, clicks: 690, daily: [12, 15, 19, 22, 17, 26, 21] },
  },
  {
    id: "pr3",
    title: "День рождения кофейни",
    description: "Праздничное меню, угощения и розыгрыш сертификатов",
    type: "event",
    status: "scheduled",
    period: "1 мар — 3 мар",
    channels: ["vk", "telegram", "instagram"],
    metricLabel: "Использований",
    metricValue: "—",
    image: "/content/interior.jpg",
    discount: "🎂",
    code: "BIRTHDAY",
  },
  {
    id: "pr4",
    title: "Кофе с собой дешевле",
    description: "Скидка на любой напиток навынос по промокоду — весь март",
    type: "code",
    status: "scheduled",
    period: "1 мар — 31 мар",
    channels: ["telegram", "max"],
    metricLabel: "Использований",
    metricValue: "—",
    discount: "−15%",
    code: "TOGO15",
    goal: 400,
  },
  {
    id: "pr5",
    title: "Новогодний глинтвейн",
    description: "Сезонное предложение к праздникам",
    type: "discount",
    status: "finished",
    period: "20 дек — 10 янв",
    channels: ["vk", "telegram"],
    metricLabel: "Использований за акцию",
    metricValue: "1 024",
    image: "/content/newdrink.jpg",
    discount: "−25%",
    uses: 1024,
    goal: 500,
    stats: { views: 41200, clicks: 3860, daily: [64, 88, 121, 143, 156, 172, 148, 132] },
  },
];

export function promoCounts(list: Promo[] = PROMOS) {
  return {
    active: list.filter((p) => p.status === "active").length,
    scheduled: list.filter((p) => p.status === "scheduled").length,
    finished: list.filter((p) => p.status === "finished").length,
  };
}

/** Суммарные использования по всем акциям — для KPI списка. */
export const promoTotalUses = (list: Promo[] = PROMOS) =>
  list.reduce((sum, p) => sum + (p.uses ?? 0), 0);

export const fmtNum = (n: number) => n.toLocaleString("ru-RU");

/** CTR в процентах с одним знаком: клики к показам. */
export function promoCtr(s?: PromoStats) {
  if (!s || !s.views) return null;
  return Math.round((s.clicks / s.views) * 1000) / 10;
}

/** Конверсия: использования к переходам. */
export function promoConversion(p: Promo) {
  if (!p.stats?.clicks || p.uses == null) return null;
  return Math.round((p.uses / p.stats.clicks) * 1000) / 10;
}

export const findPromo = (id: string) => PROMOS.find((p) => p.id === id) ?? null;

/** Процент выполнения цели — null, если цель не задана. */
export function promoProgress(p: Pick<Promo, "uses" | "goal">) {
  if (p.uses == null || !p.goal) return null;
  return Math.min(100, Math.round((p.uses / p.goal) * 100));
}
