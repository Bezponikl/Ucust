import type { ChannelId } from "@/lib/channels";
import type { AccentColor, ChartTab } from "./types";
import type { IconName } from "@/lib/icons/solar";

export interface MetricCard {
  id: string;
  label: string;
  value: string;
  delta: string;
  color: AccentColor;
  icon: IconName;
}

export interface ChannelShare {
  id: ChannelId;
  value: number; // процент охвата
}

export interface TopPost {
  id: string;
  title: string;
  date: string;
  views: string;
  likes: string;
  er: string; // вовлечённость, %
}

/** Пост в разрезе одной площадки — то, что раскрывается по клику на канал. */
export interface ChannelPost {
  id: string;
  title: string;
  date: string;
  views: number;
  reposts: number;
  likes: number;
}

export const ANALYTICS_CHART: Record<ChartTab, number[]> = {
  reach: [32, 40, 38, 52, 60, 55, 68, 72, 65, 80, 76, 95, 88, 102],
  engagement: [12, 18, 15, 22, 28, 24, 30, 34, 31, 38, 36, 44, 42, 50],
  clicks: [6, 10, 8, 14, 16, 13, 20, 22, 19, 26, 24, 30, 28, 35],
};

export const METRICS: MetricCard[] = [
  { id: "reach", label: "Охват", value: "48.2K", delta: "+22%", color: "brand", icon: "eye" },
  { id: "engagement", label: "Реакции", value: "42.4K", delta: "+16%", color: "success", icon: "heart" },
  { id: "subscribers", label: "Подписчики", value: "3 412", delta: "+127", color: "purple", icon: "user-plus" },
  { id: "clicks", label: "Клики", value: "1 980", delta: "+18%", color: "orange", icon: "trending" },
];

export const CHANNEL_SHARE: ChannelShare[] = [
  { id: "vk", value: 42 },
  { id: "telegram", value: 28 },
  { id: "instagram", value: 18 },
  { id: "ok", value: 12 },
];

export const TOP_POSTS: TopPost[] = [
  { id: "t1", title: "Зимнее меню напитков", date: "2 фев", views: "8.1K", likes: "642", er: "9.2%" },
  { id: "t2", title: "Акция «Счастливые часы»", date: "9 фев", views: "6.7K", likes: "510", er: "8.1%" },
  { id: "t3", title: "История нашего кофе", date: "13 фев", views: "5.3K", likes: "388", er: "7.4%" },
  { id: "t4", title: "Идеи на выходные", date: "6 фев", views: "4.9K", likes: "301", er: "6.8%" },
];

/** Худшие публикации периода — обратная сторона топа, показывает, что не зашло. */
export const WORST_POSTS: TopPost[] = [
  { id: "w1", title: "Мы обновили режим работы", date: "11 фев", views: "420", likes: "9", er: "0.6%" },
  { id: "w2", title: "Репост партнёрской новости", date: "4 фев", views: "610", likes: "14", er: "0.9%" },
  { id: "w3", title: "Опрос про новый сироп", date: "15 фев", views: "780", likes: "23", er: "1.4%" },
  { id: "w4", title: "Фото витрины без подписи", date: "8 фев", views: "950", likes: "31", er: "1.8%" },
];

/** Публикации по площадкам: раскрываются при клике на канал в разбивке охвата. */
// Partial: у площадок без публикаций строки просто нет — не заводим пустые заглушки
// под каждый канал из справочника.
export const CHANNEL_POSTS: Partial<Record<ChannelId, ChannelPost[]>> = {
  vk: [
    { id: "vk1", title: "Зимнее меню напитков", date: "2 фев", views: 4120, reposts: 86, likes: 312 },
    { id: "vk2", title: "Акция «Счастливые часы»", date: "9 фев", views: 3180, reposts: 64, likes: 241 },
    { id: "vk3", title: "История нашего кофе", date: "13 фев", views: 2260, reposts: 31, likes: 158 },
  ],
  telegram: [
    { id: "tg1", title: "Зимнее меню напитков", date: "2 фев", views: 2480, reposts: 112, likes: 168 },
    { id: "tg2", title: "Идеи на выходные", date: "6 фев", views: 1740, reposts: 47, likes: 96 },
    { id: "tg3", title: "Акция «Счастливые часы»", date: "9 фев", views: 1520, reposts: 39, likes: 88 },
  ],
  instagram: [
    { id: "ig1", title: "Латте-арт крупным планом", date: "5 фев", views: 1980, reposts: 24, likes: 274 },
    { id: "ig2", title: "Бариста за работой", date: "12 фев", views: 1310, reposts: 12, likes: 186 },
  ],
  ok: [
    { id: "ok1", title: "Зимнее меню напитков", date: "2 фев", views: 940, reposts: 18, likes: 71 },
    { id: "ok2", title: "История нашего кофе", date: "13 фев", views: 620, reposts: 9, likes: 44 },
  ],
};

export const PERIODS = ["7 дней", "30 дней", "90 дней"] as const;
