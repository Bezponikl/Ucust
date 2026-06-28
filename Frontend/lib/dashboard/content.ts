import type { ChannelId } from "@/lib/channels";
import type { PostStatus } from "./types";

export type PostType = "post" | "promo" | "review";

export interface Post {
  id: string;
  day: number; // день месяца (1..28) — мок-месяц Февраль 2026, Пн-старт
  title: string;
  channels: ChannelId[];
  status: PostStatus;
  type: PostType;
  time: string; // "10:00"
}

export const MONTH_LABEL = "Февраль 2026";
export const WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"] as const;
export const DAYS_IN_MONTH = 28; // Февраль 2026, Пн-старт → ровно 4 недели

export const POSTS: Post[] = [
  { id: "p2", day: 2, title: "Зимнее меню напитков", channels: ["vk", "telegram"], status: "published", type: "promo", time: "10:00" },
  { id: "p3", day: 3, title: "Знакомство с бариста", channels: ["telegram"], status: "scheduled", type: "post", time: "12:00" },
  { id: "p4", day: 4, title: "Ответ на отзыв", channels: [], status: "scheduled", type: "review", time: "09:30" },
  { id: "p6", day: 6, title: "Идеи на выходные", channels: ["vk", "telegram"], status: "published", type: "post", time: "11:00" },
  { id: "p9", day: 9, title: "Акция «Счастливые часы»", channels: ["vk"], status: "published", type: "promo", time: "08:00" },
  { id: "p11", day: 11, title: "Черновик ответа гостю", channels: [], status: "draft", type: "review", time: "—" },
  { id: "p12", day: 12, title: "Новинка недели", channels: ["vk"], status: "scheduled", type: "post", time: "13:00" },
  { id: "p13", day: 13, title: "История нашего кофе", channels: ["vk", "telegram"], status: "scheduled", type: "post", time: "10:30" },
  { id: "p14", day: 14, title: "Пост ко Дню влюблённых", channels: ["vk", "telegram"], status: "scheduled", type: "post", time: "09:00" },
  { id: "p16", day: 16, title: "Идея поста", channels: [], status: "draft", type: "post", time: "—" },
  { id: "p21", day: 21, title: "Гайд по напиткам", channels: ["vk", "telegram"], status: "scheduled", type: "post", time: "12:00" },
  { id: "p23", day: 23, title: "Ответ на отзыв", channels: [], status: "scheduled", type: "review", time: "15:00" },
  { id: "p26", day: 26, title: "Акция выходного дня", channels: ["vk", "telegram"], status: "scheduled", type: "promo", time: "10:00" },
  { id: "p27", day: 27, title: "Анонс новинок", channels: ["vk", "telegram"], status: "scheduled", type: "post", time: "11:30" },
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
