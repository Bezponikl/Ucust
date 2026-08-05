/**
 * Даты и время публикаций — единый слой для создания и редактирования поста.
 * Формат хранения даты — ISO `YYYY-MM-DD`, времени — `HH:MM` (24 часа).
 */

export const MONTHS_NOM = [
  "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
] as const;

export const MONTHS_GEN = [
  "января", "февраля", "марта", "апреля", "мая", "июня",
  "июля", "августа", "сентября", "октября", "ноября", "декабря",
] as const;

/** Мок-месяц контент-плана: Февраль 2026 (Пн-старт, ровно 4 недели). */
export const MOCK_YEAR = 2026;
export const MOCK_MONTH = 1; // 0-based → февраль

export const pad2 = (n: number) => String(n).padStart(2, "0");

export interface DateParts {
  year: number;
  month: number; // 0-based
  day: number;
}

export const toIso = ({ year, month, day }: DateParts) => `${year}-${pad2(month + 1)}-${pad2(day)}`;

export function parseIso(iso: string): DateParts {
  const [y, m, d] = iso.split("-").map(Number);
  return { year: y, month: (m ?? 1) - 1, day: d ?? 1 };
}

/** День мок-месяца (Post.day) → ISO. */
export const dayToIso = (day: number) => toIso({ year: MOCK_YEAR, month: MOCK_MONTH, day });

/** ISO → день месяца; для дат вне мок-месяца это всё равно номер дня. */
export const isoDay = (iso: string) => parseIso(iso).day;

/** Дата принадлежит мок-месяцу контент-плана (только там знаем занятость дней). */
export const isMockMonth = (iso: string) => {
  const { year, month } = parseIso(iso);
  return year === MOCK_YEAR && month === MOCK_MONTH;
};

export const daysInMonth = (year: number, month: number) => new Date(year, month + 1, 0).getDate();

/** Индекс первого дня месяца при Пн-старте: 0 = понедельник. */
export const firstWeekdayMon = (year: number, month: number) => (new Date(year, month, 1).getDay() + 6) % 7;

export const todayIso = () => {
  const t = new Date();
  return toIso({ year: t.getFullYear(), month: t.getMonth(), day: t.getDate() });
};

export const isoOffset = (days: number) => {
  const t = new Date();
  t.setDate(t.getDate() + days);
  return toIso({ year: t.getFullYear(), month: t.getMonth(), day: t.getDate() });
};

export const MONTHS_SHORT = [
  "янв", "фев", "мар", "апр", "мая", "июн",
  "июл", "авг", "сен", "окт", "ноя", "дек",
] as const;

/** «1 фев» → ISO. Возвращает null, если строку разобрать не удалось. */
export function parseRuShort(value: string, year = MOCK_YEAR): string | null {
  const m = value.trim().toLowerCase().match(/^(\d{1,2})\s+([а-яё]+)/);
  if (!m) return null;
  const day = Number(m[1]);
  const month = MONTHS_SHORT.findIndex((s) => m[2].startsWith(s.slice(0, 3)));
  if (month < 0 || day < 1 || day > daysInMonth(year, month)) return null;
  return toIso({ year, month, day });
}

/** «1 фев» — компактная подпись периода. */
export const fmtShort = (iso: string) => {
  const { month, day } = parseIso(iso);
  return `${day} ${MONTHS_SHORT[month] ?? ""}`.trim();
};

/** «1 фев — 28 фев» из пары ISO-дат. */
export const fmtPeriod = (from: string, to: string) =>
  from && to ? `${fmtShort(from)} — ${fmtShort(to)}` : from ? fmtShort(from) : "";

/** «12 февраля» — для превью и подписей. */
export const fmtDayMonth = (iso: string) => {
  const { month, day } = parseIso(iso);
  return `${day} ${MONTHS_GEN[month] ?? ""}`.trim();
};

/** «12 февраля 2026» — когда год важен (перенос на другой год). */
export const fmtFullDate = (iso: string) => {
  const { year, month, day } = parseIso(iso);
  return `${day} ${MONTHS_GEN[month] ?? ""} ${year}`;
};

/* ── Время ── */

export const TIME_RE = /^([01]\d|2[0-3]):([0-5]\d)$/;

export const isValidTime = (value: string) => TIME_RE.test(value);

/**
 * Проверка ввода времени: ровно 4 цифры, часы 00–23, минуты 00–59.
 * Возвращает нормализованное `HH:MM` либо текст ошибки — валидируем на blur,
 * чтобы не ругаться на каждое нажатие клавиши.
 */
export function validateTime(raw: string): { value: string } | { error: string } {
  const digits = raw.replace(/\D/g, "");
  if (digits.length !== 4) return { error: "Введите 4 цифры — например 09:30" };
  const h = Number(digits.slice(0, 2));
  const m = Number(digits.slice(2));
  if (h > 23) return { error: "Часы — от 00 до 23" };
  if (m > 59) return { error: "Минуты — от 00 до 59" };
  return { value: `${pad2(h)}:${pad2(m)}` };
}

/** Маска ввода: цифры сами разделяются двоеточием, максимум 4 цифры. */
export function maskTime(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 4);
  return digits.length <= 2 ? digits : `${digits.slice(0, 2)}:${digits.slice(2)}`;
}
