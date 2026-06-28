export type ReviewPlatform = "2gis" | "yandex" | "google";

export interface Review {
  id: string;
  author: string;
  rating: number; // 1..5
  platform: ReviewPlatform;
  date: string;
  text: string;
  reply: string | null; // ответ бизнеса, если есть
  aiDraft: string; // черновик ответа от AI
}

export const PLATFORM_LABEL: Record<ReviewPlatform, string> = {
  "2gis": "2ГИС",
  yandex: "Яндекс",
  google: "Google",
};

export const REVIEWS: Review[] = [
  {
    id: "r1",
    author: "Мария К.",
    rating: 5,
    platform: "yandex",
    date: "сегодня",
    text: "Лучший раф в городе! Уютно, быстро обслужили, бариста посоветовал отличную выпечку. Обязательно вернусь.",
    reply: null,
    aiDraft: "Мария, спасибо за тёплые слова! Очень рады, что вам понравились и раф, и выпечка. Будем ждать вас снова — приготовим что-нибудь особенное ☕",
  },
  {
    id: "r2",
    author: "Андрей П.",
    rating: 4,
    platform: "2gis",
    date: "вчера",
    text: "Кофе вкусный, но в час пик долго ждал заказ. В остальном всё отлично.",
    reply: null,
    aiDraft: "Андрей, спасибо за отзыв! Работаем над скоростью в часы пик, чтобы вы не ждали. Рады, что кофе пришёлся по вкусу — до встречи!",
  },
  {
    id: "r3",
    author: "Елена С.",
    rating: 5,
    platform: "google",
    date: "2 дня назад",
    text: "Атмосферное место, приятная музыка и вежливый персонал. Беру кофе с собой каждое утро.",
    reply: "Елена, спасибо! Нам очень приятно быть частью вашего утра. Хорошего дня!",
    aiDraft: "",
  },
  {
    id: "r4",
    author: "Дмитрий В.",
    rating: 3,
    platform: "yandex",
    date: "3 дня назад",
    text: "Неплохо, но цены чуть выше среднего. Качество соответствует, но хотелось бы программу лояльности.",
    reply: null,
    aiDraft: "Дмитрий, спасибо за честный отзыв! Хорошая новость: мы как раз запускаем программу лояльности — будет приятнее возвращаться. Заходите!",
  },
];

export function reviewStats() {
  const total = REVIEWS.length;
  const avg = total ? REVIEWS.reduce((s, r) => s + r.rating, 0) / total : 0;
  const unanswered = REVIEWS.filter((r) => !r.reply).length;
  return { total, avg: avg.toFixed(1), unanswered };
}
