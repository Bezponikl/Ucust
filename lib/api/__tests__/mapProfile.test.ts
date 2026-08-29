import { describe, it, expect } from "vitest";
import { toProjectRequest } from "@/lib/api/mapProfile";
import { EMPTY_INPUT } from "@/lib/onboarding/types";
import type { BrandProfile } from "@/lib/onboarding/types";

const profile: BrandProfile = {
  name: "Кофейня «Пар»",
  field: "Кофейня",
  positioning: "Третье место в спальном районе",
  market: {
    competitors: [],
    geography: "Санкт-Петербург",
    segment: "Жители района 25–40",
    trends: [],
  },
  swot: { strengths: ["Своя обжарка"], weaknesses: [], opportunities: [], threats: [] },
  services: [],
  goals: ["Вернуть гостей"],
  tone: ["дружелюбный"],
};

describe("toProjectRequest", () => {
  it("подбирает отрасль по нише", () => {
    expect(toProjectRequest({ ...EMPTY_INPUT, name: "Пар" }, profile).industry).toBe(
      "CAFE_RESTAURANT",
    );
  });

  it("для незнакомой ниши отдаёт OTHER", () => {
    const other = { ...profile, field: "Разведение альпак", positioning: "" };
    expect(toProjectRequest(EMPTY_INPUT, other).industry).toBe("OTHER");
  });

  it("переводит тон в enum", () => {
    expect(toProjectRequest(EMPTY_INPUT, profile).toneOfVoice).toBe("FRIENDLY");
  });

  it("распознаёт деловой тон", () => {
    const strict = { ...profile, tone: ["профессиональный", "сдержанный"] };
    expect(toProjectRequest(EMPTY_INPUT, strict).toneOfVoice).toBe("PROFESSIONAL");
  });

  it("берёт город из географии, аудиторию из сегмента", () => {
    const req = toProjectRequest(EMPTY_INPUT, profile);
    expect(req.city).toBe("Санкт-Петербург");
    expect(req.targetAudience).toBe("Жители района 25–40");
  });

  it("подставляет город-заглушку, если география пустая", () => {
    const noCity = { ...profile, market: { ...profile.market, geography: "" } };
    // city у бэка @NotBlank — пустая строка вернула бы 400 на ровном месте.
    expect(toProjectRequest(EMPTY_INPUT, noCity).city).toBe("Не указан");
  });

  it("собирает описание из шага «О бизнесе» и обрезает до 2000 символов", () => {
    const filled = { ...EMPTY_INPUT, activity: "Кофейня", difference: "Своя обжарка" };
    expect(toProjectRequest(filled, profile).description).toBe("Кофейня. Своя обжарка");

    const long = { ...EMPTY_INPUT, difference: "я".repeat(2500) };
    expect(toProjectRequest(long, profile).description).toHaveLength(2000);
  });

  it("подставляет позиционирование, если описание не заполняли", () => {
    expect(toProjectRequest(EMPTY_INPUT, profile).description).toBe(profile.positioning);
  });

  it("складывает профиль целиком в brandProfile", () => {
    const req = toProjectRequest(EMPTY_INPUT, profile);
    expect(JSON.parse(req.brandProfile!).swot.strengths).toEqual(["Своя обжарка"]);
  });

  it("имя проекта берёт из ввода, а при пустом — из профиля", () => {
    expect(toProjectRequest({ ...EMPTY_INPUT, name: "Пар" }, profile).name).toBe("Пар");
    expect(toProjectRequest(EMPTY_INPUT, profile).name).toBe("Кофейня «Пар»");
  });
});
