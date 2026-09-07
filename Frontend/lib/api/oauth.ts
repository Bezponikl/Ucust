import { API_BASE_URL } from "./config";
import { endpoints } from "./endpoints";
import type { AuthProvider } from "./types";

/** Провайдеры, вход через которые настроен в security-service. */
export type OAuthProvider = "yandex" | "vk";

/**
 * Начало авторизации. Это полноценный переход, а не fetch: дальше работает
 * редирект-цепочка. Адрес идёт через `/api/v0` — контракт перечисляет цепочку
 * без префикса, но шлюз обслуживает её именно под ним (проверено на контуре).
 */
export function authorizeUrl(provider: OAuthProvider): string {
  return `${API_BASE_URL}${endpoints.oauth.authorization(provider)}`;
}

export interface OAuthCallbackParams {
  token: string | null;
  error: string | null;
}

/** Разбирает адрес, на который бэк вернул браузер после входа. */
export function parseOAuthCallback(search: string): OAuthCallbackParams {
  const params = new URLSearchParams(search);
  return {
    token: params.get("token"),
    error: params.get("error"),
  };
}

export interface LinkSocialHint {
  email: string;
  provider: AuthProvider;
  providerUserId: string;
}

/**
 * Почта из соцсети совпала с почтой обычной регистрации: бэк не входит молча, а
 * просит подтвердить пароль. Данные провайдера он передаёт в адресе — их нужно
 * донести до `linkSocial`. null — в адресе не тот случай.
 */
export function parseLinkSocialHint(search: string): LinkSocialHint | null {
  const params = new URLSearchParams(search);
  if (params.get("error") !== "email_exists_link_required") return null;

  const email = params.get("email");
  const provider = params.get("provider");
  const providerUserId = params.get("providerUserId");
  if (!email || !provider || !providerUserId) return null;

  return { email, provider: provider as AuthProvider, providerUserId };
}

const OAUTH_ERRORS: Record<string, string> = {
  email_not_found: "Соцсеть не поделилась адресом почты — разрешите доступ или войдите по паролю",
  email_exists_link_required:
    "На эту почту уже есть аккаунт с паролем — войдите по паролю, и соцсеть привяжется к нему",
};

/** null — ошибки не было; иначе текст для пользователя. */
export function oauthErrorMessage(code: string | null): string | null {
  if (!code) return null;
  return OAUTH_ERRORS[code] ?? "Не удалось войти через соцсеть — попробуйте ещё раз";
}
