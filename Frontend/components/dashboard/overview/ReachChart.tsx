"use client";

import { useState } from "react";
import type { ChartTab } from "@/lib/dashboard/types";

const TABS: { id: ChartTab; label: string }[] = [
  { id: "reach", label: "Охват" },
  { id: "engagement", label: "Вовлечённость" },
  { id: "clicks", label: "Клики" },
];

export default function ReachChart({ chart }: { chart: Record<ChartTab, number[]> }) {
  const [tab, setTab] = useState<ChartTab>("reach");
  const series = chart[tab];
  const max = Math.max(...series, 1);
  const W = 100;
  const H = 40;
  const points = series
    .map((v, i) => {
      const x = (i / (series.length - 1)) * W;
      const y = H - (v / max) * (H - 4) - 2;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");

  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-base font-bold text-ink sm:text-lg">Охват за последние 30 дней</h2>
        <div role="tablist" className="flex gap-1 rounded-xl bg-surface-soft p-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={tab === t.id}
              onClick={() => setTab(t.id)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                tab === t.id ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        className="mt-5 h-40 w-full"
        role="img"
        aria-label={`График: ${TABS.find((t) => t.id === tab)?.label}`}
      >
        {[0.25, 0.5, 0.75].map((g) => (
          <line key={g} x1="0" x2={W} y1={H * g} y2={H * g} className="stroke-border" strokeWidth="0.3" />
        ))}
        <polyline
          points={points}
          fill="none"
          className="stroke-brand"
          strokeWidth="1.2"
          strokeLinejoin="round"
          strokeLinecap="round"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
    </div>
  );
}
