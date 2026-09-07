/** Блоки, из которых собран правовой документ (см. scripts/build-legal.mjs). */
export type LegalBlock =
  | { t: "h"; text: string }
  | { t: "sub"; text: string }
  | { t: "p"; text: string }
  | { t: "ul"; items: string[] }
  | { t: "ol"; items: string[] };

export interface LegalDoc {
  slug: string;
  /** Полное название — заголовок страницы. */
  title: string;
  /** Короткое имя для навигации: «Оферта», «Cookie». */
  short: string;
  /** Одна строка о содержании — для списка документов. */
  desc: string;
  blocks: LegalBlock[];
  /** Оглавление: разделы верхнего уровня с якорями. */
  toc: { id: string; text: string }[];
}
