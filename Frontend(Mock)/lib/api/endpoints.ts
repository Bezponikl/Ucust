/**
 * Реестр адресов бэка — единственное место, где живут пути API.
 * Источник: `docs/api/api-endpoints-public.json` (контракт v0, basePath `/api/v0`).
 *
 * Пути заданы относительно базы: её подставляет `apiFetch` из `API_BASE_URL`.
 */

/** Хвост запроса из заданных параметров; пустые и undefined отбрасываются. */
export function withQuery(
  path: string,
  params: Record<string, string | number | boolean | null | undefined>,
): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    search.set(key, String(value));
  }
  const qs = search.toString();
  return qs ? `${path}?${qs}` : path;
}

export const endpoints = {
  /** security-service, AuthController */
  auth: {
    register: "/auth/register",
    login: "/auth/login",
    logout: "/auth/logout",
    refresh: "/auth/refresh",
    confirmEmail: (token: string) => withQuery("/auth/confirm-email", { token }),
    resendConfirmation: (email: string) => withQuery("/auth/resend-confirmation", { email }),
    forgotPassword: "/auth/forgot-password",
    resetPassword: "/auth/reset-password",
    yandexMobile: "/auth/yandex-mobile",
    linkSocial: "/auth/link-social",
    changeEmail: {
      verifyPassword: "/auth/change-email/verify-password",
      setNewEmail: "/auth/change-email/set-new-email",
      confirm: "/auth/change-email/confirm",
    },
  },

  /** security-service, StatusController — проверка живости и разбор токена шлюзом */
  status: {
    hello: "/status/hello",
    me: "/status/me",
  },

  /** user-service, ProfileController */
  user: {
    me: "/user/me",
    avatar: "/user/me/avatar",
  },

  /** business-service, ProjectController */
  projects: {
    root: "/projects",
    byId: (id: string) => `/projects/${encodeURIComponent(id)}`,
    logo: (id: string) => `/projects/${encodeURIComponent(id)}/logo`,
  },

  /** billing-service, TariffController (публичные) */
  tariffs: {
    root: "/tariffs",
    byId: (id: string) => `/tariffs/${encodeURIComponent(id)}`,
  },

  /** billing-service, UserQuotaController */
  quota: {
    me: (feature?: string) => withQuery("/quota/me", { feature }),
    myTariff: "/quota/me/tariff",
    purchase: "/quota/me/purchase",
  },

  /** generative-orchestration-service */
  orchestration: {
    generateAsync: "/orchestration/generate/async",
    task: (taskId: string) => `/orchestration/tasks/${encodeURIComponent(taskId)}`,
    post: (id: string) => `/orchestration/posts/${encodeURIComponent(id)}`,
    confirmPost: (id: string) => `/orchestration/posts/${encodeURIComponent(id)}/confirm`,
    publishPost: (id: string) => `/orchestration/posts/${encodeURIComponent(id)}/publish`,
    projectPosts: (projectId: string) =>
      `/orchestration/projects/${encodeURIComponent(projectId)}/posts`,
  },

  /**
   * Цепочка OAuth2. В контракте она записана без префикса версии (`/oauth2/**`),
   * но живой шлюз отвечает как раз под префиксом: `/api/v0/oauth2/authorization/
   * yandex` отдаёт 302 на Яндекс, а `/oauth2/...` — 404. Поэтому пути тут такие
   * же относительные, как остальные. В `apiFetch` их не отдают: это переход
   * браузера, адрес собирает `oauth.ts`.
   */
  oauth: {
    authorization: (provider: string) => `/oauth2/authorization/${provider}`,
    callback: (provider: string) => `/login/oauth2/code/${provider}`,
  },
} as const;
