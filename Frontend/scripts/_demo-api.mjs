/**
 * ЛОКАЛЬНЫЙ МОК API ДЛЯ ДЕМОНСТРАЦИИ. В сборку не входит, приложение о нём не знает.
 *
 * Зачем: чтобы показывать фронт без поднятого бэка. Вход «проходит» всегда —
 * /auth/refresh сразу отдаёт токен, поэтому SessionProvider считает сессию живой,
 * AuthGuard пускает в дашборд, а логиниться не нужно.
 *
 * Как включить, НЕ ТРОГАЯ файлы проекта (переменная окружения перебивает .env.local):
 *   node scripts/_demo-api.mjs &
 *   NEXT_PUBLIC_API_BASE_URL=http://localhost:8123/api/v0 npx next dev -p 3111
 *
 * Ни один исходник ради демо не правится: адрес API читается из
 * process.env.NEXT_PUBLIC_API_BASE_URL в lib/api/config.ts.
 */
import { createServer } from "node:http";

const PORT = Number(process.env.DEMO_API_PORT ?? 8123);
const PREFIX = "/api/v0";

/* ── Демо-данные ──────────────────────────────────────────────── */

const PROFILE = {
  id: "demo-user",
  firstName: "Антон",
  lastName: "Есиков",
  email: "esikov@ucust.demo",
  phone: "+7 999 000-00-00",
  position: "Владелец",
  fullAvatarUrl: null,
};

/** Профиль бренда — из-за него дашборд показывает живой бизнес, а не заглушку. */
const BRAND_PROFILE = {
  name: "Кофейня «Аромат»",
  field: "Кофейня — спешелти-кофе и свежая выпечка",
  positioning:
    "Уютная городская кофейня с авторскими напитками и зерном собственной обжарки",
  market: {
    competitors: ["Surf Coffee", "Cofix", "Skuratov Coffee"],
    geography: "Россия, Санкт-Петербург",
    segment: "Жители района, офисные сотрудники, студенты, любители кофе",
    trends: [
      "Рост спроса на спешелти-кофе и альтернативные напитки",
      "Популярность кофе навынос и завтраков",
      "Гости выбирают атмосферные локальные кофейни",
    ],
  },
  swot: {
    strengths: ["Авторские напитки и своя обжарка", "Уютная атмосфера", "Локация в центре"],
    weaknesses: ["Высокая конкуренция рядом", "Зависимость от потока в часы пик"],
    opportunities: ["Доставка и кофе навынос", "Завтраки и бизнес-ланчи", "Программа лояльности"],
    threats: ["Сетевые кофейни поблизости", "Рост цен на зерно"],
  },
  services: [
    { title: "Спешелти-кофе", items: "Эспрессо, капучино, раф, фильтр" },
    { title: "Свежая выпечка", items: "Круассаны, синнабоны, чизкейки" },
    { title: "Завтраки", items: "Сырники, гранола, тосты" },
  ],
  goals: [
    "Увеличить узнаваемость кофейни в районе",
    "Привлечь новых гостей и подписчиков",
    "Повысить средний чек через сезонное меню",
  ],
  tone: ["Дружелюбный", "Тёплый", "С заботой"],
};

const PROJECT = {
  id: "demo-project",
  ownerId: PROFILE.id,
  name: "Кофейня «Аромат»",
  industry: "CAFE_RESTAURANT",
  city: "Санкт-Петербург",
  description: "Спешелти-кофейня со своей обжаркой в центре города",
  targetAudience: "Жители района 25–40 лет, офисные сотрудники, студенты",
  toneOfVoice: "FRIENDLY",
  socialLinks: { vk: "https://vk.com/ucust_demo", telegram: "https://t.me/ucust_demo" },
  businessHours: { openTime: "08:00", closeTime: "22:00", offDays: [] },
  logoUrl: null,
  brandProfile: JSON.stringify(BRAND_PROFILE),
};

const TARIFFS = [
  {
    id: "start",
    name: "Старт",
    price: 1500,
    description: "Для одного бизнеса.",
    features: ["1 бизнес", "До 12 постов в месяц", "Все соцсети без ограничений", "Генерация фото"],
  },
  {
    id: "business",
    name: "Бизнес",
    price: 3500,
    description: "Для регулярного ведения.",
    features: ["3 бизнеса", "До 30 постов в месяц", "Генерация фото и видео", "Расширенная аналитика"],
  },
];

const QUOTA = { limit: 30, used: 21, remaining: 9, feature: "GENERATION" };

const GENERATED_TEXT =
  "Летнее меню уже в «Аромате» ☀️\n\n" +
  "Мы собрали напитки, которые хочется пить в жару: холодный раф на своей обжарке, " +
  "лимонад с базиликом и эспрессо-тоник. Всё — на зерне, которое обжариваем сами.\n\n" +
  "Заходите попробовать первыми — ждём вас с 8:00 до 22:00.";

/* ── Каркас сервера ───────────────────────────────────────────── */

const log = (...a) => console.log("[demo-api]", ...a);

function send(res, status, body, origin) {
  const payload = body === undefined ? "" : JSON.stringify(body);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    // credentials: "include" запрещает Allow-Origin: * — отражаем origin запроса
    "Access-Control-Allow-Origin": origin ?? "*",
    "Access-Control-Allow-Credentials": "true",
    "Vary": "Origin",
  });
  res.end(payload);
}

/** Совпадение пути с шаблоном вида "/projects/:id/logo". */
function match(pattern, path) {
  const p = pattern.split("/").filter(Boolean);
  const a = path.split("/").filter(Boolean);
  if (p.length !== a.length) return null;
  const params = {};
  for (let i = 0; i < p.length; i += 1) {
    if (p[i].startsWith(":")) params[p[i].slice(1)] = decodeURIComponent(a[i]);
    else if (p[i] !== a[i]) return null;
  }
  return params;
}

/* method + path → ответ. undefined в body = 204. */
const ROUTES = [
  // ── Авторизация: она и есть «пропуск без бэка» ──
  ["POST", "/auth/refresh", () => [200, { accessToken: "demo-access-token", refreshToken: "demo-refresh-token" }]],
  ["POST", "/auth/login", () => [200, { accessToken: "demo-access-token", refreshToken: "demo-refresh-token" }]],
  ["POST", "/auth/register", () => [200, { accessToken: "demo-access-token", refreshToken: "demo-refresh-token" }]],
  ["POST", "/auth/logout", () => [204]],
  ["GET", "/auth/confirm-email", () => [204]],
  ["POST", "/auth/resend-confirmation", () => [204]],
  ["POST", "/auth/forgot-password", () => [204]],
  ["POST", "/auth/reset-password", () => [204]],
  ["POST", "/auth/change-email/verify-password", () => [200, { token: "demo-change-token" }]],
  ["POST", "/auth/change-email/set-new-email", () => [204]],
  ["POST", "/auth/change-email/confirm", () => [204]],

  ["GET", "/status/hello", () => [200, { status: "ok" }]],
  ["GET", "/status/me", () => [200, { userId: PROFILE.id, roles: ["USER"], source: "demo" }]],

  // ── Пользователь ──
  ["GET", "/user/me", () => [200, PROFILE]],
  ["PATCH", "/user/me", (_p, body) => [200, Object.assign(PROFILE, body ?? {})]],
  ["POST", "/user/me/avatar", () => [200, "/content/avatars/olga-m.jpg"]],

  // ── Проекты ──
  ["GET", "/projects", () => [200, [PROJECT]]],
  ["POST", "/projects", (_p, body) => [200, Object.assign({}, PROJECT, body ?? {})]],
  ["GET", "/projects/:id", () => [200, PROJECT]],
  ["PATCH", "/projects/:id", (_p, body) => [200, Object.assign(PROJECT, body ?? {})]],
  ["DELETE", "/projects/:id", () => [204]],
  ["POST", "/projects/:id/logo", () => [200, "/brand/logo-darktext.webp"]],

  // ── Биллинг ──
  ["GET", "/tariffs", () => [200, TARIFFS]],
  ["GET", "/tariffs/:id", (p) => [200, TARIFFS.find((t) => t.id === p.id) ?? TARIFFS[1]]],
  ["GET", "/quota/me", () => [200, QUOTA]],
  ["GET", "/quota/me/tariff", () => [200, { tariff: TARIFFS[1], quotas: [QUOTA] }]],
  ["POST", "/quota/me/purchase", () => [200, { tariff: TARIFFS[1], quotas: [QUOTA] }]],

  // ── Генерация ──
  ["POST", "/orchestration/generate/async", () => [200, { taskId: "demo-task" }]],
  ["GET", "/orchestration/tasks/:id", () => [200, { taskId: "demo-task", status: "DONE", text: GENERATED_TEXT, postId: "demo-post" }]],
  ["GET", "/orchestration/posts/:id", () => [200, { id: "demo-post", text: GENERATED_TEXT, status: "DRAFT" }]],
  ["POST", "/orchestration/posts/:id/confirm", () => [204]],
  ["POST", "/orchestration/posts/:id/publish", () => [204]],
  ["GET", "/orchestration/projects/:id/posts", () => [200, []]],
];

const server = createServer((req, res) => {
  const origin = req.headers.origin;
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": origin ?? "*",
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Methods": "GET,POST,PATCH,PUT,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type,Authorization",
      "Access-Control-Max-Age": "86400",
      "Vary": "Origin",
    });
    res.end();
    return;
  }

  const path = url.pathname.startsWith(PREFIX) ? url.pathname.slice(PREFIX.length) : url.pathname;

  const chunks = [];
  req.on("data", (c) => chunks.push(c));
  req.on("end", () => {
    let body;
    try {
      const raw = Buffer.concat(chunks).toString("utf8");
      body = raw ? JSON.parse(raw) : undefined;
    } catch {
      body = undefined; // multipart/пустое тело — обработчикам оно не нужно
    }

    for (const [method, pattern, handler] of ROUTES) {
      if (method !== req.method) continue;
      const params = match(pattern, path);
      if (!params) continue;
      const [status, payload] = handler(params, body);
      log(req.method, path, "→", status);
      send(res, status, payload, origin);
      return;
    }

    // Неописанный путь — честный 404: экраны рассчитаны мягко деградировать
    log(req.method, path, "→ 404 (нет в моке)");
    send(res, 404, { code: "NOT_FOUND", message: "Нет в демо-моке" }, origin);
  });
});

server.listen(PORT, () => {
  log(`слушает http://localhost:${PORT}${PREFIX} — вход проходит без бэка`);
});
