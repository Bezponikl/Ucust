import type { ChannelId } from "@/lib/channels";
import { REVIEWS, PLATFORM_LABEL } from "./reviews";

export type InboxKind = "message" | "comment" | "review";

export interface ChatMessage {
  from: "them" | "me";
  text: string;
  time: string;
}

export interface InboxItem {
  id: string;
  kind: InboxKind;
  author: string;
  avatar?: string;
  sourceLabel: string; // «VK», «Telegram», «Яндекс»…
  channel?: ChannelId; // для соцсетей — чтобы показать иконку
  rating?: number; // для отзывов, 1..5
  time: string;
  text: string; // обращение клиента
  context?: string; // напр. заголовок поста, к которому коммент
  aiDraft: string; // предложенный ИИ ответ
  answered: boolean;
  sentReply?: string; // уже отправленный ответ
  thread?: ChatMessage[]; // история переписки (для сообщений — VK-подобный чат)
}

export const KIND_LABEL: Record<InboxKind, string> = {
  message: "Сообщения",
  comment: "Комментарии",
  review: "Отзывы",
};

const MESSAGES: InboxItem[] = [
  {
    id: "m1", kind: "message", author: "Ольга М.", avatar: "/content/avatars/olga-m.jpg", sourceLabel: "VK", channel: "vk",
    time: "5 мин назад",
    text: "Здравствуйте! Работаете сегодня до скольки? Хочу зайти после 20:00.",
    aiDraft: "Здравствуйте, Ольга! Сегодня мы работаем до 22:00 — будем рады видеть вас после 20:00 ☕",
    answered: false,
    thread: [
      { from: "them", text: "Здравствуйте! А у вас есть парковка рядом?", time: "вчера, 18:20" },
      { from: "me", text: "Здравствуйте, Ольга! Да, прямо у входа небольшая парковка 🚗", time: "вчера, 18:24" },
      { from: "them", text: "Отлично, спасибо!", time: "вчера, 18:25" },
      { from: "them", text: "Здравствуйте! Работаете сегодня до скольки? Хочу зайти после 20:00.", time: "5 мин назад" },
    ],
  },
  {
    id: "m2", kind: "message", author: "Иван Т.", avatar: "/content/avatars/ivan-t.jpg", sourceLabel: "Telegram", channel: "telegram",
    time: "40 мин назад",
    text: "Можно забронировать столик на двоих на завтра в 12?",
    aiDraft: "Иван, конечно! Забронировали для вас столик на двоих завтра на 12:00. Если планы изменятся — просто напишите 🙌",
    answered: false,
  },
  {
    id: "m3", kind: "message", author: "Пётр Л.", avatar: "/content/avatars/petr-l.jpg", sourceLabel: "Одноклассники", channel: "ok",
    time: "вчера",
    text: "Спасибо за вкусный кофе, как всегда на высоте!",
    aiDraft: "Пётр, спасибо вам! Очень приятно, ждём снова ❤️",
    answered: true,
    sentReply: "Пётр, спасибо вам! Очень приятно, ждём снова ❤️",
  },
];

const COMMENTS: InboxItem[] = [
  {
    id: "c1", kind: "comment", author: "Светлана Р.", avatar: "/content/avatars/svetlana-r.jpg", sourceLabel: "VK", channel: "vk",
    time: "15 мин назад", context: "Пост «Новинка — фисташковый раф»",
    text: "А безлактозное молоко есть? Очень хочется попробовать 😍",
    aiDraft: "Светлана, да! У нас есть овсяное, миндальное и кокосовое молоко — фисташковый раф на любом из них будет великолепен 🌿",
    answered: false,
  },
  {
    id: "c2", kind: "comment", author: "Максим Д.", avatar: "/content/avatars/maxim-d.jpg", sourceLabel: "Telegram", channel: "telegram",
    time: "2 ч назад", context: "Пост «Акция: счастливые часы»",
    text: "А акция на выходных тоже действует?",
    aiDraft: "Максим, «счастливые часы» действуют по будням с 15:00 до 17:00. На выходных ждём вас с другими приятными сюрпризами 😉",
    answered: false,
  },
];

// Отзывы переиспользуем из reviews.ts, приводя к единой модели inbox.
const REVIEW_ITEMS: InboxItem[] = REVIEWS.map((r) => ({
  id: r.id,
  kind: "review" as const,
  author: r.author,
  avatar: r.avatar,
  sourceLabel: PLATFORM_LABEL[r.platform],
  rating: r.rating,
  time: r.date,
  text: r.text,
  aiDraft: r.aiDraft,
  answered: r.reply !== null,
  sentReply: r.reply ?? undefined,
}));

export const INBOX: InboxItem[] = [
  MESSAGES[0], COMMENTS[0], MESSAGES[1], COMMENTS[1], REVIEW_ITEMS[0], REVIEW_ITEMS[1],
  MESSAGES[2], REVIEW_ITEMS[2], REVIEW_ITEMS[3],
];

export function inboxCounts() {
  const needReply = INBOX.filter((i) => !i.answered).length;
  const byKind = (k: InboxKind) => INBOX.filter((i) => i.kind === k && !i.answered).length;
  return {
    all: needReply,
    message: byKind("message"),
    comment: byKind("comment"),
    review: byKind("review"),
  };
}

/**
 * Переписка, которую ИИ обязан учесть при составлении ответа.
 * Для отзыва или комментария это одно обращение, для чата — вся история.
 */
export function threadContext(item: InboxItem): ChatMessage[] {
  return item.thread ?? [{ from: "them", text: item.text, time: item.time }];
}

/**
 * Черновик ответа по ВСЕЙ переписке, а не по одной последней реплике.
 *
 * Раньше автоответ смотрел только на `item.text` — последнее сообщение — и
 * поэтому терял то, о чём уже договорились выше: здоровался заново и повторял
 * уже данные ответы. Здесь на вход идёт весь диалог; `used` — сколько сообщений
 * учтено, это же число показываем в интерфейсе.
 *
 * Это шов под реальный вызов сервиса: туда уйдёт `threadContext(item)` целиком.
 */
export function buildAiDraft(item: InboxItem): { text: string; used: number } {
  const ctx = threadContext(item);
  const used = ctx.length;

  // Continuity: если мы уже отвечали в этом диалоге, второе приветствие лишнее.
  const weReplied = ctx.some((m) => m.from === "me");
  if (!weReplied) return { text: item.aiDraft, used };

  const withoutGreeting = item.aiDraft.replace(
    /^(Здравствуйте|Добрый день|Привет)[,!]?\s*[^,!]*[,!]?\s*/iu,
    "",
  );
  const body = withoutGreeting.charAt(0).toUpperCase() + withoutGreeting.slice(1);
  return { text: body || item.aiDraft, used };
}
