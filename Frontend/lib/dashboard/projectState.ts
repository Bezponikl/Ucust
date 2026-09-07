"use client";

/**
 * Заморозка проекта — промежуточное состояние между «работает» и «удалён»:
 * публикации и автоответы встают на паузу, данные остаются на месте.
 *
 * ВАЖНО: в контракте бэка (ProjectRequest) поля статуса нет, поэтому флаг
 * живёт на устройстве. Как только у проекта появится серверный статус, этот
 * модуль заменяется вызовом API — точка замены одна.
 */

const KEY = "uc_project_frozen";

function readAll(): Record<string, boolean> {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Record<string, boolean>) : {};
  } catch {
    return {};
  }
}

export function isProjectFrozen(projectId: string | null): boolean {
  if (!projectId || typeof window === "undefined") return false;
  return readAll()[projectId] === true;
}

export function setProjectFrozen(projectId: string | null, frozen: boolean): void {
  if (!projectId || typeof window === "undefined") return;
  try {
    const all = readAll();
    if (frozen) all[projectId] = true;
    else delete all[projectId];
    localStorage.setItem(KEY, JSON.stringify(all));
  } catch {
    // приватный режим браузера — заморозка просто не переживёт перезагрузку
  }
}
