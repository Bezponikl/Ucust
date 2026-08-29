/** Ошибка ответа API. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly code?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface ParsedError {
  code: string | undefined;
  message: string;
}

/**
 * Сервисы отдают ошибку вложенно — {success:false, error:{code, message}},
 * а шлюз при 500 подставляет свой формат Spring, где поле error содержит
 * служебное «Internal Server Error». Разбираем оба, не путая одно с другим.
 */
export function parseErrorBody(body: unknown): ParsedError {
  if (!body || typeof body !== "object") return { code: undefined, message: "" };

  const raw = body as Record<string, unknown>;

  const nested = raw.error;
  if (nested && typeof nested === "object") {
    const inner = nested as Record<string, unknown>;
    return {
      code: typeof inner.code === "string" ? inner.code : undefined,
      message: typeof inner.message === "string" ? inner.message : "",
    };
  }

  return {
    code: typeof raw.code === "string" ? raw.code : undefined,
    message: typeof raw.message === "string" ? raw.message : "",
  };
}

/** Тексты по кодам ошибок: сообщения бэка приходят на английском. */
const BY_CODE: Record<string, string> = {
  USER_ALREADY_EXISTS: "Аккаунт с такой почтой уже существует — попробуйте войти",
  USER_ALREADY_ACTIVATED: "Аккаунт уже подтверждён — можно входить",
  USER_NOT_FOUND: "Пользователь не найден",
  LINK_EXPIRED: "Ссылка устарела — запросите новую",
  TOKEN_EXPIRED: "Ссылка устарела — запросите новую",
  TOKEN_NOT_FOUND: "Ссылка недействительна — запросите новую",
  REFRESH_TOKEN_NOT_FOUND: "Сессия истекла — войдите заново",
  RATE_LIMIT_EXCEEDED: "Слишком много попыток — подождите пару минут",
  ACCESS_DENIED: "Недостаточно прав для этого действия",
  AUTH_ERROR: "Неверная почта или пароль",
  NOT_FOUND: "Не найдено",
};

/** Тексты валидации: сопоставляем по узнаваемому фрагменту сообщения бэка. */
const VALIDATION_HINTS: Array<[RegExp, string]> = [
  [/passwords do not match/i, "Пароли не совпадают"],
  [/password must be between (\d+) and (\d+)/i, "Пароль — от 8 до 50 символов"],
  [/surname must be in cyrillic/i, "Фамилия — кириллицей, можно с дефисом"],
  [/name must be in cyrillic/i, "Имя — кириллицей, можно с дефисом"],
  [/phone number must be 11 digits/i, "Телефон в формате 79XXXXXXXXX"],
  [/must be a well-formed email|email.*invalid/i, "Проверьте адрес почты"],
  [/must not be blank|must not be empty/i, "Заполните обязательные поля"],
];

/** Текст для пользователя: детали 5xx и английские сообщения бэка не показываем. */
export function toMessage(e: unknown): string {
  if (!(e instanceof ApiError)) return "Не удалось связаться с сервером";

  if (e.status >= 500) return "Сервис временно недоступен, попробуйте позже";

  if (e.code === "VALIDATION_ERROR") {
    const hint = VALIDATION_HINTS.find(([re]) => re.test(e.message))?.[1];
    return hint ?? "Проверьте правильность заполнения полей";
  }

  if (e.code && BY_CODE[e.code]) return BY_CODE[e.code];

  if (e.status === 401) return "Неверная почта или пароль";
  if (e.status === 403) return "Недостаточно прав для этого действия";
  if (e.status === 404) return "Не найдено";

  return "Не удалось выполнить запрос";
}
