import type { CheckQuotaResponse, SubscriptionOverview, TariffResponse } from "./types";

/**
 * Контракт называет ответы биллинга, но не расписывает их поля. Чтобы экран не
 * зависел от догадок, всё чтение собрано здесь: берём первое подходящее поле из
 * знакомых имён, а чего нет — отдаём null, и интерфейс показывает прочерк.
 * Когда бэк опубликует DTO, правится только этот файл.
 */

function str(source: Record<string, unknown>, keys: string[]): string | null {
  for (const key of keys) {
    const value = source[key];
    if (typeof value === "string" && value) return value;
  }
  return null;
}

function num(source: Record<string, unknown>, keys: string[]): number | null {
  for (const key of keys) {
    const value = source[key];
    if (typeof value === "number" && Number.isFinite(value)) return value;
    if (typeof value === "string" && value.trim() !== "" && Number.isFinite(Number(value))) {
      return Number(value);
    }
  }
  return null;
}

export interface TariffView {
  id: string;
  name: string | null;
  price: number | null;
  description: string | null;
  features: string[];
}

export function tariffView(tariff: TariffResponse): TariffView {
  const raw = tariff as Record<string, unknown>;
  const features = raw.features;

  return {
    id: tariff.id,
    name: str(raw, ["name", "title", "displayName"]),
    price: num(raw, ["price", "monthlyPrice", "cost", "amount", "pricePerMonth"]),
    description: str(raw, ["description", "tagline", "subtitle"]),
    features: Array.isArray(features) ? features.filter((f): f is string => typeof f === "string") : [],
  };
}

export interface QuotaView {
  limit: number | null;
  used: number | null;
  remaining: number | null;
}

export function quotaView(quota: CheckQuotaResponse | null): QuotaView {
  if (!quota) return { limit: null, used: null, remaining: null };
  const raw = quota as Record<string, unknown>;

  const limit = num(raw, ["limit", "total", "quota", "maxCount"]);
  const used = num(raw, ["used", "usedCount", "consumed", "spent"]);
  const remaining = num(raw, ["remaining", "left", "available", "balance"]);

  return {
    limit,
    used: used ?? (limit !== null && remaining !== null ? limit - remaining : null),
    remaining: remaining ?? (limit !== null && used !== null ? limit - used : null),
  };
}

export interface SubscriptionView {
  tariffId: string | null;
  tariffName: string | null;
  renewsOn: string | null;
  status: string | null;
}

export function subscriptionView(overview: SubscriptionOverview | null): SubscriptionView {
  if (!overview) return { tariffId: null, tariffName: null, renewsOn: null, status: null };
  const raw = overview as Record<string, unknown>;
  const nested = (raw.tariff ?? raw.plan) as Record<string, unknown> | undefined;

  return {
    tariffId: str(raw, ["tariffId", "planId"]) ?? (nested ? str(nested, ["id"]) : null),
    tariffName: str(raw, ["tariffName", "planName"]) ?? (nested ? str(nested, ["name", "title"]) : null),
    renewsOn: str(raw, ["renewsOn", "expiresAt", "nextBillingDate", "validUntil", "endDate"]),
    status: str(raw, ["status", "state"]),
  };
}

/** Дата бэка (ISO) в вид «11 августа 2026». Не дата — вернём как пришло. */
export function formatDate(value: string | null): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" });
}
