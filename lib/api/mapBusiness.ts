import type { BusinessProfile } from "@/lib/dashboard/businesses";
import { EMPTY_BUSINESS } from "@/lib/dashboard/businesses";
import type {
  BusinessHours,
  DayOfWeek,
  Industry,
  ProjectRequest,
  ProjectResponse,
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
    workStart: toShortTime(hours?.openTime, EMPTY_BUSINESS.workStart),
    workEnd: toShortTime(hours?.closeTime, EMPTY_BUSINESS.workEnd),
    daysOff: WEEK_DAYS.map((day, index) => (offDays.includes(day) ? index : -1)).filter(
      (index) => index >= 0,
    ),
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

  return {
    name: business.name.slice(0, 100),
    industry: labelToIndustry(business.category),
    // city у бэка @NotBlank — пустое значение вернуло бы 400.
    city: (business.address || current?.city || "Не указан").slice(0, 50),
    description: business.description.slice(0, 2000),
    socialLinks: {
      ...(current?.socialLinks ?? {}),
      website: business.site || null,
    },
    businessHours,
  };
}
