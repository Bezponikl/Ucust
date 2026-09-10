"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { CHANNELS } from "@/lib/channels";
import StatCard from "@/components/dashboard/StatCard";
import ReachChart from "@/components/dashboard/overview/ReachChart";
import type { ChartTab } from "@/lib/dashboard/types";
import {
  ANALYTICS_CHART,
  CHANNEL_SHARE,
  METRICS,
  PERIODS,
  TOP_POSTS,
} from "@/lib/dashboard/analytics";

/** У подписчиков своего ряда нет — карточка остаётся просто показателем. */
const CHART_OF_METRIC: Record<string, ChartTab | undefined> = {
  reach: "reach",
  engagement: "engagement",
  clicks: "clicks",
  subscribers: undefined,
};

/** Компактная запись: 92 300 → «92.3K» (тот же масштаб, что у графика). */
const fmtK = (n: number) => {
  const v = Math.round(n * 100);
  return v >= 1000 ? `${(v / 1000).toFixed(1).replace(/\.0$/, "")}K` : `${v}`;
};

const sum = (arr: number[]) => arr.reduce((a, b) => a + b, 0);

export default function AnalyticsView() {
  const [period, setPeriod] = useState<(typeof PERIODS)[number]>("30 дней");
  // Карточка метрики и есть переключатель графика — отдельных вкладок больше нет
  const [metric, setMetric] = useState<ChartTab>("reach");

  // Значения карточек считаем из тех же рядов, что рисует график — цифры сходятся
  const totals: Record<ChartTab, string> = {
    reach: fmtK(sum(ANALYTICS_CHART.reach)),
    engagement: fmtK(sum(ANALYTICS_CHART.engagement)),
    clicks: fmtK(sum(ANALYTICS_CHART.clicks)),
  };

  // Ссылка из дашборда может открыть нужную метрику: ?metric=engagement
  useEffect(() => {
    const m = new URLSearchParams(window.location.search).get("metric");
    /* eslint-disable react-hooks/set-state-in-effect */
    if (m === "reach" || m === "engagement" || m === "clicks") setMetric(m);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-ink sm:text-2xl">Аналитика</h1>
          <p className="mt-0.5 text-sm text-ink-muted">Как растёт ваш бизнес в соцсетях</p>
        </div>
        <div role="tablist" className="flex gap-1 self-start rounded-xl bg-surface-soft p-1">
          {PERIODS.map((p) => (
            <button
              key={p}
              type="button"
              role="tab"
              aria-selected={period === p}
              onClick={() => setPeriod(p)}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                period === p ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Метрики — они же переключатели графика */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
        {METRICS.map((m) => {
          const chartTab = CHART_OF_METRIC[m.id];
          const value = chartTab ? totals[chartTab] : m.value;
          const on = chartTab != null && chartTab === metric;

          if (!chartTab) {
            return (
              <StatCard key={m.id} icon={m.icon} iconTone={m.color} value={value} label={m.label} delta={m.delta} deltaTone={m.color} />
            );
          }

          return (
            <button
              key={m.id}
              type="button"
              aria-pressed={on}
              onClick={() => setMetric(chartTab)}
              className={`rounded-[20px] text-left outline-none transition duration-200 focus-visible:ring-2 focus-visible:ring-brand/50 ${
                on ? "ring-2 ring-brand/60" : "opacity-90 hover:opacity-100"
              }`}
            >
              <StatCard icon={m.icon} iconTone={m.color} value={value} label={m.label} delta={m.delta} deltaTone={m.color} />
            </button>
          );
        })}
      </div>

      {/* Большой график: метрику выбирают карточками выше */}
      <ReachChart chart={ANALYTICS_CHART} tab={metric} onTab={setMetric} period={period} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 [&>*]:min-w-0">
        {/* Разбивка по каналам */}
        <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
          <h2 className="mb-4 text-base font-bold text-ink sm:text-lg">Охват по каналам</h2>
          <div className="flex flex-col gap-4">
            {CHANNEL_SHARE.map(({ id, value }) => {
              const ch = CHANNELS[id];
              return (
                <div key={id}>
                  <div className="mb-1.5 flex items-center justify-between">
                    <span className="flex items-center gap-2 text-sm font-medium text-ink">
                      {ch.icon && ch.iconType !== "wordmark" ? (
                        <Image src={ch.icon} alt="" width={18} height={18} className="h-[1.125rem] w-[1.125rem] object-contain" aria-hidden="true" />
                      ) : (
                        <span className="h-[1.125rem] w-[1.125rem] rounded" style={{ backgroundColor: ch.colorVar }} aria-hidden="true" />
                      )}
                      {ch.label}
                    </span>
                    <span className="text-sm font-semibold text-ink-muted">{value}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-surface-soft">
                    <div className="h-full rounded-full bg-brand" style={{ width: `${value}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Топ-посты */}
        <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
          <h2 className="mb-4 text-base font-bold text-ink sm:text-lg">Топ-посты</h2>
          <div className="flex flex-col gap-2.5">
            {TOP_POSTS.map((p, i) => (
              <div key={p.id} className="flex items-center gap-3 rounded-xl bg-surface-soft px-3 py-2.5">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-brand-tint text-xs font-bold text-brand">{i + 1}</span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-ink">{p.title}</p>
                  <p className="text-xs text-ink-muted">{p.date} · {p.views} просмотров</p>
                </div>
                <div className="shrink-0 text-right">
                  <p className="text-sm font-semibold text-ink">{p.er}</p>
                  <p className="text-xs text-ink-muted">вовлечённость</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
