/**
 * Единая точка входа в слой API: `import { login, listTariffs } from "@/lib/api"`.
 * Пути живут в `endpoints.ts`, транспорт — в `client.ts`, DTO — в `types.ts`.
 */

export { API_BASE_URL } from "./config";
export { endpoints, withQuery } from "./endpoints";
export { apiFetch, getAccessToken, setAccessToken } from "./client";
export { ApiError, parseErrorBody, toMessage } from "./errors";

export * from "./auth";
export * from "./status";
export * from "./users";
export * from "./projects";
export * from "./tariffs";
export * from "./quota";
export * from "./orchestration";
export * from "./oauth";

export type * from "./types";
