/**
 * Конкуренты приходят от парсера одной строкой: «SMMplanner (https://smmplanner.com)».
 * В таком виде их нельзя ни показать (текст уезжает за край поля), ни открыть.
 * Здесь строка разбирается на имя и ссылку и собирается обратно — хранение
 * в профиле остаётся прежним, меняется только представление.
 */

export interface Competitor {
  /** Название без скобок со ссылкой. */
  name: string;
  /** Полный URL, если парсер его нашёл. */
  url: string;
  /** Домен без www — короткая подпись под названием. */
  host: string;
}

const URL_RE = /\bhttps?:\/\/[^\s)»"']+/i;

/** Домен без протокола и www: «https://smmplanner.com/ru» → «smmplanner.com». */
export function hostOf(url: string): string {
  if (!url) return "";
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url.replace(/^https?:\/\//i, "").replace(/^www\./, "").split("/")[0];
  }
}

export function parseCompetitor(raw: string): Competitor {
  const value = (raw ?? "").trim();
  const url = value.match(URL_RE)?.[0]?.replace(/[).,;]+$/, "") ?? "";
  // Убираем ссылку и осиротевшие скобки/тире, оставшиеся от «Имя (ссылка)»
  const name = value
    .replace(URL_RE, "")
    .replace(/\(\s*\)/g, "")
    .replace(/[\s—–-]*[(\[]?\s*$/g, "")
    .replace(/^\s*[(\[]/, "")
    .trim();

  return { name: name || hostOf(url) || value, url, host: hostOf(url) };
}

/** Обратная сборка в строку профиля — формат тот же, что отдаёт парсер. */
export function formatCompetitor(c: { name: string; url: string }): string {
  const name = c.name.trim();
  const url = c.url.trim();
  if (name && url) return `${name} (${url})`;
  return name || url;
}

/** Ссылку из строки браузера («smmplanner.com») приводим к рабочему https-виду. */
export function normalizeUrl(input: string): string {
  const v = input.trim();
  if (!v) return "";
  return /^https?:\/\//i.test(v) ? v : `https://${v}`;
}
