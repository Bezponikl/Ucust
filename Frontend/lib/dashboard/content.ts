import type { ChannelId } from "@/lib/channels";
import type { PostStatus } from "./types";

// Типы контента на MVP: публикация, акция, видео.
// Отзывы — это НЕ контент, они живут в разделе «Отзывы».
export type PostType = "post" | "promo" | "video";

export interface Post {
  id: string;
  day: number; // день месяца (1..28) — мок-месяц Февраль 2026, Пн-старт
  title: string;
  excerpt: string; // текст-превью поста
  image?: string; // обложка из /public/content (у черновиков может не быть)
  channels: ChannelId[];
  status: PostStatus;
  type: PostType;
  time: string; // "10:00"
}

export const MONTH_LABEL = "Февраль 2026";
export const WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"] as const;
export const DAYS_IN_MONTH = 28; // Февраль 2026, Пн-старт → ровно 4 недели

export const POSTS: Post[] = [
  { id: "p1", day: 1, title: "Доброе утро понедельника", excerpt: "Начинаем неделю с ароматного эспрессо и тёплой атмосферы. Заходите на чашечку!", image: "/content/interior.jpg", channels: ["vk", "telegram"], status: "published", type: "video", time: "08:30" },
  { id: "p2", day: 2, title: "Зимнее меню напитков", excerpt: "Согревающие напитки сезона — пряный латте, какао с маршмеллоу и облепиховый чай.", image: "/content/drinks.jpg", channels: ["vk", "telegram"], status: "published", type: "promo", time: "10:00" },
  { id: "p3", day: 3, title: "Знакомство с бариста", excerpt: "Знакомьтесь с Аней — она готовит вашу утреннюю чашку с 8:00 каждый день.", image: "/content/barista.jpg", channels: ["telegram"], status: "scheduled", type: "post", time: "12:00" },
  { id: "p5", day: 5, title: "Момент дня: латте-арт", excerpt: "Немного магии в кадре — как рождается рисунок на молочной пенке.", image: "/content/latteart.jpg", channels: ["vk"], status: "published", type: "video", time: "16:00" },
  { id: "p6", day: 6, title: "Идеи на выходные", excerpt: "Собрали уютные идеи, куда заглянуть в выходные с друзьями за чашкой кофе.", image: "/content/newdrink.jpg", channels: ["vk", "telegram"], status: "published", type: "post", time: "11:00" },
  { id: "p9", day: 9, title: "Акция «Счастливые часы»", excerpt: "Каждый будний день с 15:00 до 17:00 — второй напиток в подарок.", image: "/content/latteart.jpg", channels: ["vk"], status: "published", type: "promo", time: "08:00" },
  { id: "p10", day: 10, title: "Скоро — обновлённое меню", excerpt: "Готовим большое обновление: новые напитки и сезонные десерты. Следите за анонсом.", image: "/content/interior.jpg", channels: ["vk", "telegram"], status: "scheduled", type: "post", time: "14:00" },
  { id: "p12", day: 12, title: "Новинка недели — фисташковый раф", excerpt: "Пробуем новинку недели — фисташковый раф. Уже в меню, приходите за впечатлением.", image: "/content/drinks.jpg", channels: ["vk"], status: "scheduled", type: "post", time: "13:00" },
  { id: "p13", day: 13, title: "История нашего кофе", excerpt: "От зерна до чашки: рассказываем, откуда приезжает наш кофе и как мы его обжариваем.", image: "/content/beans.jpg", channels: ["vk", "telegram"], status: "scheduled", type: "post", time: "10:30" },
  { id: "p14", day: 14, title: "Пост ко Дню влюблённых", excerpt: "14 февраля дарим комплимент каждой паре — приходите вдвоём за тёплым моментом.", image: "/content/pastry.jpg", channels: ["vk", "telegram"], status: "scheduled", type: "post", time: "09:00" },
  { id: "p16", day: 16, title: "Идея поста", excerpt: "Идея: короткий пост о том, как выбрать напиток под настроение дня.", channels: [], status: "draft", type: "post", time: "—" },
  { id: "p18", day: 18, title: "Бэкстейдж кухни", excerpt: "Как мы готовим свежую выпечку каждое утро — короткая история в кадре.", image: "/content/pastry.jpg", channels: ["vk", "telegram"], status: "scheduled", type: "video", time: "09:30" },
  { id: "p21", day: 21, title: "Гайд по напиткам", excerpt: "Капучино, флэт-уайт, раф — объясняем разницу простыми словами.", image: "/content/newdrink.jpg", channels: ["vk", "telegram"], status: "scheduled", type: "post", time: "12:00" },
  { id: "p24", day: 24, title: "Кофе с собой −15%", excerpt: "Всю неделю — скидка 15% на любой напиток навынос. Успейте зарядиться бодростью!", image: "/content/barista.jpg", channels: ["vk", "telegram"], status: "scheduled", type: "promo", time: "08:30" },
  { id: "p26", day: 26, title: "Акция выходного дня", excerpt: "Суббота и воскресенье — скидка 20% на всю свежую выпечку.", image: "/content/latteart.jpg", channels: ["vk", "telegram"], status: "scheduled", type: "promo", time: "10:00" },
  { id: "p27", day: 27, title: "Анонс новинок", excerpt: "Скоро в меню: сезонные десерты и авторские напитки. Не пропустите анонс.", image: "/content/interior.jpg", channels: ["vk", "telegram"], status: "scheduled", type: "post", time: "11:30" },
];

export function postsByDay(): Map<number, Post[]> {
  const map = new Map<number, Post[]>();
  for (const p of POSTS) {
    const arr = map.get(p.day) ?? [];
    arr.push(p);
    map.set(p.day, arr);
  }
  return map;
}

export const STATUS_LABEL: Record<PostStatus, string> = {
  published: "Опубликован",
  scheduled: "Запланирован",
  draft: "Черновик",
  none: "—",
};
