"use client";

import { useEffect, useId, useRef, useState } from "react";
import Icon from "@/components/ui/Icon";
import type { ChartTab } from "@/lib/dashboard/types";

const TABS: { id: ChartTab; label: string; unit: string }[] = [
  { id: "reach", label: "Охват", unit: "показов" },
  { id: "engagement", label: "Вовлечённость", unit: "реакций" },
  { id: "clicks", label: "Клики", unit: "переходов" },
];

/** Мок-ряды лежат в условных сотнях — в подписях показываем реальные значения. */
const SCALE = 100;

// Компактная запись больших чисел: 1240 → «1.2K»
function fmt(n: number) {
  const v = Math.round(n * SCALE);
  if (v >= 1000) return `${(v / 1000).toFixed(1).replace(/\.0$/, "")}K`;
  return `${v}`;
}

/** Подпись деления оси — значение уже в реальных единицах. */
function fmtAxis(v: number) {
  if (v >= 1000) return `${(v / 1000).toFixed(v % 1000 === 0 ? 0 : 1).replace(/\.0$/, "")}K`;
  return `${Math.round(v)}`;
}

const fmtFull = (n: number) => Math.round(n * SCALE).toLocaleString("ru-RU");

/**
 * Ровная шкала: шаг берём из ряда 1 / 2 / 2.5 / 5 × 10ⁿ, чтобы подписи шли
 * «10 · 20 · 30», а не «1.4 · 5.7 · 50» от произвольного максимума ряда.
 */
function niceScale(max: number, count = 4) {
  if (!(max > 0)) return { top: 1, ticks: [0, 1] };
  const rawStep = max / count;
  const mag = 10 ** Math.floor(Math.log10(rawStep));
  const norm = rawStep / mag;
  const step = (norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 2.5 ? 2.5 : norm <= 5 ? 5 : 10) * mag;
  const top = Math.ceil(max / step) * step;
  const ticks: number[] = [];
  for (let v = 0; v <= top + step / 1000; v += step) ticks.push(Number(v.toFixed(6)));
  return { top, ticks };
}

/** Дата точки: последняя — сегодня, шаг равен периоду, делённому на число точек. */
function pointDate(i: number, n: number, period: string) {
  const days = parseInt(period, 10) || 30;
  const back = ((n - 1 - i) * days) / (n - 1);
  const d = new Date();
  d.setDate(d.getDate() - Math.round(back));
  return d.toLocaleDateString("ru-RU", { day: "numeric", month: "long" });
}

type ChartKind = "line" | "bar";

const KINDS: { id: ChartKind; icon: "chart-line" | "chart-bar"; label: string }[] = [
  { id: "line", icon: "chart-line", label: "Линейный график" },
  { id: "bar", icon: "chart-bar", label: "Столбчатый график" },
];

export default function ReachChart({
  chart,
  tab: tabProp,
  onTab,
  period = "30 дней",
  periods,
  onPeriod,
  showTabs,
}: {
  chart: Record<ChartTab, number[]>;
  /** Управление извне: на аналитике метрику выбирают карточками над графиком. */
  tab?: ChartTab;
  onTab?: (t: ChartTab) => void;
  period?: string;
  /** Период живёт в самом графике — переключать его удобнее рядом с данными. */
  periods?: readonly string[];
  onPeriod?: (p: string) => void;
  /** Свой переключатель метрик нужен только там, где снаружи его нет. */
  showTabs?: boolean;
}) {
  const [tabState, setTabState] = useState<ChartTab>("reach");
  const tab = tabProp ?? tabState;
  const setTab = (t: ChartTab) => (onTab ? onTab(t) : setTabState(t));
  // Карточки метрик над графиком уже переключают ряд, поэтому такой же
  // переключатель внутри графика был бы вторым органом управления тем же.
  const tabsVisible = showTabs ?? onTab == null;

  const [kind, setKind] = useState<ChartKind>("line");
  const [active, setActive] = useState<number | null>(null);
  const gid = useId().replace(/[:]/g, "");

  // Раньше viewBox был фиксированный 680×240, а контейнер — широкий и низкий.
  // preserveAspectRatio вписывал график по высоте и оставлял пустые поля по бокам:
  // линия жалась к середине, а метка пика упиралась в край нарисованной области.
  // Меряем контейнер и делаем viewBox равным его пиксельному размеру — 1:1.
  const boxRef = useRef<HTMLDivElement>(null);
  const [box, setBox] = useState({ w: 680, h: 240 });

  useEffect(() => {
    const el = boxRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      const r = entry.contentRect;
      if (r.width > 0 && r.height > 0) setBox({ w: Math.round(r.width), h: Math.round(r.height) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const active_tab = TABS.find((t) => t.id === tab)!;
  const series = chart[tab];
  const n = series.length;
  const max = Math.max(...series);
  const peakIdx = series.indexOf(max);

  const latest = series[n - 1];
  const first = series[0];
  const delta = first ? Math.round(((latest - first) / first) * 100) : 0;
  const avg = series.reduce((a, b) => a + b, 0) / n;
  const total = series.reduce((a, b) => a + b, 0);

  // Геометрия в координатах viewBox (= пиксели контейнера)
  const W = box.w;
  const H = box.h;
  const padL = 46; // левый жёлоб под подписи оси значений
  const padR = 14;
  const padT = 22;
  const padB = 26;
  const plotW = Math.max(W - padL - padR, 10);
  const plotH = Math.max(H - padT - padB, 10);

  // Шкалу считаем в реальных единицах — оттого и деления выходят круглыми
  const scale = niceScale(max * SCALE);
  const top = scale.top / SCALE;

  const step = plotW / (n - 1);
  const px = (i: number) => padL + i * step;
  const py = (v: number) => padT + (1 - v / top) * plotH;

  // У столбцов своя разбивка: точки стоят по центрам полос, иначе крайние
  // столбцы наполовину уходят за край области графика.
  const band = plotW / n;
  const cx = (i: number) => (kind === "bar" ? padL + (i + 0.5) * band : px(i));

  const linePts = series.map((v, i) => `${px(i).toFixed(1)},${py(v).toFixed(1)}`).join(" ");
  const areaPts = `${padL},${padT + plotH} ${linePts} ${padL + plotW},${padT + plotH}`;

  // Столбцы уже полосы — между ними остаётся воздух
  const barW = Math.max(Math.min(band * 0.62, 34), 4);

  const days = parseInt(period, 10) || 30;
  const captions = [
    { i: 0, text: `${days} дн. назад` },
    { i: Math.floor((n - 1) / 2), text: `${Math.round(days / 2)} дн.` },
    { i: n - 1, text: "сегодня" },
  ];

  // Подсказку рисуем HTML-ом поверх svg: в ней помещаются и дата, и единицы
  const tipLeft = active === null ? 0 : Math.min(Math.max(cx(active), 78), Math.max(W - 78, 78));
  const tipTop = active === null ? 0 : Math.max(py(series[active]) - 12, 6);

  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
      {/* Шапка: значение и дельта слева, управление данными справа */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">
            {active_tab.label} · {period}
          </p>
          {/* Крупное число — сумма за период; она же стоит в карточке метрики */}
          <div className="mt-1 flex items-baseline gap-2.5">
            <span className="font-display text-3xl font-extrabold text-ink sm:text-[2.125rem]">
              {fmt(total)}
            </span>
            <span
              className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-semibold ${
                delta >= 0 ? "bg-success/10 text-success" : "bg-brand-pink/10 text-brand-pink"
              }`}
            >
              {delta >= 0 ? "↑" : "↓"} {Math.abs(delta)}%
            </span>
            <span className="text-xs text-ink-muted">{active_tab.unit} за период</span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 sm:justify-end">
          {/* Период — здесь же, у самих данных, а не в шапке страницы */}
          {periods && onPeriod && (
            <div role="tablist" aria-label="Период" className="flex gap-1 rounded-xl bg-surface-soft p-1">
              {periods.map((p) => (
                <button
                  key={p}
                  type="button"
                  role="tab"
                  aria-selected={period === p}
                  onClick={() => {
                    onPeriod(p);
                    setActive(null);
                  }}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                    period === p ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          )}

          {/* Вид графика: линия показывает тренд, столбцы — сравнение дней */}
          <div role="group" aria-label="Вид графика" className="flex gap-1 rounded-xl bg-surface-soft p-1">
            {KINDS.map((k) => (
              <button
                key={k.id}
                type="button"
                aria-pressed={kind === k.id}
                aria-label={k.label}
                title={k.label}
                onClick={() => setKind(k.id)}
                className={`flex h-7 w-9 items-center justify-center rounded-lg transition ${
                  kind === k.id ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
                }`}
              >
                <Icon name={k.icon} size={16} aria-hidden="true" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Свой переключатель метрик — только там, где снаружи его нет */}
      {tabsVisible && (
        <div className="mt-4 flex justify-center">
          <div role="tablist" aria-label="Метрика графика" className="inline-flex gap-1 rounded-xl bg-surface-soft p-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                role="tab"
                aria-selected={tab === t.id}
                title={`Показать на графике: ${t.label} (${t.unit})`}
                onClick={() => {
                  setTab(t.id);
                  setActive(null);
                }}
                className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
                  tab === t.id ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* График */}
      <div ref={boxRef} className="relative mt-4 h-48 w-full sm:h-56">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width="100%"
        height="100%"
        preserveAspectRatio="none"
        role="img"
        aria-label={`График «${active_tab.label}»: с ${fmt(first)} до ${fmt(latest)}`}
        onMouseLeave={() => setActive(null)}
      >
        <defs>
          <linearGradient id={`area-${gid}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--brand)" stopOpacity="0.28" />
            <stop offset="100%" stopColor="var(--brand)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Сетка с ровным шагом; подписи — в левом жёлобе, как на биржевых графиках */}
        {scale.ticks.map((real) => {
          const y = padT + (1 - real / scale.top) * plotH;
          const bottom = real === 0;
          return (
            <g key={real}>
              <line
                x1={padL}
                x2={padL + plotW}
                y1={y}
                y2={y}
                stroke="var(--border)"
                strokeWidth="1"
                strokeDasharray={bottom ? "0" : "3 5"}
              />
              <text x={padL - 8} y={y} textAnchor="end" dominantBaseline="middle" fontSize="10" fill="var(--ink-muted)">
                {fmtAxis(real)}
              </text>
            </g>
          );
        })}

        {/* Группа перерисовывается при смене метрики или вида — отсюда анимация отрисовки */}
        <g key={`${tab}-${kind}`}>
          {kind === "line" ? (
            <>
              <polygon points={areaPts} fill={`url(#area-${gid})`} className="reach-area" />
              <polyline
                points={linePts}
                fill="none"
                stroke="var(--brand)"
                strokeWidth="2.5"
                strokeLinejoin="round"
                strokeLinecap="round"
                className="reach-line"
              />

              {/* Метка пика: держим внутри области графика, иначе съезжает за край */}
              <g>
                <circle cx={px(peakIdx)} cy={py(max)} r="3.5" fill="var(--brand)" stroke="var(--card)" strokeWidth="2" />
                <g
                  transform={`translate(${Math.min(Math.max(px(peakIdx), padL + 34), padL + plotW - 34)}, ${Math.max(py(max) - 16, padT - 4)})`}
                >
                  <rect x="-32" y="-10" width="64" height="20" rx="10" fill="var(--brand)" />
                  <text x="0" y="0.5" textAnchor="middle" dominantBaseline="middle" fontSize="12" fontWeight="700" fill="#fff">
                    пик {fmt(max)}
                  </text>
                </g>
              </g>
            </>
          ) : (
            series.map((v, i) => {
              const y = py(v);
              return (
                <rect
                  key={i}
                  x={cx(i) - barW / 2}
                  y={y}
                  width={barW}
                  height={Math.max(padT + plotH - y, 1)}
                  rx={Math.min(4, barW / 2)}
                  fill="var(--brand)"
                  opacity={active === null || active === i ? 1 : 0.42}
                  style={{ transition: "opacity 150ms" }}
                />
              );
            })
          )}
        </g>

        {/* Наведение: направляющая, а в линейном виде ещё и точка на кривой */}
        {active !== null && (
          <g pointerEvents="none">
            <line
              x1={cx(active)}
              x2={cx(active)}
              y1={padT}
              y2={padT + plotH}
              stroke="var(--brand)"
              strokeWidth="1"
              strokeDasharray="3 4"
              opacity="0.5"
            />
            {kind === "line" && (
              <circle cx={px(active)} cy={py(series[active])} r="4.5" fill="var(--brand)" stroke="var(--card)" strokeWidth="2.5" />
            )}
          </g>
        )}

        {/* Прозрачные зоны наведения по колонкам */}
        {series.map((_, i) => (
          <rect
            key={i}
            x={kind === "bar" ? padL + i * band : padL + (i - 0.5) * step}
            y={padT}
            width={kind === "bar" ? band : step}
            height={plotH}
            fill="transparent"
            onMouseEnter={() => setActive(i)}
            // На телефоне ховера нет: значение показываем по касанию колонки
            onPointerDown={() => setActive(i)}
          />
        ))}

        {/* Подписи оси X */}
        {captions.map((c) => (
          <text
            key={c.text}
            x={Math.min(Math.max(cx(c.i), padL), W - 24)}
            y={H - 8}
            textAnchor={c.i === 0 ? "start" : c.i === n - 1 ? "end" : "middle"}
            fontSize="11"
            fill="var(--ink-muted)"
          >
            {c.text}
          </text>
        ))}
      </svg>

      {/* Подсказка по точке: точное значение и дата — как на биржевых графиках */}
      {active !== null && (
        <div
          role="status"
          className="uc-fade-in pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full rounded-xl border border-border bg-card px-3 py-2 text-center shadow-lift"
          style={{ left: tipLeft, top: tipTop }}
        >
          <p className="font-display whitespace-nowrap text-sm font-bold leading-tight text-ink">
            {fmtFull(series[active])}{" "}
            <span className="text-xs font-medium text-ink-muted">{active_tab.unit}</span>
          </p>
          <p className="mt-0.5 whitespace-nowrap text-[0.6875rem] leading-tight text-ink-muted">
            {pointDate(active, n, period)}
          </p>
        </div>
      )}
      </div>

      {/* Мини-сводка */}
      <div className="mt-4 grid grid-cols-3 gap-3 border-t border-border pt-4">
        {[
          { k: "Пик за день", v: fmt(max), hint: `Лучший день периода по метрике «${active_tab.label}»` },
          { k: "В среднем в день", v: fmt(avg), hint: `Сумма за период, делённая на число дней (${n})` },
          { k: "Сегодня", v: fmt(latest), hint: "Последний день периода" },
        ].map((s) => (
          <div key={s.k}>
            {/* Подсказка объясняет, откуда цифра: «в среднем» иначе читается по-разному */}
            <p className="flex items-center gap-1 text-xs text-ink-muted">
              {s.k}
              <span
                role="img"
                aria-label={s.hint}
                title={s.hint}
                className="inline-flex h-3.5 w-3.5 cursor-help items-center justify-center rounded-full border border-border text-[0.5625rem] font-bold leading-none text-ink-muted"
              >
                ?
              </span>
            </p>
            <p className="font-display text-lg font-bold text-ink">{s.v}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
