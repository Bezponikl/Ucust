import type { BrandProfile, WizardInput } from "@/lib/onboarding/types";
import type { Industry, ProjectRequest, ToneOfVoice } from "./types";

// Бэк принимает отрасль и тон как enum из фиксированного списка, а онбординг
// оперирует свободным текстом. Сопоставляем по ключевым словам ниши.
const INDUSTRY_HINTS: Array<[Industry, RegExp]> = [
  ["CAFE_RESTAURANT", /кофе|кафе|ресторан|бар\b|пекарн|кондитер|пицц|суши|достав\w* ед/i],
  ["BEAUTY_SALON", /салон|красот|барбер|парикмахер|маникюр|ногт|бров|космет|спа\b/i],
  ["FITNESS", /фитнес|спорт|зал\b|йог|танц|бассейн|тренаж/i],
  ["MEDICINE", /клиник|медицин|стоматолог|врач|лаборатор|аптек/i],
  ["EDUCATION", /школ|курс|обучен|образован|репетитор|детск\w* центр|языков/i],
  ["RETAIL", /магазин|розниц|товар|бутик|шоурум|маркет/i],
  ["SERVICES", /услуг|сервис|ремонт|клининг|ателье|автомой|юридич|бухгалтер/i],
];

const TONE_HINTS: Array<[ToneOfVoice, RegExp]> = [
  ["PROFESSIONAL", /профессионал|эксперт|делов|официальн|строг|сдержан/i],
  ["INFORMAL", /неформальн|на «ты»|на "ты"|прост|разговорн|свойск/i],
  ["CREATIVE", /креатив|игрив|смел|нестандартн|ярк/i],
  ["FRIENDLY", /дружелюб|тёпл|тепл|заботлив|душевн/i],
];

function pick<T>(hints: Array<[T, RegExp]>, text: string, fallback: T): T {
  return hints.find(([, re]) => re.test(text))?.[0] ?? fallback;
}

/**
 * Онбординг собирает заметно больше, чем принимает ProjectRequest, поэтому
 * профиль целиком уезжает в brandProfile — иначе SWOT, услуги и цели пропали бы.
 */
export function toProjectRequest(input: WizardInput, profile: BrandProfile): ProjectRequest {
  const nicheText = [profile.field, profile.positioning, input.activity].join(" ");
  const toneText = profile.tone.join(" ");

  return {
    name: (input.name || profile.name).slice(0, 100),
    industry: pick(INDUSTRY_HINTS, nicheText, "OTHER"),
    // city у бэка @NotBlank: пустая строка вернула бы 400 на ровном месте.
    city: (profile.market.geography || "Не указан").slice(0, 50),
    // Описание бизнеса приходит с шага «О бизнесе»; если его заполнили ссылкой —
    // берём позиционирование из собранного профиля, поле у бэка обязательное.
    description: ([input.activity, input.difference].filter(Boolean).join(". ") || profile.positioning).slice(0, 2000),
    targetAudience: profile.market.segment.slice(0, 500),
    toneOfVoice: pick(TONE_HINTS, toneText, "FRIENDLY"),
    socialLinks: {
      instagram: input.link.startsWith("https://") ? input.link : null,
      telegram: input.socials.includes("telegram") ? "" : null,
      website: null,
    },
    businessHours: null,
    brandProfile: JSON.stringify(profile),
  };
}
