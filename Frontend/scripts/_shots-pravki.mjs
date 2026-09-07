/**
 * Съёмка экранов под текущий пакет правок: аналитика (график, тултип, столбцы),
 * конкуренты в онбординге, правовые документы, меню профиля без кнопки «?».
 * Запуск: node scripts/_shots-pravki.mjs
 */
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.UC_BASE ?? "http://localhost:3000";
const API = "**/api/v0/**";
const OUT = "screenshots/pravki";

const PROFILE = {
  id: "u1",
  firstName: "Анна",
  lastName: "Иванова",
  email: "anna@example.com",
  phone: null,
  position: null,
  fullAvatarUrl: null,
};

const PROJECT = {
  id: "p1",
  ownerId: "u1",
  name: "Кофейня Аромат",
  industry: "CAFE_RESTAURANT",
  city: "Санкт-Петербург",
  description: "Спешелти-кофейня со своей обжаркой",
  targetAudience: "Жители района 25–40 лет",
  toneOfVoice: "FRIENDLY",
  logoUrl: null,
  brandProfile: null,
};

const stub = (route, body, status = 200) =>
  route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });

async function routeApi(page) {
  await page.route(API, async (route) => {
    const url = route.request().url();
    if (url.includes("/auth/refresh")) return stub(route, { accessToken: "stub", refreshToken: "stub" });
    if (url.includes("/user/me")) return stub(route, PROFILE);
    if (url.includes("/projects")) return stub(route, [PROJECT]);
    if (url.includes("/status/me")) return stub(route, { userId: "u1", roles: ["USER"], source: "stub" });
    return stub(route, {}, 404);
  });
}

mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();

async function shot(name, { path, w = 1440, h = 900, before, full = false }) {
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
  await routeApi(page);
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  if (before) await before(page);
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: full });
  console.log(`${name} → ${page.url()}${errors.length ? `  ⚠ ${errors.slice(0, 3).join(" | ")}` : ""}`);
  await ctx.close();
}

// Аналитика: базовый вид, наведение на точку, столбчатый вид
await shot("analytics", { path: "/dashboard/analytics" });
await shot("analytics-hover", {
  path: "/dashboard/analytics",
  before: async (page) => {
    const svg = page.locator("svg[role=img]").first();
    const b = await svg.boundingBox();
    await page.mouse.move(b.x + b.width * 0.62, b.y + b.height * 0.5);
    await page.waitForTimeout(400);
  },
});
await shot("analytics-bars", {
  path: "/dashboard/analytics",
  before: async (page) => {
    await page.getByRole("button", { name: "Столбчатый график" }).click();
    await page.waitForTimeout(500);
  },
});
await shot("analytics-mobile", { path: "/dashboard/analytics", w: 390, h: 844 });

// Меню профиля: кнопки «?» в шапке больше нет, подсказки внутри меню
await shot("profile-menu", {
  path: "/dashboard/analytics",
  before: async (page) => {
    await page.getByRole("button", { name: "Профиль" }).click();
    await page.waitForTimeout(400);
  },
});

// Правовые: публичная страница и раздел кабинета
await shot("legal-public", { path: "/legal/offer", full: true });
await shot("legal-index", { path: "/legal" });
await shot("legal-dashboard", { path: "/dashboard/legal/privacy" });
await shot("legal-mobile", { path: "/legal/terms", w: 390, h: 844 });

await browser.close();
