/**
 * Съёмка блока конкурентов на экране бренд-профиля: состояние онбординга
 * кладём прямо в sessionStorage, живой прогон визарда для вёрстки не нужен.
 * Запуск: node scripts/_shots-competitors.mjs
 */
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.UC_BASE ?? "http://localhost:3000";
const OUT = "screenshots/pravki";

const STATE = {
  input: {
    name: "UCust",
    aboutMode: "link",
    link: "https://ucust.online",
    activity: "ИИ-платформа для ведения соцсетей малого бизнеса",
    difference: "Автопилот вместо ручного SMM",
    socials: ["vk", "telegram"],
    files: [],
  },
  profile: {
    name: "UCust",
    field: "SMM-платформа для малого бизнеса",
    positioning: "ИИ ведёт соцсети за владельца бизнеса",
    market: {
      competitors: [
        "SMMplanner (https://smmplanner.com)",
        "LiveDune (https://livedune.ru)",
        "Postmypost (https://postmypost.ru)",
        "Яндекс.Бизнес (https://business.yandex.ru)",
        "VK Реклама (https://ads.vk.com)",
        "TgStat (https://tgstat.ru)",
        "Локальные агентства г. Москва",
        "Контент-фрилансеры",
      ],
      geography: "Москва",
      segment: "Предприниматели, маркетологи и SMM-специалисты, которым нужно вести соцсети без штата",
      trends: ["Рост доли ИИ-контента", "Уход зарубежных сервисов"],
    },
    swot: { strengths: [], weaknesses: [], opportunities: [], threats: [] },
    services: [],
    goals: [],
    tone: ["дружелюбный"],
  },
};

mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();

for (const [name, w, h] of [["competitors", 1440, 900], ["competitors-mobile", 390, 844]]) {
  const ctx = await browser.newContext({
    viewport: { width: w, height: h },
    deviceScaleFactor: 2,
    isMobile: w < 700,
    hasTouch: w < 700,
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto(`${BASE}/onboarding`, { waitUntil: "domcontentloaded" });
  await page.evaluate((s) => window.sessionStorage.setItem("ucust:onboarding", JSON.stringify(s)), STATE);
  await page.goto(`${BASE}/onboarding/review`, { waitUntil: "load" });
  await page.waitForTimeout(2500);
  const market = page.getByRole("button", { name: /Рынок/ }).first();
  if (await market.count()) {
    await market.click();
    await page.waitForTimeout(700);
  }
  await page.screenshot({ path: `${OUT}/${name}.png` });
  console.log(`${name} → ${page.url()}${errors.length ? `  ⚠ ${errors.slice(0, 2).join(" | ")}` : ""}`);
  await ctx.close();
}

await browser.close();
