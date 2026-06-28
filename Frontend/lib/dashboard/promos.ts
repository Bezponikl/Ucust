import type { ChannelId } from "@/lib/channels";

export type PromoStatus = "active" | "scheduled" | "finished";

export interface Promo {
  id: string;
  title: string;
  description: string;
  status: PromoStatus;
  period: string;
  channels: ChannelId[];
  metricLabel: string;
  metricValue: string;
}

export const PROMO_STATUS_LABEL: Record<PromoStatus, string> = {
  active: "Активна",
  scheduled: "Запланирована",
  finished: "Завершена",
};

export const PROMOS: Promo[] = [
  {
    id: "pr1",
    title: "Счастливые часы",
    description: "−20% на все напитки с 15:00 до 17:00 по будням",
    status: "active",
    period: "1 фев — 28 фев",
    channels: ["vk", "telegram"],
    metricLabel: "Использований",
    metricValue: "248",
  },
  {
    id: "pr2",
    title: "Второй кофе в подарок",
    description: "При покупке любого напитка — второй бесплатно по выходным",
    status: "active",
    period: "5 фев — 20 фев",
    channels: ["vk"],
    metricLabel: "Использований",
    metricValue: "132",
  },
  {
    id: "pr3",
    title: "День рождения кофейни",
    description: "Праздничное меню и розыгрыш сертификатов",
    status: "scheduled",
    period: "1 мар — 3 мар",
    channels: ["vk", "telegram", "instagram"],
    metricLabel: "Охват анонса",
    metricValue: "—",
  },
  {
    id: "pr4",
    title: "Новогодний глинтвейн",
    description: "Сезонное предложение к праздникам",
    status: "finished",
    period: "20 дек — 10 янв",
    channels: ["vk", "telegram"],
    metricLabel: "Использований",
    metricValue: "1 024",
  },
];

export function promoCounts() {
  return {
    active: PROMOS.filter((p) => p.status === "active").length,
    scheduled: PROMOS.filter((p) => p.status === "scheduled").length,
    finished: PROMOS.filter((p) => p.status === "finished").length,
  };
}
