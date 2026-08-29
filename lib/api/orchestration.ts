import { apiFetch } from "./client";
import { endpoints } from "./endpoints";
import type {
  AsyncGenerateRequest,
  AsyncGenerateResponse,
  PostResponse,
  TaskStatusResponse,
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
