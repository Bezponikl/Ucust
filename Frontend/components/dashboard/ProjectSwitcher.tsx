"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown, Plus, Check } from "lucide-react";
import { useDashboard } from "./DashboardProvider";

const MOCK_PROJECTS = ["Вердиктор", "Coffee Shop", "Fashion Store"];

export default function ProjectSwitcher() {
  const { data } = useDashboard();
  const current = data?.businessName ?? "Ваш бизнес";
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex max-w-[200px] items-center gap-2 rounded-xl border border-border bg-surface-soft px-3 py-1.5 text-left"
      >
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-brand-tint text-xs font-bold text-brand" aria-hidden="true">
          {current.slice(0, 1).toUpperCase()}
        </span>
        <span className="min-w-0 leading-tight">
          <span className="block truncate text-sm font-semibold text-ink">{current}</span>
          <span className="block text-xs text-ink-muted">Проект</span>
        </span>
        <ChevronDown size={16} className={`shrink-0 text-ink-muted transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true" />
      </button>

      {open && (
        <div className="absolute left-0 top-full z-50 mt-2 w-64 overflow-hidden rounded-2xl border border-border bg-card p-1.5 shadow-lift">
          <button type="button" onClick={() => setOpen(false)} className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left hover:bg-surface-soft">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-tint text-xs font-bold text-brand" aria-hidden="true">{current.slice(0, 1).toUpperCase()}</span>
            <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{current}</span>
            <Check size={16} className="text-brand" aria-hidden="true" />
          </button>
          {MOCK_PROJECTS.map((p) => (
            <button key={p} type="button" onClick={() => setOpen(false)} className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left hover:bg-surface-soft">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-surface-soft text-xs font-bold text-ink-muted" aria-hidden="true">{p.slice(0, 1)}</span>
              <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{p}</span>
            </button>
          ))}
          <div className="my-1 h-px bg-border" />
          <button type="button" onClick={() => setOpen(false)} className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-medium text-brand hover:bg-surface-soft">
            <Plus size={16} aria-hidden="true" /> Добавить проект
          </button>
        </div>
      )}
    </div>
  );
}
