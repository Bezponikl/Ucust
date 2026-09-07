import { API_BASE_URL } from "./config";
import { endpoints } from "./endpoints";
import { ApiError, parseErrorBody } from "./errors";

/**
 * Access-токен живёт только в памяти вкладки: в localStorage его класть нельзя,
 * иначе любая XSS уносит сессию. Долгоживущий refresh лежит в httpOnly-куке,
 * недоступной JS, — поэтому после перезагрузки страницы сессия восстанавливается
 * запросом /auth/refresh, а не чтением хранилища.
 */
let accessToken: string | null = null;
let refreshing: Promise<string | null> | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

async function refreshAccessToken(): Promise<string | null> {
  // Параллельные 401 должны сойтись в один запрос обновления: иначе гонка
  // сожжёт refresh-токен и выбросит пользователя из сессии.
  if (!refreshing) {
    refreshing = (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}${endpoints.auth.refresh}`, {
          method: "POST",
          credentials: "include",
        });
        if (!res.ok) return null;
        const data = (await res.json()) as JwtLike;
        accessToken = data.accessToken;
        return accessToken;
      } catch {
        return null;
      } finally {
        refreshing = null;
      }
    })();
  }
  return refreshing;
}

interface JwtLike {
  accessToken: string;
}

export interface ApiFetchInit extends RequestInit {
  /** true — подставить Authorization и при 401 попытаться обновить токен. */
  auth?: boolean;
}

/**
 * Бэк стандартизирует все успешные ответы обёрткой ApiResponse из common:
 * `{ success: true, data: ..., error, pagination }`. Здесь мы её разворачиваем,
 * чтобы вызывающий код работал с чистыми DTO. Не-обёртки (строки, массивы,
 * пустые тела) возвращаются как есть. Ошибки сюда не доходят — их отбрасывает
 * ветка `!res.ok` выше.
 */
function unwrapData<T>(body: unknown): T {
  if (body !== null && typeof body === "object" && "success" in body && "data" in body) {
    const { success, data } = body as { success?: unknown; data?: unknown };
    if (success === true) return data as T;
  }
  return body as T;
}

export async function apiFetch<T>(path: string, init: ApiFetchInit = {}): Promise<T> {
  const { auth = false, headers, ...rest } = init;

  const send = (token: string | null) =>
    fetch(`${API_BASE_URL}${path}`, {
      ...rest,
      credentials: "include",
      headers: {
        // FormData сама проставляет boundary — свой Content-Type её ломает.
        ...(rest.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
    });

  let res = await send(auth ? accessToken : null);

  if (res.status === 401 && auth) {
    const fresh = await refreshAccessToken();
    if (fresh) res = await send(fresh);
  }

  if (!res.ok) {
    let parsed: { code: string | undefined; message: string } = { code: undefined, message: "" };
    try {
      parsed = parseErrorBody(await res.json());
    } catch {
      /* тело не JSON — оставляем пустое сообщение, его переведёт toMessage */
    }
    throw new ApiError(res.status, parsed.message, parsed.code);
  }

  if (res.status === 204) return undefined as T;
  const text = await res.text();
  return (text ? unwrapData(JSON.parse(text)) : undefined) as T;
}
