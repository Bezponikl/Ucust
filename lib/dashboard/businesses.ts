import type { ChannelId } from "@/lib/channels";
import { CHANNEL_ORDER } from "@/lib/channels";
import type { OnboardingState } from "@/lib/onboarding/storage";

export interface SocialLink {
  id: ChannelId;
  connected: boolean;
}

export interface BusinessProfile {
  id: string;
  name: string;
  logo?: string;
  category: string;
  address: string;
  phone: string;
  site: string;
  description: string;
  workStart: string; // "09:00"
  workEnd: string; // "18:00"
  daysOff: number[]; // 0..6 → Пн..Вс
  socials: SocialLink[];
}

/**
 * Список повторяет отрасли бэка (Industry) один в один: иначе выбранная сфера
 * не доедет до проекта. Перевод в enum — в lib/api/mapBusiness.ts.
 */
export const CATEGORIES = [
  "Кафе и рестораны",
  "Салон красоты",
  "Розничный магазин",
  "Услуги",
  "Образование",
  "Фитнес и спорт",
  "Медицина",
  "Другое",
];

const socials = (connectedIds: ChannelId[]): SocialLink[] =>
  CHANNEL_ORDER.slice(0, 6).map((id) => ({ id, connected: connectedIds.includes(id) }));

/** Пустой профиль — пока проекта нет, показывать чужие данные нечестно. */
export const EMPTY_BUSINESS: BusinessProfile = {
  id: "current",
  name: "",
  category: CATEGORIES[0],
  address: "",
  phone: "",
  site: "",
  description: "",
  workStart: "09:00",
  workEnd: "18:00",
  daysOff: [],
  socials: socials([]),
};

/**
 * Профиль бизнеса из данных онбординга: настройки показывают тот же проект,
 * что и весь остальной дашборд.
 */
export function businessFromOnboarding(state: OnboardingState | null): BusinessProfile | null {
  const profile = state?.profile;
  if (!profile) return null;
  const input = state?.input;
  return {
    ...EMPTY_BUSINESS,
    name: profile.name || input?.name || "",
    category: profile.field || CATEGORIES[0],
    site: input?.link ?? "",
    description: profile.positioning || input?.difference || input?.activity || "",
    socials: socials(input?.socials ?? []),
  };
}
