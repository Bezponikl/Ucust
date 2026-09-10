"use client";

import { useState } from "react";
import Icon from "@/components/ui/Icon";
import { WEEKDAYS, postsByDay } from "@/lib/dashboard/content";
import {
  MONTHS_NOM,
  MOCK_MONTH,
  MOCK_YEAR,
  daysInMonth,
  firstWeekdayMon,
  parseIso,
  toIso,
  todayIso,
} from "@/lib/dashboard/date";

const YEAR_MIN = MOCK_YEAR - 1;
const YEAR_MAX = MOCK_YEAR + 5;

/**
 * Календарь месяца с переключением месяца и года.
 * Дата приходит и уходит в ISO `YYYY-MM-DD` — один формат на создание и редактирование.
 */
export function MonthCalendar({
  value,
  onSelect,
  /** Дата поста до правки: свою занятость днём не подсвечиваем. */
  originalDate,
}: {
  value: string;
  onSelect: (iso: string) => void;
  originalDate?: string;
}) {
  const selected = parseIso(value);
  const [view, setView] = useState({ year: selected.year, month: selected.month });
  const [picking, setPicking] = useState(false);

  const today = todayIso();
  const busyByDay = postsByDay();
  const isMockView = view.year === MOCK_YEAR && view.month === MOCK_MONTH;
  const original = originalDate ? parseIso(originalDate) : null;

  const shift = (delta: number) => {
    const next = new Date(view.year, view.month + delta, 1);
    const year = next.getFullYear();
    if (year < YEAR_MIN || year > YEAR_MAX) return;
    setView({ year, month: next.getMonth() });
  };

  const total = daysInMonth(view.year, view.month);
  const offset = firstWeekdayMon(view.year, view.month);

  return (
    <div className="rounded-2xl border border-border bg-surface-soft/80 p-3 backdrop-blur-sm">
      {/* ── Шапка: месяц-год открывает быстрый выбор ── */}
      <div className="mb-2 flex items-center gap-1">
        <button
          type="button"
          onClick={() => shift(-1)}
          aria-label="Предыдущий месяц"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-ink-muted transition duration-150 hover:bg-brand/8 hover:text-brand"
        >
          <Icon name="chevron-left" size={16} aria-hidden="true" />
        </button>

        <button
          type="button"
          onClick={() => setPicking((v) => !v)}
          aria-expanded={picking}
          className="flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-1.5 text-sm font-semibold text-ink transition duration-150 hover:bg-brand/8 hover:text-brand"
        >
          {MONTHS_NOM[view.month]} {view.year}
          <Icon
            name="chevron-down"
            size={14}
            className={`text-ink-muted transition-transform duration-150 ${picking ? "rotate-180" : ""}`}
            aria-hidden="true"
          />
        </button>

        <button
          type="button"
          onClick={() => shift(1)}
          aria-label="Следующий месяц"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-ink-muted transition duration-150 hover:bg-brand/8 hover:text-brand"
        >
          <Icon name="chevron-right" size={16} aria-hidden="true" />
        </button>
      </div>

      {picking ? (
        <div className="uc-fade-in">
          {/* Год */}
          <div className="mb-2 flex items-center justify-between gap-1 rounded-xl bg-card/60 px-1 py-1">
            <button
              type="button"
              onClick={() => setView((v) => ({ ...v, year: Math.max(YEAR_MIN, v.year - 1) }))}
              disabled={view.year <= YEAR_MIN}
              aria-label="Предыдущий год"
              className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-muted transition duration-150 hover:bg-brand/8 hover:text-brand disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-ink-muted"
            >
              <Icon name="chevron-left" size={15} aria-hidden="true" />
            </button>
            <span className="text-sm font-semibold text-ink">{view.year}</span>
            <button
              type="button"
              onClick={() => setView((v) => ({ ...v, year: Math.min(YEAR_MAX, v.year + 1) }))}
              disabled={view.year >= YEAR_MAX}
              aria-label="Следующий год"
              className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-muted transition duration-150 hover:bg-brand/8 hover:text-brand disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-ink-muted"
            >
              <Icon name="chevron-right" size={15} aria-hidden="true" />
            </button>
          </div>

          {/* Месяцы */}
          <div className="grid grid-cols-3 gap-1">
            {MONTHS_NOM.map((label, i) => {
              const on = i === view.month;
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() => { setView((v) => ({ ...v, month: i })); setPicking(false); }}
                  aria-pressed={on}
                  className={`rounded-lg py-2 text-sm font-medium transition duration-150 ${
                    on ? "bg-brand text-white" : "text-ink hover:bg-brand/8 hover:text-brand"
                  }`}
                >
                  {label.slice(0, 3)}
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="uc-fade-in grid grid-cols-7 gap-1">
          {WEEKDAYS.map((w) => (
            <div key={w} className="pb-1 text-center text-[0.6875rem] font-medium text-ink-muted">{w}</div>
          ))}
          {Array.from({ length: total }, (_, i) => i + 1).map((d) => {
            const iso = toIso({ year: view.year, month: view.month, day: d });
            const isSel = iso === value;
            const isToday = iso === today;
            const isOriginal = original?.year === view.year && original?.month === view.month && original?.day === d;
            const busy = isMockView && !isOriginal && (busyByDay.get(d)?.length ?? 0) > 0;
            return (
              <button
                key={d}
                type="button"
                onClick={() => onSelect(iso)}
                aria-pressed={isSel}
                aria-label={`${d} ${MONTHS_NOM[view.month]} ${view.year}`}
                style={{ gridColumnStart: d === 1 ? offset + 1 : undefined }}
                className={`relative flex h-9 items-center justify-center rounded-lg text-sm font-medium transition duration-150 ${
                  isSel
                    ? "bg-brand text-white"
                    : `text-ink hover:bg-brand/8 hover:text-brand ${isToday ? "ring-1 ring-inset ring-brand/50" : ""}`
                }`}
              >
                {d}
                {busy && !isSel && <span className="absolute bottom-1 h-1 w-1 rounded-full bg-brand" aria-hidden="true" />}
              </button>
            );
          })}
        </div>
      )}

      <button
        type="button"
        onClick={() => {
          const t = parseIso(today);
          setView({ year: t.year, month: t.month });
          setPicking(false);
          onSelect(today);
        }}
        className="mt-2 w-full rounded-lg py-1.5 text-xs font-medium text-ink-muted transition duration-150 hover:bg-brand/8 hover:text-brand"
      >
        Сегодня
      </button>
    </div>
  );
}
