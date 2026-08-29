"use client";

import Link from "next/link";
import Icon from "@/components/ui/Icon";

const ITEMS = ["О проекте", "Рынок", "SWOT анализ", "Услуги", "Цели"];

/**
 * Навигация по разделам профиля. Это последовательная проверка досье,
 * поэтому шаги пронумерованы, а пройденные отмечены галочкой.
 */
export default function ProfileSidebar({ current, onSelect }: { current: number; onSelect: (i: number) => void }) {
  const progress = ((current + 1) / ITEMS.length) * 100;

  return (
    <aside className="shrink-0 lg:w-72">
      <Link
        href="/dashboard"
        className="mb-6 hidden items-center gap-2 text-sm text-ink-muted transition hover:text-ink lg:flex"
      >
        <Icon name="arrow-left" size={16} aria-hidden="true" /> В кабинет
      </Link>

      <div className="mb-4 hidden lg:block">
        <div className="mb-2 flex items-baseline justify-between">
          <span className="text-xs font-semibold uppercase tracking-[0.14em] text-ink-muted">Профиль бренда</span>
          <span className="text-xs font-medium text-ink-muted">{current + 1} / {ITEMS.length}</span>
        </div>
        <div className="h-1 overflow-hidden rounded-full bg-border">
          <div className="h-full rounded-full bg-brand transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <nav className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-2 lg:mx-0 lg:flex-col lg:gap-1 lg:overflow-visible lg:px-0 lg:pb-0">
        {ITEMS.map((item, i) => {
          const active = i === current;
          const done = i < current;
          return (
            <button
              key={item}
              type="button"
              onClick={() => onSelect(i)}
              aria-current={active ? "step" : undefined}
              className={`group flex shrink-0 items-center gap-3 whitespace-nowrap rounded-2xl px-3 py-2.5 text-left text-sm font-medium transition lg:w-full ${
                active
                  ? "bg-brand/12 text-ink ring-1 ring-brand/30"
                  : "text-ink-muted hover:bg-surface-soft hover:text-ink"
              }`}
            >
              <span
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold transition ${
                  active
                    ? "bg-brand text-white"
                    : done
                      ? "bg-success/15 text-success"
                      : "bg-surface-soft text-ink-muted group-hover:text-ink"
                }`}
              >
                {done ? <Icon name="check-bold" size={13} aria-hidden="true" /> : i + 1}
              </span>
              {item}
              {active && (
                <Icon name="chevron-right" size={14} className="ml-auto hidden text-brand lg:block" aria-hidden="true" />
              )}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
