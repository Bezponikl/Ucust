"use client";

import { useState } from "react";
import Image from "next/image";
import { CHANNELS } from "@/lib/channels";
import type { AccentColor } from "@/lib/dashboard/types";
import ReachChart from "@/components/dashboard/overview/ReachChart";
import {
  ANALYTICS_CHART,
  CHANNEL_SHARE,
  METRICS,
  PERIODS,
  TOP_POSTS,
} from "@/lib/dashboard/analytics";

const DELTA_TINT: Record<AccentColor, string> = {
  brand: "text-brand",
  purple: "text-brand-purple",
  pink: "text-brand-pink",
  orange: "text-brand-orange",
  success: "text-success",
};

export default function AnalyticsView() {
  const [period, setPeriod] = useState<(typeof PERIODS)[number]>("30 дней");

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink sm:text-3xl">Аналитика</h1>
          <p className="mt-1 text-sm text-ink-muted">Как растёт ваш бизнес в соцсетях</p>
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

      {/* Метрики */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
        {METRICS.map((m) => (
          <div key={m.id} className="rounded-[20px] border border-border bg-card p-4 shadow-soft sm:p-5">
            <p className="text-sm text-ink-muted">{m.label}</p>
            <p className="mt-1 font-display text-2xl font-extrabold text-ink sm:text-3xl">{m.value}</p>
            <p className={`mt-0.5 text-xs font-semibold ${DELTA_TINT[m.color]}`}>{m.delta}</p>
          </div>
        ))}
      </div>

      {/* Большой график */}
      <ReachChart chart={ANALYTICS_CHART} />

      <div className="grid gap-6 lg:grid-cols-2">
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
                        <Image src={ch.icon} alt="" width={18} height={18} className="h-[18px] w-[18px] object-contain" aria-hidden="true" />
                      ) : (
                        <span className="h-[18px] w-[18px] rounded" style={{ backgroundColor: ch.colorVar }} aria-hidden="true" />
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
