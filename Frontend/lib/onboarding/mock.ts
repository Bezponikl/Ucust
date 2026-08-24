import type { BrandProfile, WizardInput } from "./types";
import { pickPreset } from "./presets";
import { submitAiTask } from "@/lib/api/ai";

/**
 * Синхронизированный анализ бизнеса через Агента-Интервьюера и Сайгу.
 * Отправляет реальный запрос в AI Gateway (POST /api/v1/ai/task с task_type: "onboarding").
 * В случае отсутствия связи с сервером бережно подставляет локальный пресет.
 */
export async function analyzeBusiness(input: WizardInput): Promise<BrandProfile> {
  const name = input.name.trim() || "Ваш бизнес";
  const text = [input.name, input.description, input.activity, input.difference, input.link].join(" ");
  const fallbackPreset = pickPreset(text);

  try {
    const res = await submitAiTask({
      task_type: "onboarding",
      payload: {
        company_name: name,
        name: name,
        description: input.description,
        activity: input.activity,
        difference: input.difference,
        raw_social_input: input.link,
        link: input.link,
        socials: input.socials,
        files: input.files,
      },
    });

    if (res?.data?.profile) {
      const p = res.data.profile as BrandProfile;
      return {
        name: p.name || name,
        field: p.field || input.activity || fallbackPreset.field,
        positioning: p.positioning || input.description || fallbackPreset.positioning,
        market: {
          competitors: p.market?.competitors?.length ? p.market.competitors : fallbackPreset.market.competitors,
          geography: p.market?.geography || fallbackPreset.market.geography,
          segment: p.market?.segment || fallbackPreset.market.segment,
          trends: p.market?.trends?.length ? p.market.trends : fallbackPreset.market.trends,
        },
        swot: {
          strengths: p.swot?.strengths?.length ? p.swot.strengths : fallbackPreset.swot.strengths,
          weaknesses: p.swot?.weaknesses?.length ? p.swot.weaknesses : fallbackPreset.swot.weaknesses,
          opportunities: p.swot?.opportunities?.length ? p.swot.opportunities : fallbackPreset.swot.opportunities,
          threats: p.swot?.threats?.length ? p.swot.threats : fallbackPreset.swot.threats,
        },
        services: p.services?.length ? p.services : fallbackPreset.services,
        goals: p.goals?.length ? p.goals : fallbackPreset.goals,
        tone: p.tone?.length ? p.tone : fallbackPreset.tone,
      };
    }
  } catch (err) {
    console.warn("[Onboarding] AI Gateway offline, using smart local preset:", err);
  }

  // Fallback с минимальной задержкой для плавности анимации стадий
  await new Promise((resolve) => setTimeout(resolve, 2200));
  return { name, ...fallbackPreset };
}
