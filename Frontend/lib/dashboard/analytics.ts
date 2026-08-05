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

export const PERIODS = ["7 дней", "30 дней", "90 дней"] as const;
