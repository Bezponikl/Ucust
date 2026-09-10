/** DTO бэка один-в-один. Менять только вместе с контрактом в docs/api/. */

export interface JwtResponse {
  accessToken: string;
  type: string;
}

/** Активная сессия пользователя (security-service, AuthController). */
export interface SessionResponse {
  id: string;
  ip: string;
  /** Город, определённый по IP (null, если не удалось). */
  city: string | null;
  userAgent: string;
  createdAt: string | null;
  expiresAt: string | null;
  rememberMe: boolean;
  current: boolean;
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
  middleName: string | null;
  lastName: string;
  email: string;
  phone: string | null;
  position: string | null;
  fullAvatarUrl: string | null;
}

export interface UpdateProfileRequest {
  firstName?: string;
  middleName?: string;
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

/** Значения enum из бэка (PostStatus). */
export type PostStatus = "DRAFT" | "CONFIRMED" | "SCHEDULED" | "PUBLISHED" | "REJECTED";

/**
 * Пост генерации. Известные поля — из PostResponse бэка (gen-ort), остальное
 * открыто индексной подписью на случай новых полей сверх текущей версии.
 */
export interface PostResponse {
  id: string;
  projectId?: string;
  text?: string | null;
  imageUrl?: string | null;
  hashtags?: string | null;
  targetPlatforms?: string | null;
  /** ISO-8601 (Instant) — время запланированной публикации. */
  scheduledAt?: string | null;
  status?: PostStatus;
  contentType?: string;
  generationMode?: string;
  createdAt?: string | null;
  [key: string]: unknown;
}

/** Partial-правки поста: бэк обновляет только переданные поля (PATCH). */
export interface UpdatePostRequest {
  text?: string;
  imageUrl?: string;
  hashtags?: string;
  targetPlatforms?: string;
  /** ISO-8601 (Instant), напр. 2026-09-12T10:00:00Z. */
  scheduledAt?: string;
}

/** Ответ AI-аудита поста (критик Чарли Мангера через /api/v1/ai/critic/review). */
export interface CriticReviewResponse {
  status: string;
  critic: string;
  data: Record<string, unknown> | null;
  error: string | null;
}

/** Ответ верификации соцсети (этап онбординга): verified=true — страница/канал существует. */
export interface SocialVerifyResponse {
  channel: string;
  reference: string;
  verified: boolean;
  provider: string | null;
  error: string | null;
}
