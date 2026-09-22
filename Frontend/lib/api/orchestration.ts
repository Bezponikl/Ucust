import { apiFetch } from "./client";
import { endpoints } from "./endpoints";
import type { ChannelId } from "@/lib/channels";
import type {
  AsyncGenerateRequest,
  AsyncGenerateResponse,
  ChannelAnalyzeRequest,
  ChannelAnalysisResponse,
  ChannelSettingsResponse,
  CriticReviewResponse,
  PostResponse,
  SocialVerifyResponse,
  TaskStatusResponse,
  UpdatePostRequest,
} from "./types";

/**
 * Ставит генерацию в очередь. Ответ приходит сразу (202) и содержит только
 * taskId: сам текст появится позже — состояние забирается `getTaskStatus`.
 */
export function generateAsync(req: AsyncGenerateRequest): Promise<AsyncGenerateResponse> {
  return apiFetch<AsyncGenerateResponse>(endpoints.orchestration.generateAsync, {
    method: "POST",
    auth: true,
    body: JSON.stringify(req),
  });
}

/**
 * Генерация с фотографиями: multipart — часть `request` = JSON-параметры,
 * часть `files` = изображения. Бэк сохраняет их в MinIO и передаёт контуру
 * как attachments (Moondream VQA учитывает кадр в тексте поста).
 */
export function generateAsyncWithMedia(
  req: AsyncGenerateRequest,
  files: File[],
): Promise<AsyncGenerateResponse> {
  const form = new FormData();
  form.append("request", new Blob([JSON.stringify(req)], { type: "application/json" }));
  files.forEach((f) => form.append("files", f));
  return apiFetch<AsyncGenerateResponse>(endpoints.orchestration.generateAsync, {
    method: "POST",
    auth: true,
    body: form,
  });
}

export function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  return apiFetch<TaskStatusResponse>(endpoints.orchestration.task(taskId), { auth: true });
}

export interface PollTaskOptions {
  /**
   * Признак того, что ждать больше нечего. Набор статусов в контракте не раскрыт,
   * поэтому решение остаётся за вызывающим — гадать за бэк здесь нельзя.
   */
  isDone: (task: TaskStatusResponse) => boolean;
  /** Пауза между опросами, мс. */
  intervalMs?: number;
  /** Через сколько сдаться, мс. По истечении бросается ошибка. */
  timeoutMs?: number;
  signal?: AbortSignal;
}

/** Опрос задачи до готовности. Бросает Error по таймауту или отмене. */
export async function pollTask(
  taskId: string,
  { isDone, intervalMs = 2000, timeoutMs = 120_000, signal }: PollTaskOptions,
): Promise<TaskStatusResponse> {
  const deadline = Date.now() + timeoutMs;

  for (;;) {
    if (signal?.aborted) throw new Error("Ожидание генерации отменено");

    const task = await getTaskStatus(taskId);
    if (isDone(task)) return task;

    if (Date.now() + intervalMs > deadline) {
      throw new Error("Генерация не завершилась за отведённое время");
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
}

export function getPost(id: string): Promise<PostResponse> {
  return apiFetch<PostResponse>(endpoints.orchestration.post(id), { auth: true });
}

/**
 * Сохраняет отредактированный пост (partial): текст, картинка, хештеги,
 * площадки, время публикации. Бэк обновляет только переданные поля.
 */
export function updatePost(id: string, patch: UpdatePostRequest): Promise<PostResponse> {
  return apiFetch<PostResponse>(endpoints.orchestration.updatePost(id), {
    method: "PATCH",
    auth: true,
    body: JSON.stringify(patch),
  });
}

/**
 * AI-аудит поста критиком Чарли Мангера: возвращает замечания/правки по тексту.
 * Применение правок — отдельным PATCH через `updatePost`.
 */
export function aiReviewPost(id: string): Promise<CriticReviewResponse> {
  return apiFetch<CriticReviewResponse>(endpoints.orchestration.aiReviewPost(id), {
    method: "POST",
    auth: true,
  });
}

export function listProjectPosts(projectId: string): Promise<PostResponse[]> {
  return apiFetch<PostResponse[]>(endpoints.orchestration.projectPosts(projectId), { auth: true });
}

/** Пользователь принял сгенерированный пост — он больше не черновик. */
export function confirmPost(id: string): Promise<PostResponse> {
  return apiFetch<PostResponse>(endpoints.orchestration.confirmPost(id), {
    method: "POST",
    auth: true,
  });
}

export function publishPost(id: string): Promise<PostResponse> {
  return apiFetch<PostResponse>(endpoints.orchestration.publishPost(id), {
    method: "POST",
    auth: true,
  });
}

/**
 * Планирует публикацию: бэк ставит статус SCHEDULED с указанным scheduledAt.
 * Момент времени — ISO-строка с часовым поясом (см. combineDateTime).
 */
export function schedulePost(id: string, scheduledAt: string): Promise<PostResponse> {
  return apiFetch<PostResponse>(endpoints.orchestration.schedulePost(id), {
    method: "POST",
    auth: true,
    body: JSON.stringify({ scheduledAt }),
  });
}

/** «Отложить» — пометить пост как REJECTED (не одобрен, в план не выйдет). */
export function rejectPost(id: string): Promise<PostResponse> {
  return apiFetch<PostResponse>(endpoints.orchestration.rejectPost(id), {
    method: "POST",
    auth: true,
  });
}

/**
 * Проверяет ссылку/канал соцсети (best-effort со стороны бэка). verified=true
 * не гарантирует права публикации — только существование страницы/канала.
 */
export function verifySocial(
  channel: ChannelId,
  reference: string,
): Promise<SocialVerifyResponse> {
  return apiFetch<SocialVerifyResponse>(endpoints.orchestration.socialsVerify, {
    method: "POST",
    auth: true,
    body: JSON.stringify({ channel, reference }),
  });
}

/**
 * Запускает анализ Telegram-канала: бэк дёргает контур (parse_telegram) и
 * импортирует посты канала в контент-план. Ответ приходит синхронно и уже
 * содержит posts/objections, когда контур отвечает быстро.
 */
export function analyzeChannel(req: ChannelAnalyzeRequest): Promise<ChannelAnalysisResponse> {
  return apiFetch<ChannelAnalysisResponse>(endpoints.orchestration.channelAnalyze, {
    method: "POST",
    auth: true,
    body: JSON.stringify(req),
  });
}

/** Состояние анализа канала по его id (для перезагрузки с готовыми постами). */
export function getChannelAnalysis(id: string): Promise<ChannelAnalysisResponse> {
  return apiFetch<ChannelAnalysisResponse>(endpoints.orchestration.channelAnalysisById(id), {
    auth: true,
  });
}

/**
 * Настройки автоскана канала проекта (интервал в часах, момент последнего скана).
 * Доступны только для проектов с привязанным Telegram-каналом — иначе бэк 400.
 */
export function getChannelSettings(projectId: string): Promise<ChannelSettingsResponse> {
  return apiFetch<ChannelSettingsResponse>(endpoints.orchestration.channelSettings(projectId), {
    auth: true,
  });
}

/** Обновляет интервал автоскана канала проекта (часы). */
export function updateChannelSettings(
  projectId: string,
  autoRescanIntervalHours: number,
): Promise<ChannelSettingsResponse> {
  return apiFetch<ChannelSettingsResponse>(endpoints.orchestration.channelSettings(projectId), {
    method: "PUT",
    auth: true,
    body: JSON.stringify({ autoRescanIntervalHours }),
  });
}
