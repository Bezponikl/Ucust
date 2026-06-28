"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

const ITEMS = ["1. О проекте", "2. Рынок", "3. SWOT анализ", "4. Услуги", "5. Цели"];

export default function ProfileSidebar({ current, onSelect }: { current: number; onSelect: (i: number) => void }) {
  return (
    <aside className="shrink-0 border-border lg:w-64 lg:border-r">
      <Link
        href="/"
        className="mb-4 hidden items-center gap-2 px-4 pt-6 text-sm text-ink-muted hover:text-ink lg:flex"
      >
        <ArrowLeft size={16} aria-hidden="true" /> На главную
      </Link>
      <p className="mb-2 hidden px-4 text-xs font-semibold uppercase tracking-wide text-ink-muted lg:block">
        Проект
      </p>
      <nav className="flex gap-2 overflow-x-auto px-2 pb-2 lg:flex-col lg:overflow-visible lg:pb-0">
        {ITEMS.map((item, i) => (
          <button
            key={item}
            type="button"
            onClick={() => onSelect(i)}
            aria-current={i === current ? "page" : undefined}
            className={`whitespace-nowrap rounded-xl px-4 py-2.5 text-left text-sm font-medium transition ${
              i === current ? "bg-brand text-white" : "text-ink-muted hover:bg-surface-soft hover:text-ink"
            }`}
          >
            {item}
          </button>
        ))}
      </nav>
    </aside>
  );
}
