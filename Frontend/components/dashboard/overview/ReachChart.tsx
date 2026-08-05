"use client";

import { useId, useState } from "react";
import type { ChartTab } from "@/lib/dashboard/types";

const TABS: { id: ChartTab; label: string; unit: string }[] = [
  { id: "reach", label: "Охват", unit: "показов" },
  { id: "engagement", label: "Вовлечённость", unit: "реакций" },
  { id: "clicks", label: "Клики", unit: "переходов" },
];

// Компактная запись больших чисел: 1240 → «1.2K»
function fmt(n: number) {
  const v = Math.round(n * 100); // мок-данные — усл. масштаб ×100
  if (v >= 1000) return `${(v / 1000).toFixed(1).replace(/\.0$/, "")}K`;
  return `${v}`;
}

export default function ReachChart({
  chart,
  tab: tabProp,
  onTab,
  period = "30 дней",
}: {
  chart: Record<ChartTab, number[]>;
  /** Управление извне: на аналитике метрику выбирают карточками над графиком. */
  tab?: ChartTab;
  onTab?: (t: ChartTab) => void;
  period?: string;
}) {
  const [tabState, setTabState] = useState<ChartTab>("reach");
  const controlled = tabProp != null;
  const tab = tabProp ?? tabState;
  const setTab = (t: ChartTab) => (onTab ? onTab(t) : setTabState(t));

  const [active, setActive] = useState<number | null>(null);
  const gid = useId().replace(/[:]/g, "");

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

  // Геометрия в координатах viewBox
  const W = 680;
  const H = 240;
  const padL = 14;
  const padR = 14;
  const padT = 26;
  const padB = 26;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;
  const top = max * 1.08 || 1; // немного «воздуха» над пиком

  const px = (i: number) => padL + (i / (n - 1)) * plotW;
  const py = (v: number) => padT + (1 - v / top) * plotH;

  const linePts = series.map((v, i) => `${px(i).toFixed(1)},${py(v).toFixed(1)}`).join(" ");
  const areaPts = `${padL},${padT + plotH} ${linePts} ${padL + plotW},${padT + plotH}`;

  const captions = [
    { i: 0, text: "4 нед. назад" },
    { i: Math.floor((n - 1) / 2), text: "2 нед." },
    { i: n - 1, text: "сегодня" },
  ];

  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
      {/* Шапка: значение + дельта слева, переключатель справа */}
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

        {!controlled && (
          <div role="tablist" className="flex gap-1 self-start rounded-xl bg-surface-soft p-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                role="tab"
                aria-selected={tab === t.id}
                onClick={() => {
                  setTab(t.id);
                  setActive(null);
                }}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                  tab === t.id ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* График */}
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="mt-4 h-48 w-full sm:h-56"
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

        {/* Горизонтальные линии сетки + подписи значений оси Y */}
        {[0, 0.5, 1].map((g) => {
          const y = padT + g * plotH;
          const val = top * (1 - g); // g=0 → верх (max), g=1 → низ (0)
          return (
            <g key={g}>
              <line
                x1={padL}
                x2={padL + plotW}
                y1={y}
                y2={y}
                stroke="var(--border)"
                strokeWidth="1"
                strokeDasharray={g === 1 ? "0" : "3 5"}
              />
              <text x={padL} y={y - 4} fontSize="10" fill="var(--ink-muted)">
                {fmt(val)}
              </text>
            </g>
          );
        })}

        {/* Ключевая группа перерисовывается при смене вкладки (даёт анимацию отрисовки) */}
        <g key={tab}>
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
        </g>

        {/* Ховер: направляющая + активная точка + подсказка */}
        {active !== null && (
          <g pointerEvents="none">
            <line x1={px(active)} x2={px(active)} y1={padT} y2={padT + plotH} stroke="var(--brand)" strokeWidth="1" strokeDasharray="3 4" opacity="0.5" />
            <circle cx={px(active)} cy={py(series[active])} r="4.5" fill="var(--brand)" stroke="var(--card)" strokeWidth="2.5" />
            <g transform={`translate(${Math.min(Math.max(px(active), 38), W - 38)}, ${Math.max(py(series[active]) - 30, 14)})`}>
              <rect x="-36" y="-14" width="72" height="26" rx="8" fill="var(--ink)" />
              <text x="0" y="-1" textAnchor="middle" dominantBaseline="middle" fontSize="13" fontWeight="700" fill="#fff">
                {fmt(series[active])}
              </text>
            </g>
          </g>
        )}

        {/* Прозрачные зоны наведения по колонкам */}
        {series.map((_, i) => (
          <rect
            key={i}
            x={padL + (i - 0.5) * (plotW / (n - 1))}
            y={padT}
            width={plotW / (n - 1)}
            height={plotH}
            fill="transparent"
            onMouseEnter={() => setActive(i)}
          />
        ))}

        {/* Подписи оси X */}
        {captions.map((c) => (
          <text
            key={c.text}
            x={Math.min(Math.max(px(c.i), 24), W - 24)}
            y={H - 8}
            textAnchor={c.i === 0 ? "start" : c.i === n - 1 ? "end" : "middle"}
            fontSize="11"
            fill="var(--ink-muted)"
          >
            {c.text}
          </text>
        ))}
      </svg>

      {/* Мини-сводка */}
      <div className="mt-4 grid grid-cols-3 gap-3 border-t border-border pt-4">
        {[
          { k: "Пик за день", v: fmt(max) },
          { k: "В среднем в день", v: fmt(avg) },
          { k: "Сегодня", v: fmt(latest) },
        ].map((s) => (
          <div key={s.k}>
            <p className="text-xs text-ink-muted">{s.k}</p>
            <p className="font-display text-lg font-bold text-ink">{s.v}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
