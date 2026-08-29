import type { ChannelId } from "@/lib/channels";
import { CHANNEL_ORDER } from "@/lib/channels";
import type { Post, PostType } from "@/lib/dashboard/content";
import type { PostStatus } from "@/lib/dashboard/types";
import type { PostResponse, TaskStatusResponse } from "./types";

/**
 * Оркестратор отдаёт посты и статусы задач, но контракт их полей не раскрывает.
 * Всё чтение собрано здесь: ищем значение среди знакомых имён и мягко
 * деградируем, если поля нет. Когда бэк опубликует DTO, правится этот файл,
 * а экраны остаются как есть.
 */

function pickString(source: Record<string, unknown>, keys: string[]): string | null {
  for (const key of keys) {
    const value = source[key];
    if (typeof value === "string" && value.trim()) return value;
  }
  return null;
}

/** Статусы, после которых опрашивать задачу больше нет смысла. */
const TERMINAL = new Set([
  "DONE",
  "SUCCESS",
  "SUCCEEDED",
  "COMPLETED",
  "FINISHED",
  "READY",
  "FAILED",
  "ERROR",
  "CANCELLED",
  "CANCELED",
  "REJECTED",
]);

const FAILED = new Set(["FAILED", "ERROR", "CANCELLED", "CANCELED", "REJECTED"]);

export function isTaskFinished(task: TaskStatusResponse): boolean {
  const status = (task.status ?? "").toUpperCase();
  // Результат в теле важнее статуса: если текст уже пришёл, ждать нечего.
  return TERMINAL.has(status) || taskText(task) !== null;
}

export function isTaskFailed(task: TaskStatusResponse): boolean {
  return FAILED.has((task.status ?? "").toUpperCase()) && taskText(task) === null;
}

/** Текст поста из ответа задачи. null — сервер результата ещё не положил. */
export function taskText(task: TaskStatusResponse): string | null {
  const raw = task as Record<string, unknown>;
  const direct = pickString(raw, ["text", "content", "result", "body", "generatedText"]);
  if (direct) return direct;

  const nested = (raw.post ?? raw.result ?? raw.data) as Record<string, unknown> | undefined;
  if (nested && typeof nested === "object") {
    const fromNested = pickString(nested, ["text", "content", "body"]);
    if (fromNested) return fromNested;
  }

  const list = (raw.posts ?? raw.results ?? raw.items) as unknown;
  if (Array.isArray(list) && list.length > 0 && typeof list[0] === "object" && list[0]) {
    return pickString(list[0] as Record<string, unknown>, ["text", "content", "body"]);
  }
  return null;
}

/** id созданного поста — нужен, чтобы потом его подтвердить и опубликовать. */
export function taskPostId(task: TaskStatusResponse): string | null {
  const raw = task as Record<string, unknown>;
  const direct = pickString(raw, ["postId", "createdPostId"]);
  if (direct) return direct;

  const nested = (raw.post ?? raw.result ?? raw.data) as Record<string, unknown> | undefined;
  if (nested && typeof nested === "object") {
    const id = pickString(nested, ["id", "postId"]);
    if (id) return id;
  }

  const list = (raw.posts ?? raw.results ?? raw.items) as unknown;
  if (Array.isArray(list) && list.length > 0 && typeof list[0] === "object" && list[0]) {
    return pickString(list[0] as Record<string, unknown>, ["id", "postId"]);
  }
  return null;
}

const STATUS_MAP: Record<string, PostStatus> = {
  PUBLISHED: "published",
  POSTED: "published",
  SENT: "published",
  SCHEDULED: "scheduled",
  PLANNED: "scheduled",
  CONFIRMED: "scheduled",
  APPROVED: "scheduled",
  DRAFT: "draft",
  NEW: "draft",
  CREATED: "draft",
  GENERATED: "draft",
};

export function postStatus(post: PostResponse): PostStatus {
  const raw = post as Record<string, unknown>;
  const value = pickString(raw, ["status", "state"]);
  return value ? STATUS_MAP[value.toUpperCase()] ?? "draft" : "draft";
}

function postType(post: PostResponse): PostType {
  const raw = post as Record<string, unknown>;
  const value = (pickString(raw, ["type", "mode", "kind", "contentType"]) ?? "").toUpperCase();
  if (value.includes("VIDEO")) return "video";
  if (value.includes("PROMO") || value.includes("ACTION")) return "promo";
  return "post";
}

function postChannels(post: PostResponse): ChannelId[] {
  const raw = post as Record<string, unknown>;
  const value = raw.channels ?? raw.socialNetworks ?? raw.platforms;
  if (!Array.isArray(value)) return [];

  return value
    .map((item) => (typeof item === "string" ? item.toLowerCase() : ""))
    .filter((id): id is ChannelId => (CHANNEL_ORDER as readonly string[]).includes(id));
}

/** Дата публикации: сначала запланированная, иначе дата создания. */
function postDate(post: PostResponse): Date | null {
  const raw = post as Record<string, unknown>;
  const value = pickString(raw, [
    "scheduledAt",
    "publishAt",
    "publishedAt",
    "plannedAt",
    "createdAt",
    "date",
  ]);
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** Пост бэка в вид, который рисует календарь и лента контента. */
export function toDashboardPost(post: PostResponse): Post {
  const raw = post as Record<string, unknown>;
  const text = pickString(raw, ["text", "content", "body"]) ?? "";
  const title =
    pickString(raw, ["title", "heading", "name"]) ??
    text.split("\n").find((line) => line.trim())?.slice(0, 60) ??
    "Без названия";
  const date = postDate(post);

  return {
    id: post.id,
    day: date ? date.getDate() : 1,
    title,
    excerpt: text.slice(0, 240),
    image: pickString(raw, ["imageUrl", "image", "mediaUrl", "coverUrl"]) ?? undefined,
    channels: postChannels(post),
    status: postStatus(post),
    type: postType(post),
    time: date
      ? date.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })
      : "—",
  };
}
