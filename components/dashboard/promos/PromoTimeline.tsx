"use client";

import { useMemo } from "react";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import {
  PROMO_STATUS_LABEL,
  PROMO_TYPE,
  promoPeriod,
  type Promo,
  type PromoStatus,
} from "@/lib/dashboard/promos";
import { MONTHS_SHORT, parseIso, todayIso } from "@/lib/dashboard/date";

const BAR_COLOR: Record<PromoStatus, string> = {
  active: "bg-success",
  scheduled: "bg-brand",
  finished: "bg-ink-muted/55",
};

/** ISO → номер дня от эпохи: считаем в целых днях, часовые пояса не мешают. */
function dayNumber(iso: string): number {
  const { year, month, day } = parseIso(iso);
  return Math.floor(Date.UTC(year, month, day) / 86_400_000);
}

/** Подписи месяцев на шкале: где начинается каждый месяц диапазона. */
function monthTicks(fromDay: number, toDay: number) {
  const ticks: { at: number; label: string }[] = [];
  const start = new Date(fromDay * 86_400_000);
  let y = start.getUTCFullYear();
  let m = start.getUTCMonth();
  // первый тик — начало месяца, в который попадает левый край шкалы
  for (let guard = 0; guard < 48; guard += 1) {
    const at = Math.floor(Date.UTC(y, m, 1) / 86_400_000);
    if (at > toDay) break;
    if (at >= fromDay) ticks.push({ at, label: MONTHS_SHORT[m] ?? "" });
    m += 1;
    if (m > 11) { m = 0; y += 1; }
  }
  return ticks;
}

/**
 * Шкала-таймлайн акций: у каждой строки полоса на общей оси дат, поэтому
 * пересечения периодов видно сразу — какие акции идут одновременно и где
 * в календаре остались дыры.
 */
export default function PromoTimeline({ promos }: { promos: Promo[] }) {
  const scale = useMemo(() => {
    if (promos.length === 0) return null;
    const starts = promos.map((p) => dayNumber(p.start));
    const ends = promos.map((p) => dayNumber(p.end));
    const min = Math.min(...starts);
    const max = Math.max(...ends);
    // поля по краям, чтобы крайние полосы не липли к границам
    const pad = Math.max(2, Math.round((max - min) * 0.04));
    const from = min - pad;
    const to = max + pad;
    const span = Math.max(1, to - from);
    return { from, to, span, ticks: monthTicks(from, to) };
  }, [promos]);

  if (!scale) return null;

  const pctOf = (day: number) => ((day - scale.from) / scale.span) * 100;
  const today = dayNumber(todayIso());
  const todayPct = pctOf(today);
  const todayVisible = todayPct >= 0 && todayPct <= 100;

  return (
    <section
      aria-label="Периоды акций на шкале дат"
      className="rounded-[20px] border border-border/70 bg-card/80 p-4 sm:p-5"
    >
      <div className="mb-3 flex items-center gap-2">
        <Icon name="calendar" size={15} className="text-ink-muted" aria-hidden="true" />
        <h2 className="text-sm font-semibold text-ink">Периоды акций</h2>
        <span className="text-xs text-ink-muted">видно пересечения и пустые недели</span>
      </div>

      {/* Ось: подписи месяцев по общей сетке */}
      <div className="relative mb-2 h-4 select-none">
        {scale.ticks.map((t) => (
          <span
            key={t.at}
            className="absolute top-0 -translate-x-1/2 text-[0.6875rem] font-medium text-ink-muted"
            style={{ left: `${pctOf(t.at)}%` }}
          >
            {t.label}
          </span>
        ))}
      </div>

      <div className="relative">
        {/* Разделители месяцев и метка «сегодня» — сквозь все строки */}
        <div className="pointer-events-none absolute inset-0" aria-hidden="true">
          {scale.ticks.map((t) => (
            <span key={t.at} className="absolute inset-y-0 w-px bg-border/60" style={{ left: `${pctOf(t.at)}%` }} />
          ))}
          {todayVisible && (
            <span className="absolute inset-y-0 w-px bg-brand/70" style={{ left: `${todayPct}%` }} />
          )}
        </div>

        <ul className="relative flex flex-col gap-1.5">
          {promos.map((p) => {
            const left = pctOf(dayNumber(p.start));
            // конец включительно: акция «1–3 мар» занимает три дня, а не два
            const right = pctOf(dayNumber(p.end) + 1);
            const width = Math.max(1.5, right - left);
            // Короткая акция в полосу не помещается — подписываем её рядом,
            // иначе на шкале остаётся безымянный кружок.
            const labelInside = width >= 14;
            const title = `${p.title} · ${PROMO_STATUS_LABEL[p.status]} · ${promoPeriod(p)}`;
            return (
              <li key={p.id} className="relative h-9">
                <Link
                  href={`/dashboard/promos/${p.id}`}
                  title={title}
                  aria-label={title}
                  className="absolute inset-y-1 flex items-center gap-2 focus-visible:outline-none"
                  style={{
                    left: `${left}%`,
                    // подпись снаружи не должна упираться в правый край шкалы
                    right: labelInside ? undefined : 0,
                    width: labelInside ? `${width}%` : undefined,
                  }}
                >
                  <span
                    className={`flex h-full shrink-0 items-center gap-1.5 overflow-hidden rounded-full px-2.5 text-xs font-semibold text-white transition group-hover:brightness-110 ${BAR_COLOR[p.status]}`}
                    style={labelInside ? { width: "100%" } : { width: `${(width / Math.max(0.01, 100 - left)) * 100}%`, minWidth: "1.5rem" }}
                  >
                    <Icon name={PROMO_TYPE[p.type].icon} size={12} className="shrink-0 opacity-90" aria-hidden="true" />
                    {labelInside && <span className="truncate">{p.title}</span>}
                  </span>
                  {!labelInside && (
                    <span className="truncate text-xs font-medium text-ink">{p.title}</span>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[0.6875rem] text-ink-muted">
        {(["active", "scheduled", "finished"] as PromoStatus[]).map((s) => (
          <span key={s} className="inline-flex items-center gap-1.5">
            <span className={`h-2 w-2 rounded-full ${BAR_COLOR[s]}`} aria-hidden="true" />
            {PROMO_STATUS_LABEL[s]}
          </span>
        ))}
        {todayVisible && (
          <span className="inline-flex items-center gap-1.5">
            <span className="h-3 w-px bg-brand/70" aria-hidden="true" /> сегодня
          </span>
        )}
      </div>
    </section>
  );
}
