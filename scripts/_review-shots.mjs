/**
 * Съёмка экранов дашборда для ревью правок. Сессия и проект подменяются
 * стабами API — живой контур для вёрстки не нужен.
 *
 * Запуск: node scripts/_review-shots.mjs [имя-набора]
 */
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.UC_BASE ?? "http://localhost:3111";
const API = "**/api/v0/**";
const OUT = "screenshots/review";

const PROFILE = {
  id: "u1",
  firstName: "Антон",
  lastName: "Есиков",
  email: "esikov@example.com",
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

function stub(route, body, status = 200) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

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

const SHOTS = [
  { name: "create", path: "/dashboard/create", w: 1440, h: 900 },
  { name: "create-mobile", path: "/dashboard/create", w: 390, h: 844 },
  { name: "content", path: "/dashboard/content", w: 1440, h: 900 },
  { name: "promos", path: "/dashboard/promos", w: 1440, h: 900 },
  { name: "analytics", path: "/dashboard/analytics", w: 1440, h: 900 },
  { name: "analytics-mobile", path: "/dashboard/analytics", w: 390, h: 844 },
  { name: "subscription", path: "/dashboard/subscription", w: 1440, h: 900 },
  { name: "inbox", path: "/dashboard/inbox", w: 1440, h: 900 },
  { name: "business", path: "/dashboard/business", w: 1440, h: 900 },
  { name: "dashboard", path: "/dashboard", w: 1440, h: 900 },
];

const only = process.argv[2];

mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();

for (const shot of SHOTS) {
  if (only && !shot.name.includes(only)) continue;
  const ctx = await browser.newContext({
    viewport: { width: shot.w, height: shot.h },
    deviceScaleFactor: 2,
    isMobile: shot.w < 700,
    hasTouch: shot.w < 700,
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await routeApi(page);
  await page.goto(`${BASE}${shot.path}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: `${OUT}/${shot.name}.png`, fullPage: false });
  console.log(`${shot.name} → ${page.url()}${errors.length ? `  ⚠ ${errors.slice(0, 3).join(" | ")}` : ""}`);
  await ctx.close();
}

await browser.close();
