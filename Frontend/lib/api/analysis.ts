import { apiFetch } from "./client";
import { endpoints } from "./endpoints";
import type { BrandProfile, MarketInfo, SwotInfo, WizardInput } from "@/lib/onboarding/types";

/**
 * Контракт бэка (generative-orchestration-service, BusinessAnalysisController):
 * профиль уже нормализован в форму BrandProfile, поэтому фронт лишь подстраховывает
 * поля на случай частичного ответа.
 */
export interface AnalysisResponse {
  id: string;
  sessionId: string;
  taskType: string;
  status: "PENDING" | "COMPLETED" | "FAILED";
  profile: Partial<BrandProfile> | null;
  result: Record<string, unknown> | null;
  error: string | null;
}

/** Пустой профиль — стартовое значение ручного режима (как было в моке). */
function emptyProfile(input: WizardInput): BrandProfile {
  return {
    name: input.name.trim() || "Ваш бизнес",
    field: "",
    positioning: "",
    market: { competitors: [], geography: "", segment: "", trends: [] },
    swot: { strengths: [], weaknesses: [], opportunities: [], threats: [] },
    services: [],
    goals: [],
    tone: [],
  };
}

function toList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((v): v is string => typeof v === "string" && v.trim() !== "").map((v) => v.trim());
}

function toStr(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

/**
 * Защищённая нормализация ответа бэка: заполняет обязательные секции BrandProfile,
 * чтобы секции ревью всегда рендерились с валидными данными.
 */
function normalizeProfile(profile: Partial<BrandProfile>, input: WizardInput): BrandProfile {
  const market: MarketInfo = {
    competitors: toList(profile.market?.competitors),
    geography: toStr(profile.market?.geography),
    segment: toStr(profile.market?.segment),
    trends: toList(profile.market?.trends),
  };
  const swot: SwotInfo = {
    strengths: toList(profile.swot?.strengths),
    weaknesses: toList(profile.swot?.weaknesses),
    opportunities: toList(profile.swot?.opportunities),
    threats: toList(profile.swot?.threats),
  };
  const services = Array.isArray(profile.services)
    ? profile.services
        .filter((s): s is { title: string; items: string } => !!s && typeof s.title === "string")
        .map((s) => ({ title: toStr(s.title), items: toStr(s.items) }))
    : [];
  return {
    name: toStr(profile.name) || input.name.trim() || "Ваш бизнес",
    field: toStr(profile.field),
    positioning: toStr(profile.positioning),
    market,
    swot,
    services,
    goals: toList(profile.goals),
    tone: toList(profile.tone),
  };
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function fetchAnalysis(sessionId: string): Promise<AnalysisResponse | null> {
  try {
    return await apiFetch<AnalysisResponse>(endpoints.orchestration.analysisById(sessionId), {
      auth: true,
    });
  } catch {
    return null;
  }
}

async function pollUntilDone(sessionId: string, tries = 10, intervalMs = 1000): Promise<AnalysisResponse | null> {
  for (let i = 0; i < tries; i++) {
    await sleep(intervalMs);
    const current = await fetchAnalysis(sessionId);
    if (current && current.status !== "PENDING") return current;
  }
  return null;
}

/**
 * Реальный AI-анализ бизнеса по шагу «Расскажите о бизнесе»: ссылка + документы
 * (data-URL) + заметки уезжают в business analysis. Если AI-контур недоступен или
 * анализ завершился с ошибкой — тихо откатываемся на пустой профиль: онбординг
 * остаётся рабочим в ручном режиме (профиль заполняется на экране ревью).
 */
export async function analyzeBusiness(input: WizardInput): Promise<BrandProfile> {
  const documents = input.fileData.map((f) => f.dataUrl).filter((d) => d.length > 0);
  const payload = {
    ...(input.name.trim() ? { companyName: input.name.trim() } : {}),
    ...(input.aboutMode === "link" && input.link.trim()
      ? { url: input.link.trim() }
      : {
          notes: [input.activity, input.difference].filter((s) => s.trim()).join(". ") || undefined,
        }),
    documents,
  };

  let response: AnalysisResponse | null = null;
  try {
    response = await apiFetch<AnalysisResponse>(endpoints.orchestration.analyze, {
      method: "POST",
      auth: true,
      body: JSON.stringify(payload),
    });
  } catch {
    return emptyProfile(input);
  }

  if (!response || response.status === "FAILED") return emptyProfile(input);
  if (response.status === "COMPLETED") return normalizeProfile(response.profile ?? {}, input);

  // Статуса PENDING у живого бэка не бывает (wait-синхронный), но страхуемся
  // на случай асинхронного контура с callback-пушем.
  const final = await pollUntilDone(response.sessionId);
  if (final && final.status === "COMPLETED") return normalizeProfile(final.profile ?? {}, input);
  return emptyProfile(input);
}