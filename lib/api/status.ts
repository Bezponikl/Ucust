import { apiFetch } from "./client";
import { endpoints } from "./endpoints";
import type { StatusMeResponse } from "./types";

/** Проверка живости контура под текущим токеном. Ответ — строка «hello». */
export function hello(): Promise<string> {
  return apiFetch<string>(endpoints.status.hello, { auth: true });
}

/**
 * Кого шлюз видит за токеном. Полезно при разборе доступов: сюда попадают
 * заголовки, которые шлюз проставил сервисам, а не то, что нарисовал фронт.
 */
export function whoAmI(): Promise<StatusMeResponse> {
  return apiFetch<StatusMeResponse>(endpoints.status.me, { auth: true });
}
