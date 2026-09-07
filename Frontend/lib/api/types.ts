/** DTO бэка один-в-один. Менять только вместе с контрактом в docs/api/. */

export interface JwtResponse {
  accessToken: string;
  type: string;
}

export interface RegisterRequest {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface ProfileResponse {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string | null;
  position: string | null;
  fullAvatarUrl: string | null;
}

export interface UpdateProfileRequest {
  firstName?: string;
  lastName?: string;
  phone?: string;
  position?: string;
}

export type Industry =
  | "CAFE_RESTAURANT"
  | "BEAUTY_SALON"
  | "RETAIL"
  | "SERVICES"
  | "EDUCATION"
  | "FITNESS"
  | "MEDICINE"
  | "OTHER";

export type ToneOfVoice = "FRIENDLY" | "PROFESSIONAL" | "INFORMAL" | "CREATIVE";

export interface SocialLinks {
  instagram?: string | null;
  telegram?: string | null;
  website?: string | null;
}

export type DayOfWeek =
  | "MONDAY"
  | "TUESDAY"
  | "WEDNESDAY"
  | "THURSDAY"
  | "FRIDAY"
  | "SATURDAY"
  | "SUNDAY";

export interface BusinessHours {
  /** Время в формате HH:mm — бэк принимает и отдаёт java.time.LocalTime. */
  openTime?: string | null;
  closeTime?: string | null;
  offDays?: DayOfWeek[] | null;
}

/** Провайдеры, зарегистрированные в security-service (OAuth2ClientConfig). */
export type AuthProvider = "YANDEX" | "VK";

export interface LinkSocialRequest {
  email: string;
  password: string;
  provider: AuthProvider;
  providerUserId: string;
}

export interface ProjectRequest {
  name: string;
  industry: Industry;
  city: string;
  description?: string;
  targetAudience?: string;
  toneOfVoice: ToneOfVoice;
  socialLinks?: SocialLinks;
  businessHours?: BusinessHours | null;
  /** Профиль бренда целиком: у бэка для SWOT, услуг и целей полей нет. */
  brandProfile?: string;
}

export interface ProjectResponse extends Omit<ProjectRequest, "brandProfile"> {
  id: string;
  ownerId: string;
  logoUrl: string | null;
  /** В ответе поле может прийти null, тогда как в запросе его просто нет. */
  brandProfile?: string | null;
}

/* ------------------------------------------------------------------ *
 * Ниже — DTO эндпоинтов, чья форма ответа в контракте названа, но не
 * расшифрована (TariffResponse, PostResponse и т.п.). Известные поля
 * описаны явно, остальное открыто индексной подписью: так фронт не врёт
 * о полях, которых может не быть, и не падает на тех, что придут сверх.
 * По мере уточнения контракта подписи убираются, поля дописываются.
 * ------------------------------------------------------------------ */

/** Данные пользователя, разобранные шлюзом из токена. */
export interface StatusMeResponse {
  userId: string;
  roles: string[];
  source: string;
}

/** Вход через Яндекс с мобильного: обмен access-токена провайдера на свой JWT. */
export interface YandexMobileRequest {
  accessToken: string;
}

/** Смена почты, шаг 1: подтверждение пароля владельцем аккаунта. */
export interface ChangeEmailVerifyPasswordRequest {
  password: string;
}

/** Шаг 2: на новую почту уходит код подтверждения. */
export interface ChangeEmailSetNewEmailRequest {
  token: string;
  newEmail: string;
}

/** Шаг 3: код из письма закрывает смену. */
export interface ChangeEmailConfirmRequest {
  token: string;
  code: string;
}

export interface TariffResponse {
  id: string;
  name?: string;
  [key: string]: unknown;
}

/** Ответ на «сколько мне осталось по фиче». */
export interface CheckQuotaResponse {
  [key: string]: unknown;
}

/** Свой тариф вместе с квотами по всем фичам. */
export interface SubscriptionOverview {
  [key: string]: unknown;
}

export interface PurchaseTariffRequest {
  tariffId: string;
}

/** Значения enum в контракте не раскрыты — берём как есть из бэка. */
export type GenerationMode = string;

export interface AsyncGenerateRequest {
  projectId: string;
  mode: GenerationMode;
  /** Сколько постов сгенерировать; бэк по умолчанию берёт 1. */
  count?: number;
  prompt?: string;
  industry?: string;
  description?: string;
  targetAudience?: string;
  toneOfVoice?: string;
  city?: string;
  currentMonth?: string;
  currentYear?: number;
}

/** 202 Accepted: работа принята, результат забирается по taskId. */
export interface AsyncGenerateResponse {
  taskId: string;
}

export interface TaskStatusResponse {
  taskId: string;
  status: string;
  [key: string]: unknown;
}

export interface PostResponse {
  id: string;
  [key: string]: unknown;
}
