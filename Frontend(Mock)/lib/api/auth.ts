import { apiFetch, setAccessToken } from "./client";
import { endpoints } from "./endpoints";
import type {
  ChangeEmailConfirmRequest,
  ChangeEmailSetNewEmailRequest,
  JwtResponse,
  LinkSocialRequest,
  LoginRequest,
  RegisterRequest,
} from "./types";

export async function register(req: RegisterRequest): Promise<void> {
  await apiFetch<void>(endpoints.auth.register, { method: "POST", body: JSON.stringify(req) });
}

export async function login(req: LoginRequest): Promise<string> {
  const res = await apiFetch<JwtResponse>(endpoints.auth.login, {
    method: "POST",
    body: JSON.stringify(req),
  });
  setAccessToken(res.accessToken);
  return res.accessToken;
}

export async function logout(): Promise<void> {
  try {
    await apiFetch<void>(endpoints.auth.logout, { method: "POST", auth: true });
  } finally {
    // Даже если сервер не ответил, локальную сессию гасим: пользователь нажал «выйти».
    setAccessToken(null);
  }
}

/** Восстановление сессии по httpOnly-куке. null — куки нет или она просрочена. */
export async function refresh(): Promise<string | null> {
  try {
    const res = await apiFetch<JwtResponse>(endpoints.auth.refresh, { method: "POST" });
    setAccessToken(res.accessToken);
    return res.accessToken;
  } catch {
    return null;
  }
}

/** Подтверждение почты по токену из письма — вызывается со страницы перехода по ссылке. */
export async function confirmEmail(token: string): Promise<void> {
  await apiFetch<void>(endpoints.auth.confirmEmail(token));
}

export async function resendConfirmation(email: string): Promise<void> {
  await apiFetch<void>(endpoints.auth.resendConfirmation(email), { method: "POST" });
}

export async function forgotPassword(email: string): Promise<void> {
  await apiFetch<void>(endpoints.auth.forgotPassword, {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

/**
 * Привязка соцсети к уже существующему парольному аккаунту. Бэк упирается в это,
 * когда почта из Яндекса совпала с почтой обычной регистрации: возвращает браузер
 * на /login с кодом `email_exists_link_required` и данными провайдера в адресе.
 * Пользователь подтверждает пароль — и входит уже связанным аккаунтом.
 */
export async function linkSocial(req: LinkSocialRequest): Promise<string> {
  const res = await apiFetch<JwtResponse>(endpoints.auth.linkSocial, {
    method: "POST",
    body: JSON.stringify(req),
  });
  setAccessToken(res.accessToken);
  return res.accessToken;
}

/**
 * Вход через Яндекс без редирект-цепочки: приложение уже получило токен провайдера
 * и меняет его на свой. Для веба вход начинается с `authorizeUrl` из oauth.ts.
 */
export async function loginWithYandexToken(accessToken: string): Promise<string> {
  const res = await apiFetch<JwtResponse>(endpoints.auth.yandexMobile, {
    method: "POST",
    body: JSON.stringify({ accessToken }),
  });
  setAccessToken(res.accessToken);
  return res.accessToken;
}

export async function resetPassword(
  token: string,
  newPassword: string,
  confirmPassword: string,
): Promise<void> {
  await apiFetch<void>(endpoints.auth.resetPassword, {
    method: "POST",
    body: JSON.stringify({ token, newPassword, confirmPassword }),
  });
}

/* --- Смена почты: пароль → код на новый адрес → подтверждение --- */

/**
 * Шаг 1. Единственный шаг под Bearer: остальные два идут по токену смены.
 * Контракт обещает только «200 OK», но токен бэк может вернуть и телом —
 * тогда пользователю не придётся переписывать его из письма руками.
 * null — токена в ответе нет, ждём письмо.
 */
export async function changeEmailVerifyPassword(password: string): Promise<string | null> {
  const res = await apiFetch<unknown>(endpoints.auth.changeEmail.verifyPassword, {
    method: "POST",
    auth: true,
    body: JSON.stringify({ password }),
  });

  if (typeof res === "string") return res || null;
  if (res && typeof res === "object") {
    const body = res as Record<string, unknown>;
    for (const key of ["token", "data", "changeEmailToken"]) {
      if (typeof body[key] === "string") return body[key] as string;
    }
  }
  return null;
}

/** Шаг 2. Отправляет код подтверждения на новый адрес. */
export async function changeEmailSetNewEmail(req: ChangeEmailSetNewEmailRequest): Promise<void> {
  await apiFetch<void>(endpoints.auth.changeEmail.setNewEmail, {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/** Шаг 3. Код из письма закрывает смену. */
export async function changeEmailConfirm(req: ChangeEmailConfirmRequest): Promise<void> {
  await apiFetch<void>(endpoints.auth.changeEmail.confirm, {
    method: "POST",
    body: JSON.stringify(req),
  });
}
