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
let refreshing: Promise<RefreshOutcome> | null = null;

/** Слот для уведомления «сессия умерла» — регистрирует SessionProvider. */
let sessionExpiredListener: (() => void) | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

/** Передать обработчик протухания сессии (или null, чтобы отписаться). */
export function onSessionExpired(listener: (() => void) | null): void {
  sessionExpiredListener = listener;
}

/** Итог попытки обновить токен. Что отдаём: новый токен / сессия мертва / временный сбой. */
type RefreshOutcome =
  | { ok: true; token: string }
  | { ok: false; reason: "expired" | "transient" };

async function refreshAccessToken(): Promise<RefreshOutcome> {
  // Параллельные 401 должны сойтись в один запрос обновления: иначе гонка
  // сожжёт refresh-токен и выбросит пользователя из сессии.
  if (!refreshing) {
    refreshing = (async (): Promise<RefreshOutcome> => {
      try {
        const res = await fetch(`${API_BASE_URL}${endpoints.auth.refresh}`, {
          method: "POST",
          credentials: "include",
        });
        if (res.status === 401 || res.status === 403) {
          // Refresh-кука перестала приниматься — сессия реально истекла.
          accessToken = null;
          sessionExpiredListener?.();
          return { ok: false, reason: "expired" };
        }
        if (!res.ok) {
          // Временный сбой шлюза/сети: токен не обновился, но сессию не рушим.
          return { ok: false, reason: "transient" };
        }
        // Ответ также завёрнут в ApiResponse (unwrapData), как и у остальных
        // эндпоинтов: без него accessToken вычитался бы как undefined.
        const data = unwrapData(await res.json()) as JwtLike;
        if (!data.accessToken) {
          accessToken = null;
          sessionExpiredListener?.();
          return { ok: false, reason: "expired" };
        }
        accessToken = data.accessToken;
        return { ok: true, token: accessToken };
      } catch {
        // Сеть лежала — не выкидываем пользователя из сессии.
        return { ok: false, reason: "transient" };
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
    const outcome = await refreshAccessToken();
    if (outcome.ok) {
      res = await send(outcome.token);
      // Свежий токен тоже отвергнут — асимметрия между фронтом и шлюзом. Сессия
      // на деле жива (refresh прошёл), поэтому отдельной протухшей ошибки не шьём:
      // это обычный 401, который toMessage покажет как «Неверная почта или пароль».
    } else if (outcome.reason === "expired") {
      // Refresh начисто отказал — сессия мертва. Состояние переключает
      // sessionExpiredListener, а вызывающий код получает понятное сообщение.
      throw new ApiError(401, "", undefined, true);
    }
    // reason === "transient": токены не достались, но и сессия жива —
    // проваливаемся в общую ветку !res.ok и показываем обычную ошибку.
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
