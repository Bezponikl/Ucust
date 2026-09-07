// Правовые документы UCust. Публичные — доступны всем (и авторизованным, и нет).
// Тексты лежат в content/legal/*.md и собираются скриптом scripts/build-legal.mjs
// в lib/legal.content.ts (полные документы) и lib/legal.index.ts (навигация).
//
// Этот модуль — лёгкий фасад: здесь только метаданные и ссылки, поэтому его
// можно импортировать в футеры и меню, не таща в бандл сотню килобайт текста.
// За самими документами ходите в "@/lib/legal.content".

export { LEGAL_COMPANY, LEGAL_EMAIL, LEGAL_UPDATED, type LegalLink } from "./legal.index";
export type { LegalBlock, LegalDoc } from "./legal.types";

import { LEGAL_INDEX } from "./legal.index";

/** Ссылки на документы в порядке навигации: label — короткое имя для меню. */
export const LEGAL_LINKS = LEGAL_INDEX.map((d) => ({
  label: d.short,
  title: d.title,
  desc: d.desc,
  slug: d.slug,
  href: `/legal/${d.slug}`,
}));

export const isLegalSlug = (slug: string) => LEGAL_INDEX.some((d) => d.slug === slug);
