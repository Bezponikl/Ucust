import { describe, it, expect } from "vitest";
import { buildDashboardData } from "@/lib/dashboard/data";
import type { BrandProfile } from "@/lib/onboarding/types";

const PROFILE: BrandProfile = {
  name: "Кофейня на Невском",
  field: "Кофейня",
  positioning: "Свежая обжарка",
  market: { competitors: [], geography: "СПб", segment: "B2C", trends: [] },
  swot: { strengths: [], weaknesses: [], opportunities: [], threats: [] },
  services: [],
  goals: [],
  tone: [],
};

describe("buildDashboardData", () => {
  it("берёт имя из brandProfile, когда он есть", () => {
    const data = buildDashboardData(PROFILE, null, null, []);
    expect(data.businessName).toBe("Кофейня на Невском");
    expect(data.businessLogo).toBeNull();
  });

  it("падает на имя проекта, когда brandProfile пустой", () => {
    const data = buildDashboardData(null, "EcoCoffee Roasters", "http://localhost:8100/s3/a.png", [
      { id: "p1", name: "EcoCoffee Roasters", logo: null },
    ]);
    expect(data.businessName).toBe("EcoCoffee Roasters");
    expect(data.businessLogo).toBe("http://localhost:8100/s3/a.png");
    expect(data.projects).toHaveLength(1);
  });

  it("возвращает null, когда нет ни профиля, ни проекта", () => {
    expect(buildDashboardData(null, null, null, []).businessName).toBeNull();
    expect(buildDashboardData(null, null, null, []).businessLogo).toBeNull();
  });
});