import type { BusinessProfile } from "@/lib/dashboard/businesses";
import { EMPTY_BUSINESS, TONE_LABELS } from "@/lib/dashboard/businesses";
import type {
  BusinessHours,
  DayOfWeek,
  Industry,
  ProjectRequest,
  ProjectResponse,
  ToneOfVoice,
} from "./types";

/**
 * Настройки бизнеса показывают проект бэка человеческим языком: отрасль там —
 * enum, дни недели — константы, часы — LocalTime. Перевод в обе стороны собран
 * здесь, чтобы экран не знал про формат контракта.
 */

export const INDUSTRY_LABELS: Record<Industry, string> = {
  CAFE_RESTAURANT: "Кафе и рестораны",
  BEAUTY_SALON: "Салон красоты",
  RETAIL: "Розничный магазин",
  SERVICES: "Услуги",
  EDUCATION: "Образование",
  FITNESS: "Фитнес и спорт",
  MEDICINE: "Медицина",
  OTHER: "Другое",
};

/** Метки тона в том же порядке, что и TONE_LABELS: индексу метки = индекс enum. */
export const TONE_ENUMS: ToneOfVoice[] = [
  "FRIENDLY",
  "PROFESSIONAL",
  "INFORMAL",
  "CREATIVE",
];

export function toneToLabel(tone: ToneOfVoice | undefined): string {
  if (!tone) return EMPTY_BUSINESS.toneOfVoice;
  return TONE_LABELS[TONE_ENUMS.indexOf(tone)] ?? TONE_LABELS[0];
}

export function labelToTone(label: string): ToneOfVoice {
  const idx = TONE_LABELS.indexOf(label);
  return TONE_ENUMS[idx >= 0 ? idx : 0];
}

/** Порядок дней в интерфейсе: Пн…Вс, как в календаре. */
const WEEK_DAYS: DayOfWeek[] = [
  "MONDAY",
  "TUESDAY",
  "WEDNESDAY",
  "THURSDAY",
  "FRIDAY",
  "SATURDAY",
  "SUNDAY",
];

export function industryToLabel(industry: Industry | undefined): string {
  return industry ? INDUSTRY_LABELS[industry] ?? INDUSTRY_LABELS.OTHER : INDUSTRY_LABELS.OTHER;
}

export function labelToIndustry(label: string): Industry {
  const found = (Object.entries(INDUSTRY_LABELS) as Array<[Industry, string]>).find(
    ([, value]) => value === label,
  );
  return found?.[0] ?? "OTHER";
}

/** «09:00» ← «09:00:00»: бэк отдаёт LocalTime с секундами, полю ввода они мешают. */
function toShortTime(value: string | null | undefined, fallback: string): string {
  if (!value) return fallback;
  const [h = "", m = ""] = value.split(":");
  return h && m ? `${h}:${m}` : fallback;
}

/** Позиционирование из brandProfile-JSON: терпим к любой форме строки. */
export function positioningOf(project: ProjectResponse | null | undefined): string {
  const raw = project?.brandProfile;
  if (!raw) return "";
  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const value = parsed.positioning;
    return typeof value === "string" ? value : "";
  } catch {
    return "";
  }
}

/** Позиционирование в brandProfile-JSON: остальные ключи профиля сохраняем. */
export function brandProfileWithPositioning(
  current: ProjectResponse | null | undefined,
  positioning: string,
): string | undefined {
  const raw = current?.brandProfile;
  let base: Record<string, unknown> = {};
  if (raw) {
    try {
      const parsed = JSON.parse(raw) as Record<string, unknown>;
      if (parsed && typeof parsed === "object") base = parsed;
    } catch {
      base = {};
    }
  }
  if (positioning.trim()) base.positioning = positioning.trim();
  else if ("positioning" in base) delete base.positioning;
  return Object.keys(base).length > 0 ? JSON.stringify(base) : undefined;
}

export function projectToBusiness(project: ProjectResponse): BusinessProfile {
  const hours = project.businessHours ?? null;
  const offDays = hours?.offDays ?? [];

  return {
    ...EMPTY_BUSINESS,
    id: project.id,
    name: project.name ?? "",
    logo: project.logoUrl ?? undefined,
    category: industryToLabel(project.industry),
    // Отдельного адреса у проекта нет — бэк хранит город.
    address: project.city ?? "",
    site: project.socialLinks?.website ?? "",
    description: project.description ?? "",
    targetAudience: project.targetAudience ?? "",
    toneOfVoice: toneToLabel(project.toneOfVoice),
    positioning: positioningOf(project),
    instagram: project.socialLinks?.instagram ?? "",
    telegram: project.socialLinks?.telegram ?? "",
    workStart: toShortTime(hours?.openTime, EMPTY_BUSINESS.workStart),
    workEnd: toShortTime(hours?.closeTime, EMPTY_BUSINESS.workEnd),
    daysOff: WEEK_DAYS.map((day, index) => (offDays.includes(day) ? index : -1)).filter(
      (index) => index >= 0,
    ),
    // Список собран из `...EMPTY_BUSINESS` — статус сверяем с реальными ссылками проекта.
    socials: EMPTY_BUSINESS.socials.map((s) => ({
      ...s,
      connected: s.id === "telegram" ? Boolean(project.socialLinks?.telegram) : s.connected,
    })),
  };
}

/** Правки экрана в вид, который принимает PATCH /projects/{id}. */
export function businessToProjectPatch(
  business: BusinessProfile,
  current?: ProjectResponse | null,
): Partial<ProjectRequest> {
  const businessHours: BusinessHours = {
    openTime: business.workStart || null,
    closeTime: business.workEnd || null,
    offDays: business.daysOff.map((index) => WEEK_DAYS[index]).filter(Boolean),
  };

  const socialLinks = {
    ...(current?.socialLinks ?? {}),
    website: business.site || null,
    instagram: business.instagram.trim() || null,
    telegram: business.telegram.trim() || null,
  };

  return {
    name: business.name.slice(0, 100),
    industry: labelToIndustry(business.category),
    // city у бэка @NotBlank — пустое значение вернуло бы 400.
    city: (business.address || current?.city || "Не указан").slice(0, 50),
    description: business.description.slice(0, 2000),
    targetAudience: business.targetAudience.trim().slice(0, 500),
    toneOfVoice: labelToTone(business.toneOfVoice),
    socialLinks,
    businessHours,
    brandProfile: brandProfileWithPositioning(current, business.positioning),
  };
}
