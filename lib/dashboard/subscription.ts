export type TariffAccent = "blue" | "gradient" | "purple";

export interface TariffPlan {
  id: string;
  name: string;
  price: number;
  tagline: string;
  features: string[];
  accent: TariffAccent;
  highlighted: boolean;
  maxProjects: number;
  maxPosts: number;
}

export const TARIFF_PLANS: TariffPlan[] = [
  {
    id: "start",
    name: "Старт",
    price: 1500,
    tagline: "Для одного бизнеса.",
    accent: "blue",
    highlighted: false,
    maxProjects: 1,
    maxPosts: 12,
    features: [
      "1 бизнес",
      "До 12 постов в месяц",
      "Все соцсети без ограничений",
      "Генерация фото",
      "Посты по контент-плану",
      "Базовая аналитика",
      "Email-поддержка",
    ],
  },
  {
    id: "business",
    name: "Бизнес",
    price: 3500,
    tagline: "Для регулярного ведения.",
    accent: "gradient",
    highlighted: true,
    maxProjects: 3,
    maxPosts: 30,
    features: [
      "3 бизнеса",
      "До 30 постов в месяц",
      "Все соцсети без ограничений",
      "Генерация фото и видео",
      "Генерация постов по запросу",
      "Расширенная аналитика",
      "Приоритетная поддержка",
    ],
  },
];

export interface CurrentSubscription {
  planId: string;
  renewsOn: string;
  status: "active" | "cancelled";
  usedProjects: number;
  usedPosts: number;
}

export const CURRENT_SUBSCRIPTION: CurrentSubscription = {
  planId: "business",
  renewsOn: "11 августа 2026",
  status: "active",
  usedProjects: 2,
  usedPosts: 21,
};

export interface PaymentRecord {
  id: string;
  date: string;
  plan: string;
  amount: number;
  status: "Оплачено" | "Отменено";
}

export const PAYMENT_HISTORY: PaymentRecord[] = [
  { id: "p1", date: "11 июля 2026", plan: "Бизнес", amount: 3500, status: "Оплачено" },
  { id: "p2", date: "11 июня 2026", plan: "Бизнес", amount: 3500, status: "Оплачено" },
  { id: "p3", date: "11 мая 2026", plan: "Старт", amount: 1500, status: "Оплачено" },
];
