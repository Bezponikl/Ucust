import type { BrandProfile } from "@/lib/onboarding/types";
import type { DashboardData } from "./types";

/**
 * Данные обзора дашборда. Мок: статы/график/рекомендации локальные, имя и часть
 * подсказок приправлены «мозгом бренда». ПОЗЖЕ заменяется на fetch к API — меняется
 * только тело этой функции.
 */
export function getDashboardData(profile: BrandProfile | null): DashboardData {
  const businessName = profile?.name?.trim() || "Ваш бизнес";
  const firstService = profile?.services?.[0]?.title ?? "новинке";
  const firstGoal = profile?.goals?.[0] ?? "Привлечь новых клиентов";

  return {
    businessName,
    stats: [
      { id: "views", label: "Просмотры", value: "12.5K", hint: "За последнюю неделю", delta: "+18%", icon: "views", color: "brand" },
      { id: "engagement", label: "Вовлечённость", value: "+24%", hint: "За последний месяц", icon: "engagement", color: "success" },
      { id: "subscribers", label: "Новые подписчики", value: "+127", hint: "За последнюю неделю", icon: "subscribers", color: "purple" },
      { id: "reviews", label: "Отзывы", value: "47", hint: "Требуют внимания", icon: "reviews", color: "orange" },
    ],
    chart: {
      reach: [20, 35, 28, 42, 55, 48, 62, 58, 70, 65, 78, 92],
      engagement: [10, 18, 16, 24, 30, 26, 34, 38, 33, 44, 40, 52],
      clicks: [5, 9, 7, 14, 12, 20, 18, 24, 22, 30, 28, 36],
    },
    tips: [
      {
        id: "post",
        title: `Создать пост о ${firstService.toLowerCase()}`,
        text: "Подписчики спрашивают про новинки — хороший повод для поста.",
        color: "pink",
        href: "/dashboard/create",
      },
      {
        id: "reviews",
        title: "Ответить на 3 новых отзыва",
        text: "Гости ждут вашего ответа — это повышает доверие.",
        color: "orange",
        href: "/dashboard/reviews",
      },
      {
        id: "promo",
        title: "Запустить акцию «Счастливые часы»",
        text: `Цель «${firstGoal.toLowerCase()}» — акция поможет её достичь.`,
        color: "brand",
        href: "/dashboard/promos",
      },
    ],
    week: [
      { weekday: "Пн", day: 1, status: "published", channels: ["vk", "telegram"] },
      { weekday: "Вт", day: 2, status: "published", channels: ["vk"] },
      { weekday: "Ср", day: 3, status: "scheduled", channels: ["telegram"] },
      { weekday: "Чт", day: 4, status: "scheduled", channels: ["vk", "telegram"] },
      { weekday: "Пт", day: 5, status: "draft", channels: [] },
      { weekday: "Сб", day: 6, status: "scheduled", channels: ["vk"] },
      { weekday: "Вс", day: 7, status: "none", channels: [] },
    ],
    activity: [
      { id: "a1", text: "Опубликован пост «Летняя акция»", time: "2 часа назад", color: "success" },
      { id: "a2", text: "Новый отзыв от Марии К.", time: "3 часа назад", color: "orange" },
      { id: "a3", text: "Запущена акция «День рождения»", time: "5 часов назад", color: "pink" },
    ],
  };
}
