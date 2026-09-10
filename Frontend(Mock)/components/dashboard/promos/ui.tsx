"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import { menuSurfaceClass } from "@/lib/dashboard/surface";

/** Закрытие по клику вне и по Escape. */
export function useDismiss<T extends HTMLElement>(open: boolean, close: () => void) {
  const ref = useRef<T>(null);
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) close();
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") close(); };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open, close]);
  return ref;
}

/* ── Сегментированный переключатель ── */
export interface Segment<T extends string> {
  id: T;
  label?: string;
  icon?: IconName;
  count?: number;
  /** Подсказка для варианта без подписи (режим отображения). */
  title?: string;
}

export function Segmented<T extends string>({
  value,
  options,
  onChange,
  ariaLabel,
  compact = false,
}: {
  value: T;
  options: Segment<T>[];
  onChange: (v: T) => void;
  ariaLabel: string;
  /** Только иконки — для переключателя вида. */
  compact?: boolean;
}) {
  return (
    <div
      role="tablist"
      aria-label={ariaLabel}
      className="inline-flex shrink-0 items-center gap-0.5 rounded-full border border-border/70 bg-surface-soft/60 p-1"
    >
      {options.map((o) => {
        const on = o.id === value;
        return (
          <button
            key={o.id}
            type="button"
            role="tab"
            aria-selected={on}
            title={o.title}
            aria-label={o.title}
            onClick={() => onChange(o.id)}
            className={`inline-flex items-center gap-1.5 rounded-full text-sm font-medium transition duration-200 ${
              compact ? "h-8 w-8 justify-center" : "px-3.5 py-1.5"
            } ${on ? "bg-card text-ink shadow-soft" : "text-ink-muted hover:text-ink"}`}
          >
            {o.icon && <Icon name={o.icon} size={compact ? 16 : 14} aria-hidden="true" />}
            {o.label}
            {o.count != null && (
              <span className={`text-xs tabular-nums ${on ? "text-ink-muted" : "text-ink-muted/70"}`}>
                {o.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

/* ── Компактный дропдаун фильтра ── */
export interface SelectOption<T extends string> {
  id: T;
  label: string;
  icon?: IconName;
}

export function FilterSelect<T extends string>({
  value,
  options,
  onChange,
  ariaLabel,
  icon,
}: {
  value: T;
  options: SelectOption<T>[];
  onChange: (v: T) => void;
  ariaLabel: string;
  icon?: IconName;
}) {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);
  const ref = useDismiss<HTMLDivElement>(open, () => setOpen(false));
  const current = options.find((o) => o.id === value);

  return (
    <div ref={ref} className="relative shrink-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={ariaLabel}
        className={`inline-flex h-9 items-center gap-2 rounded-full border px-3.5 text-sm font-medium transition duration-200 ${
          open ? "border-brand/40 bg-card text-ink" : "border-border/70 bg-surface-soft/60 text-ink-muted hover:text-ink"
        }`}
      >
        {icon && <Icon name={icon} size={14} aria-hidden="true" />}
        <span className="max-w-36 truncate">{current?.label ?? ariaLabel}</span>
        <Icon
          name="chevron-down"
          size={14}
          className={`transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          aria-hidden="true"
        />
      </button>

      {open && (
        <div
          role="listbox"
          className={`uc-pop-in absolute right-0 top-full z-40 mt-2 w-52 overflow-hidden rounded-2xl border border-border/70 p-1.5 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}
        >
          {options.map((o) => (
            <button
              key={o.id}
              type="button"
              role="option"
              aria-selected={o.id === value}
              onClick={() => { onChange(o.id); setOpen(false); }}
              className={`flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left text-sm transition duration-150 hover:bg-surface-soft ${
                o.id === value ? "text-ink" : "text-ink-muted"
              }`}
            >
              {o.icon && <Icon name={o.icon} size={14} aria-hidden="true" />}
              <span className="min-w-0 flex-1 truncate">{o.label}</span>
              {o.id === value && <Icon name="check" size={14} className="shrink-0 text-brand" aria-hidden="true" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Поиск ── */
export function SearchInput({
  value,
  onChange,
  placeholder = "Поиск",
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  return (
    <div className="relative w-full min-w-0 sm:w-auto sm:max-w-64 sm:flex-1">
      <Icon
        name="search"
        size={15}
        className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-muted"
        aria-hidden="true"
      />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
        className="h-9 w-full rounded-full border border-border/70 bg-surface-soft/60 pl-9 pr-8 text-sm text-ink outline-none transition duration-200 placeholder:text-ink-muted/70 focus:border-brand/40 focus:bg-card"
      />
      {value && (
        <button
          type="button"
          onClick={() => onChange("")}
          aria-label="Очистить поиск"
          className="absolute right-2.5 top-1/2 flex h-5 w-5 -translate-y-1/2 items-center justify-center rounded-full text-ink-muted transition hover:text-ink"
        >
          <Icon name="close" size={13} aria-hidden="true" />
        </button>
      )}
    </div>
  );
}

/* ── Компактная плитка KPI (высота ≈90px) ── */
export function KpiTile({
  label,
  value,
  delta,
  tone = "ink",
  active = false,
  onClick,
}: {
  label: string;
  value: string;
  /** Например «↑12%» — показываем только там, где сравнение осмысленно. */
  delta?: string;
  tone?: "ink" | "success" | "brand";
  /** Плитка-фильтр: подсвечивается, когда её срез выбран. */
  active?: boolean;
  onClick?: () => void;
}) {
  const valueTone =
    tone === "success" ? "text-success" : tone === "brand" ? "text-brand" : "text-ink";

  const body = (
    <>
      <span className="truncate text-xs font-medium text-ink-muted">{label}</span>
      <span className="flex items-baseline gap-2">
        <span className={`font-display text-[1.75rem] font-extrabold leading-none tabular-nums ${valueTone}`}>
          {value}
        </span>
        {delta && <span className="text-xs font-semibold text-success">{delta}</span>}
      </span>
    </>
  );

  const base = "flex h-[5.625rem] flex-col justify-center gap-1.5 rounded-[20px] border px-4 py-3 backdrop-blur-sm sm:px-5";

  if (!onClick) {
    return <div className={`${base} border-border/70 bg-card/70`}>{body}</div>;
  }

  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`${base} text-left outline-none transition duration-200 focus-visible:ring-2 focus-visible:ring-brand/50 ${
        active ? "border-brand/60 bg-brand/[0.08]" : "border-border/70 bg-card/70 hover:border-brand/30"
      }`}
    >
      {body}
    </button>
  );
}

/* ── Заголовок раздела с действием справа ── */
export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <h1 className="text-xl font-bold text-ink sm:text-2xl">{title}</h1>
        <p className="mt-0.5 text-sm text-ink-muted">{subtitle}</p>
      </div>
      {action}
    </div>
  );
}
