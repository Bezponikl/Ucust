// Извлекает только нужные иконки Solar из @iconify-json/solar в локальный lib/icons/solar.ts.
// Так мы не тащим в бандл весь набор (6500+ иконок). Запуск: node scripts/gen-icons.mjs
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const solar = JSON.parse(readFileSync(join(root, "node_modules/@iconify-json/solar/icons.json"), "utf8"));
const dw = solar.width ?? 24;
const dh = solar.height ?? 24;

// Смысловое имя в коде  →  имя иконки в наборе Solar
const MAP = {
  "arrow-right": "arrow-right-linear",
  "arrow-left": "arrow-left-linear",
  "arrow-up": "arrow-up-linear",
  "chevron-down": "alt-arrow-down-linear",
  "chevron-left": "alt-arrow-left-linear",
  "chevron-right": "alt-arrow-right-linear",
  menu: "hamburger-menu-linear",
  close: "close-circle-linear",
  check: "check-circle-linear",
  "check-bold": "check-circle-bold",
  sparkles: "magic-stick-3-linear",
  "sparkles-bold": "magic-stick-3-bold",
  sliders: "tuning-2-linear",
  help: "question-circle-linear",
  sun: "sun-linear",
  moon: "moon-linear",
  dashboard: "widget-2-linear",
  calendar: "calendar-linear",
  trending: "chart-2-linear",
  mail: "letter-linear",
  shield: "shield-check-linear",
  heart: "hand-heart-linear",
  // Добавлено для замены lucide в дашборде/онбординге/модалках (§12)
  "image-plus": "gallery-add-linear",
  logout: "logout-2-linear",
  monitor: "monitor-linear",
  trash: "trash-bin-trash-linear",
  camera: "camera-linear",
  "file-text": "document-text-linear",
  gift: "gift-linear",
  megaphone: "speaker-linear",
  plus: "add-square-linear",
  bell: "bell-linear",
  star: "star-linear",
  "star-bold": "star-bold",
  "bar-chart": "chart-square-linear",
  scale: "scale-linear",
  settings: "settings-linear",
  eye: "eye-linear",
  "user-plus": "user-plus-rounded-linear",
  message: "chat-round-linear",
  send: "plain-2-linear",
  edit: "pen-2-linear",
  link: "link-round-linear",
  upload: "upload-linear",
  grid: "widget-linear",
  "calendar-check": "calendar-mark-linear",
  "calendar-plus": "calendar-add-linear",
  clapperboard: "clapperboard-play-linear",
  clock: "clock-circle-linear",
  play: "play-bold",
  refresh: "refresh-linear",
  image: "gallery-linear",
  brain: "cpu-bolt-linear",
  "mail-check": "letter-opened-linear",
  card: "card-linear",
  receipt: "bill-list-linear",
  phone: "phone-linear",
  emoji: "smile-circle-linear",
  lock: "lock-keyhole-minimalistic-linear",
  search: "magnifer-linear",
  copy: "copy-linear",
  list: "list-linear",
  sort: "sort-vertical-linear",
  crop: "crop-linear",
};

const out = {};
const missing = [];
for (const [key, solarName] of Object.entries(MAP)) {
  const ic = solar.icons[solarName];
  if (!ic) { missing.push(`${key} → ${solarName}`); continue; }
  out[key] = { body: ic.body, w: ic.width ?? dw, h: ic.height ?? dh };
}

if (missing.length) {
  console.error("НЕ НАЙДЕНЫ:\n" + missing.join("\n"));
  process.exit(1);
}

// Свои иконки поверх набора. В Solar галочка есть только внутри круга или квадрата,
// а внутри наших круглых бейджей это давало двойную обводку — рисуем чистую птичку.
const EXTRA = {
  check: {
    body: '<path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m5 12.5l4.5 4.5L19 7"/>',
    w: 24,
    h: 24,
  },
  close: {
    body: '<path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 6l12 12M18 6L6 18"/>',
    w: 24,
    h: 24,
  },
};
Object.assign(out, EXTRA);

const ts =
`// АВТОГЕНЕРАЦИЯ — не редактировать вручную. Источник: scripts/gen-icons.mjs (набор Solar).
// Пересобрать: node scripts/gen-icons.mjs
export type IconName = ${Object.keys(out).map((k) => `"${k}"`).join(" | ")};

export const ICONS: Record<IconName, { body: string; w: number; h: number }> = ${JSON.stringify(out, null, 2)};
`;

mkdirSync(join(root, "lib/icons"), { recursive: true });
writeFileSync(join(root, "lib/icons/solar.ts"), ts);
console.log(`OK: извлечено ${Object.keys(out).length} иконок → lib/icons/solar.ts`);
