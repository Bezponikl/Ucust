"use client";

import { motion } from "framer-motion";
import Icon from "./ui/Icon";
import type { IconName } from "@/lib/icons/solar";

const NAV: { icon: IconName; active: boolean }[] = [
  { icon: "grid", active: false },
  { icon: "calendar", active: true },
  { icon: "edit", active: false },
  { icon: "bar-chart", active: false },
  { icon: "settings", active: false },
];

type Post = { ch: string; color: string; label: string };

const DAYS: { day: string; date: number; posts: Post[] }[] = [
  { day: "Пн", date: 12, posts: [{ ch: "vk", color: "var(--channel-vk)", label: "Акция дня" }] },
  {
    day: "Вт",
    date: 13,
    posts: [
      { ch: "tg", color: "var(--channel-telegram)", label: "Раф −20%" },
      { ch: "ok", color: "var(--channel-ok)", label: "Анонс" },
    ],
  },
  { day: "Ср", date: 14, posts: [{ ch: "max", color: "var(--channel-max)", label: "Меню" }] },
  {
    day: "Чт",
    date: 15,
    posts: [{ ch: "vk", color: "var(--channel-vk)", label: "Сторис" }],
  },
  {
    day: "Пт",
    date: 16,
    posts: [
      { ch: "tg", color: "var(--channel-telegram)", label: "Розыгрыш" },
      { ch: "max", color: "var(--channel-max)", label: "Отзыв" },
    ],
  },
];

const BARS = [42, 64, 51, 78, 60, 92, 71];

export default function ProductMockup() {
  return (
    <div className="flex h-full w-full flex-col overflow-hidden rounded-[20px] border border-border bg-card text-left shadow-soft">
      {/* окно-хром */}
      <div className="flex items-center gap-2 border-b border-border bg-surface-soft px-4 py-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
        <span className="font-display mx-auto translate-x-[-14px] text-[0.6875rem] text-ink-muted">
          UCust · Контент-план
        </span>
      </div>

      <div className="flex min-h-0 flex-1">
        {/* сайдбар */}
        <div className="flex w-12 shrink-0 flex-col items-center gap-1 border-r border-border bg-surface-soft py-3">
          <span className="mb-2 flex h-7 w-7 items-center justify-center rounded-lg bg-brand text-[0.6875rem] font-bold text-white">
            U
          </span>
          {NAV.map(({ icon, active }, i) => (
            <span
              key={i}
              className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                active ? "bg-brand-tint text-brand" : "text-ink-muted"
              }`}
            >
              <Icon name={icon} size={16} aria-hidden="true" />
            </span>
          ))}
        </div>

        {/* основная область */}
        <div className="flex min-w-0 flex-1 flex-col p-3 sm:p-4">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-ink">Эта неделя</span>
              <span className="rounded-full bg-brand-tint px-2 py-0.5 text-[0.625rem] font-semibold text-brand">
                7 постов
              </span>
            </div>
            <span className="inline-flex items-center gap-1 rounded-full bg-brand px-2.5 py-1 text-[0.625rem] font-semibold text-white">
              <Icon name="sparkles" size={10} aria-hidden="true" />
              Сгенерировать
            </span>
          </div>

          {/* мини-календарь */}
          <div className="grid grid-cols-4 gap-1.5 sm:grid-cols-5">
            {DAYS.map((d, di) => (
              <div
                key={d.day}
                className={`flex-col rounded-lg bg-surface-soft p-1.5 ${
                  di === 4 ? "hidden sm:flex" : "flex"
                }`}
              >
                <div className="mb-1 flex items-baseline justify-between px-0.5">
                  <span className="text-[0.625rem] font-medium text-ink-muted">
                    {d.day}
                  </span>
                  <span className="text-[0.625rem] font-semibold text-ink">
                    {d.date}
                  </span>
                </div>
                <div className="flex flex-col gap-1">
                  {d.posts.map((p, pi) => (
                    <motion.div
                      key={pi}
                      initial={{ opacity: 0, y: 6, scale: 0.96 }}
                      whileInView={{ opacity: 1, y: 0, scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.15 * di + 0.1 * pi, duration: 0.4 }}
                      className="flex items-center gap-1 rounded-md bg-card px-1.5 py-1 shadow-soft"
                    >
                      <span
                        className="h-1.5 w-1.5 shrink-0 rounded-full"
                        style={{ background: p.color }}
                      />
                      <span className="truncate text-[0.5625rem] font-medium text-ink">
                        {p.label}
                      </span>
                    </motion.div>
                  ))}
                  {d.posts.length === 0 && (
                    <span className="rounded-md border border-dashed border-border py-1.5" />
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* аналитика */}
          <div className="mt-auto flex items-end gap-4 rounded-xl bg-surface-soft px-3 py-2.5">
            <div className="shrink-0">
              <div className="text-[0.625rem] text-ink-muted">Охват за неделю</div>
              <div className="font-display text-base font-bold leading-tight text-ink">
                12 480
              </div>
              <div className="text-[0.625rem] font-semibold text-success">
                +18% к прошлой
              </div>
            </div>
            <div className="flex h-10 flex-1 items-end justify-between gap-1">
              {BARS.map((h, i) => (
                <motion.span
                  key={i}
                  className="h-full w-full rounded-sm bg-brand/70"
                  style={{ originY: 1 }}
                  initial={{ scaleY: 0 }}
                  whileInView={{ scaleY: h / 100 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.05 * i + 0.3, duration: 0.5, ease: "easeOut" }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
