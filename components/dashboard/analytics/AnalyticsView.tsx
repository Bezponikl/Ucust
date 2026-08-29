"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { CHANNELS } from "@/lib/channels";
import StatCard from "@/components/dashboard/StatCard";
import ReachChart from "@/components/dashboard/overview/ReachChart";
import type { ChartTab } from "@/lib/dashboard/types";
import Icon from "@/components/ui/Icon";
import type { ChannelId } from "@/lib/channels";
import {
  ANALYTICS_CHART,
  CHANNEL_POSTS,
  CHANNEL_SHARE,
  METRICS,
  PERIODS,
  TOP_POSTS,
  WORST_POSTS,
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

const fmtNum = (n: number) => n.toLocaleString("ru-RU");

/** Что означает каждая карточка — без этого «Реакции» и «Клики» читаются одинаково. */
const METRIC_HINT: Record<string, string> = {
  reach: "Сколько раз ваши публикации показали пользователям за период",
  engagement: "Лайки, комментарии и репосты по всем площадкам",
  subscribers: "Подписчики всех подключённых сообществ на конец периода",
  clicks: "Переходы по ссылкам из публикаций",
};

export default function AnalyticsView() {
  const [period, setPeriod] = useState<(typeof PERIODS)[number]>("30 дней");
  // Раскрытая площадка: по клику показываем её посты с просмотрами, репостами и лайками
  const [openChannel, setOpenChannel] = useState<ChannelId | null>(null);
  // Топ или «худшие» — обратная сторона важнее для выводов, чем ещё один топ
  const [postsMode, setPostsMode] = useState<"top" | "worst">("top");
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
      <div>
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Аналитика</h1>
        <p className="mt-0.5 text-sm text-ink-muted">Как растёт ваш бизнес в соцсетях</p>
      </div>

      {/* Метрики — они же переключатели графика */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
        {METRICS.map((m) => {
          const chartTab = CHART_OF_METRIC[m.id];
          const value = chartTab ? totals[chartTab] : m.value;
          const on = chartTab != null && chartTab === metric;

          if (!chartTab) {
            return (
              <StatCard key={m.id} icon={m.icon} iconTone={m.color} value={value} label={m.label} delta={m.delta} deltaTone={m.color} tooltip={METRIC_HINT[m.id]} />
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
              <StatCard icon={m.icon} iconTone={m.color} value={value} label={m.label} delta={m.delta} deltaTone={m.color} tooltip={METRIC_HINT[m.id]} />
            </button>
          );
        })}
      </div>

      {/* Большой график: метрику выбирают карточками выше */}
      <ReachChart
        chart={ANALYTICS_CHART}
        tab={metric}
        onTab={setMetric}
        period={period}
        periods={PERIODS}
        onPeriod={(p) => setPeriod(p as (typeof PERIODS)[number])}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 [&>*]:min-w-0">
        {/* Разбивка по каналам — строка раскрывается в статистику по постам */}
        <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
          <h2 className="text-base font-bold text-ink sm:text-lg">Охват по каналам</h2>
          <p className="mb-4 mt-0.5 text-xs text-ink-muted">Нажмите на площадку — покажем её публикации</p>
          <div className="flex flex-col gap-2">
            {CHANNEL_SHARE.map(({ id, value }) => {
              const ch = CHANNELS[id];
              const posts = CHANNEL_POSTS[id] ?? [];
              const open = openChannel === id;
              return (
                <div key={id}>
                  <button
                    type="button"
                    aria-expanded={open}
                    onClick={() => setOpenChannel(open ? null : id)}
                    className="w-full rounded-xl px-2 py-2 text-left transition hover:bg-surface-soft"
                  >
                    <span className="mb-1.5 flex items-center justify-between gap-2">
                      <span className="flex items-center gap-2 text-sm font-medium text-ink">
                        {ch.icon && ch.iconType !== "wordmark" ? (
                          <Image src={ch.icon} alt="" width={18} height={18} className="h-[1.125rem] w-[1.125rem] object-contain" aria-hidden="true" />
                        ) : (
                          <span className="h-[1.125rem] w-[1.125rem] rounded" style={{ backgroundColor: ch.colorVar }} aria-hidden="true" />
                        )}
                        {ch.label}
                      </span>
                      <span className="flex items-center gap-1.5">
                        <span className="text-sm font-semibold text-ink-muted">{value}%</span>
                        <Icon
                          name="chevron-down"
                          size={14}
                          className={`text-ink-muted transition-transform ${open ? "rotate-180" : ""}`}
                          aria-hidden="true"
                        />
                      </span>
                    </span>
                    <span className="block h-2 overflow-hidden rounded-full bg-surface-soft">
                      <span className="block h-full rounded-full bg-brand" style={{ width: `${value}%` }} />
                    </span>
                  </button>

                  {open && (
                    <div className="uc-fade-in mt-1 flex flex-col gap-1.5 rounded-xl bg-surface-soft/70 p-2.5">
                      {posts.length === 0 ? (
                        <p className="px-1 py-1.5 text-xs text-ink-muted">За период публикаций не было</p>
                      ) : (
                        posts.map((post) => (
                          <div key={post.id} className="rounded-lg bg-card px-3 py-2">
                            <p className="truncate text-sm font-medium text-ink">{post.title}</p>
                            <p className="text-xs text-ink-muted">{post.date}</p>
                            <div className="mt-1.5 flex items-center gap-4 text-xs">
                              <span className="inline-flex items-center gap-1 text-ink-muted" title="Просмотры">
                                <Icon name="eye" size={13} aria-hidden="true" />
                                <span className="font-semibold tabular-nums text-ink">{fmtNum(post.views)}</span>
                              </span>
                              <span className="inline-flex items-center gap-1 text-ink-muted" title="Репосты">
                                <Icon name="send" size={13} aria-hidden="true" />
                                <span className="font-semibold tabular-nums text-ink">{fmtNum(post.reposts)}</span>
                              </span>
                              <span className="inline-flex items-center gap-1 text-ink-muted" title="Лайки">
                                <Icon name="heart" size={13} aria-hidden="true" />
                                <span className="font-semibold tabular-nums text-ink">{fmtNum(post.likes)}</span>
                              </span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Посты: лучшие и худшие — одним переключателем */}
        <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-base font-bold text-ink sm:text-lg">
              {postsMode === "top" ? "Топ-посты" : "Худшие посты"}
            </h2>
            <div role="tablist" aria-label="Какие посты показать" className="inline-flex gap-1 rounded-xl bg-surface-soft p-1">
              {([["top", "Лучшие"], ["worst", "Худшие"]] as const).map(([id, label]) => (
                <button
                  key={id}
                  type="button"
                  role="tab"
                  aria-selected={postsMode === id}
                  onClick={() => setPostsMode(id)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                    postsMode === id ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-2.5">
            {(postsMode === "top" ? TOP_POSTS : WORST_POSTS).map((p, i) => (
              <div key={p.id} className="flex items-center gap-3 rounded-xl bg-surface-soft px-3 py-2.5">
                <span
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${
                    postsMode === "top" ? "bg-brand-tint text-brand" : "bg-brand-orange/12 text-brand-orange"
                  }`}
                >
                  {i + 1}
                </span>
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
