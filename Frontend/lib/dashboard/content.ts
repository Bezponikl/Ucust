import type { ChannelId } from "@/lib/channels";
import { CUR_MONTH, CUR_YEAR, MONTHS_GEN, MONTHS_NOM, daysInMonth, firstWeekdayMon, pad2 } from "./date";
import type { PostStatus } from "./types";

// Типы контента на MVP: публикация, акция, видео.
// Отзывы — это НЕ контент, они живут в разделе «Отзывы».
export type PostType = "post" | "promo" | "video";

export interface Post {
  id: string;
  day: number; // день текущего месяца (1..DAYS_IN_MONTH), Пн-старт
  title: string;
  excerpt: string; // текст-превью поста
  image?: string; // обложка из /public/content (у черновиков может не быть)
  channels: ChannelId[];
  status: PostStatus;
  type: PostType;
  time: string; // "10:00"
}

/** План контента — живой календарь текущего месяца, а не фиксированный мок. */
export const MONTH_LABEL = `${MONTHS_NOM[CUR_MONTH]} ${CUR_YEAR}`;
export const MONTH_GEN = MONTHS_GEN[CUR_MONTH]; // «сентября» для подписей «на 15 сентября»
export const MONTH_DD = pad2(CUR_MONTH + 1); // «09» для дат вида «15.09.2026»
export const YEAR = CUR_YEAR;
export const DAYS_IN_MONTH = daysInMonth(CUR_YEAR, CUR_MONTH);
/** Сдвиг первого дня (Пн-старт): 0 = понедельник — выравнивает календарь. */
export const MONTH_OFFSET = firstWeekdayMon(CUR_YEAR, CUR_MONTH);
export const WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"] as const;
export const DAYS_PER_WEEK = WEEKDAYS.length;

export const POSTS: Post[] = [];

/** Посты проекта по дням месяца. Демо-данных больше нет: пустой список = пустой план. */
export function postsByDay(list: Post[]): Map<number, Post[]> {
  const map = new Map<number, Post[]>();
  for (const p of list) {
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
