// Собирает правовые документы из content/legal/*.md в lib/legal.content.ts.
// Исходники — тексты юриста, править нужно их, а не сгенерированный файл.
// Запуск: node scripts/build-legal.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const dir = join(root, "content/legal");

const operator = JSON.parse(readFileSync(join(dir, "_operator.json"), "utf8"));

// Порядок здесь = порядок в навигации: от главного договора к частным согласиям
const DOCS = [
  {
    slug: "offer",
    file: "offer.md",
    title: "Публичная оферта",
    short: "Оферта",
    desc: "Условия платного доступа: тарифы, оплата, автопродление и возврат средств.",
  },
  {
    slug: "terms",
    file: "terms.md",
    title: "Пользовательское соглашение",
    short: "Соглашение",
    desc: "Правила работы с сервисом: регистрация, права сторон, ИИ-инструменты, контент.",
  },
  {
    slug: "privacy",
    file: "privacy.md",
    title: "Политика конфиденциальности",
    short: "Конфиденциальность",
    desc: "Какие данные собираем, зачем, где храним и как их защищаем.",
  },
  {
    slug: "pdn-consent",
    file: "pdn-consent.md",
    title: "Согласие на обработку персональных данных",
    short: "Согласие на ПДн",
    desc: "Перечень данных, цели и способы обработки, срок действия согласия.",
  },
  {
    slug: "cookie",
    file: "cookie.md",
    title: "Соглашение об использовании cookie",
    short: "Cookie",
    desc: "Какие cookie-файлы используются на сайте и как ими управлять.",
  },
  {
    slug: "marketing-consent",
    file: "marketing-consent.md",
    title: "Согласие на рекламную и новостную рассылку",
    short: "Рассылка",
    desc: "Условия рассылок и порядок отказа от них.",
  },
];

/** Плейсхолдеры юриста подставляем из _operator.json — правится в одном месте. */
function substitute(text) {
  return text
    .replace(/\[наименование юридического лица\/ИП[^\]]*\]/g, operator.company)
    .replace(/\[наименование, ОГРН\/ОГРНИП[^\]]*\]/g, operator.requisites)
    .replace(/\[дата публикации\]/g, operator.updated);
}

const isBulletLine = (l) => /^[-*•]\s+/.test(l);
const isOrderedLine = (l) => /^\d+\.\s+\S/.test(l) && !/^\d+\.\d/.test(l);
/** Строка целиком в ** ** — это подзаголовок раздела, а не абзац. */
const isSubheadLine = (l) => /^\*\*[^*]+\*\*:?$/.test(l);

/**
 * Разбор ограничен тем, что реально встречается в документах: заголовки «##»,
 * жирные подзаголовки, маркированные и нумерованные списки, абзацы с **…**.
 * Полноценный markdown-парсер здесь был бы лишней зависимостью.
 */
function parse(md) {
  const lines = substitute(md).split(/\r?\n/);
  const blocks = [];
  let list = null; // накопитель текущего списка

  const flush = () => {
    if (list && list.items.length) blocks.push(list);
    list = null;
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      // Пустые строки внутри списка (экспорт из редактора) его не разрывают
      continue;
    }

    if (line.startsWith("## ")) {
      flush();
      blocks.push({ t: "h", text: line.slice(3).trim() });
      continue;
    }
    if (line.startsWith("### ")) {
      flush();
      blocks.push({ t: "sub", text: line.slice(4).trim() });
      continue;
    }
    if (isSubheadLine(line)) {
      flush();
      const text = line.replace(/^\*\*|\*\*:?$/g, "").trim();
      // «**1. Перечень данных**» — такой же раздел, как «## 1. Предмет», просто
      // юрист оформил его жирным. Иначе документ остался бы без оглавления.
      blocks.push({ t: /^\d+\.\s/.test(text) ? "h" : "sub", text });
      continue;
    }
    if (isBulletLine(line)) {
      if (!list || list.t !== "ul") {
        flush();
        list = { t: "ul", items: [] };
      }
      list.items.push(line.replace(/^[-*•]\s+/, ""));
      continue;
    }
    if (isOrderedLine(line)) {
      if (!list || list.t !== "ol") {
        flush();
        list = { t: "ol", items: [] };
      }
      list.items.push(line.replace(/^\d+\.\s+/, ""));
      continue;
    }

    flush();
    blocks.push({ t: "p", text: line });
  }
  flush();

  // Первая строка «Дата последнего обновления: …» дублирует подпись в шапке
  if (blocks[0]?.t === "p" && /^Дата последнего обновления/i.test(blocks[0].text)) blocks.shift();

  return blocks;
}

const docs = DOCS.map((meta) => {
  const md = readFileSync(join(dir, meta.file), "utf8");
  const blocks = parse(md);
  // Оглавление: заголовки верхнего уровня с якорями по порядку
  const toc = blocks
    .map((b, i) => (b.t === "h" ? { id: `s${i}`, text: b.text } : null))
    .filter(Boolean);
  return { slug: meta.slug, title: meta.title, short: meta.short, desc: meta.desc, blocks, toc };
});

const ts = `// АВТОГЕНЕРАЦИЯ — не редактировать вручную.
// Источник: content/legal/*.md + content/legal/_operator.json
// Пересобрать: node scripts/build-legal.mjs
import type { LegalDoc } from "./legal.types";

export const LEGAL_UPDATED = ${JSON.stringify(operator.updated)};
export const LEGAL_COMPANY = ${JSON.stringify(operator.company)};
export const LEGAL_EMAIL = ${JSON.stringify(operator.email)};

export const LEGAL_DOCS: LegalDoc[] = ${JSON.stringify(docs, null, 2)};
`;

writeFileSync(join(root, "lib/legal.content.ts"), ts);

// Лёгкий индекс для навигации: подключать полные тексты ради ссылок в меню
// значит тащить в бандл сотню килобайт документов.
const index = docs.map(({ slug, title, short, desc }) => ({ slug, title, short, desc }));
const indexTs = `// АВТОГЕНЕРАЦИЯ — не редактировать вручную. Пересобрать: node scripts/build-legal.mjs

export interface LegalLink {
  slug: string;
  title: string;
  short: string;
  desc: string;
}

export const LEGAL_UPDATED = ${JSON.stringify(operator.updated)};
export const LEGAL_COMPANY = ${JSON.stringify(operator.company)};
export const LEGAL_EMAIL = ${JSON.stringify(operator.email)};

export const LEGAL_INDEX: LegalLink[] = ${JSON.stringify(index, null, 2)};
`;
writeFileSync(join(root, "lib/legal.index.ts"), indexTs);
const stats = docs.map((d) => `${d.slug}: ${d.blocks.length} блоков, ${d.toc.length} разделов`).join("\n  ");
console.log(`OK: ${docs.length} документов → lib/legal.content.ts\n  ${stats}`);
