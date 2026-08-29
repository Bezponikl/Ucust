"use client";

import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type ReactNode,
  type RefObject,
  type TextareaHTMLAttributes,
} from "react";
import Icon from "@/components/ui/Icon";
import AnchoredPopover from "@/components/ui/AnchoredPopover";
import TimeInput from "@/components/ui/TimeInput";
import type { IconName } from "@/lib/icons/solar";
import { CHANNELS, CHANNEL_ORDER, type ChannelId } from "@/lib/channels";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import { menuSurfaceClass } from "@/lib/dashboard/surface";
import { fmtDayMonth } from "@/lib/dashboard/date";
import { MonthCalendar } from "./schedule";

/** Закрытие поповера по клику вне и по Escape. */
function useDismiss(open: boolean, close: () => void) {
  const ref = useRef<HTMLDivElement>(null);
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

/** Раскрывать поповер вверх, если снизу не помещается (считаем в момент открытия). */
function dropsUp(anchor: HTMLElement | null, needed: number) {
  if (!anchor) return false;
  const rect = anchor.getBoundingClientRect();
  return window.innerHeight - rect.bottom < needed && rect.top > needed;
}

/** Заголовок публикации: растёт под текст, живёт без рамки — как в документе. */
export function AutoGrowTextarea({
  value,
  innerRef,
  ...rest
}: TextareaHTMLAttributes<HTMLTextAreaElement> & {
  value: string;
  /** Ссылка наружу — например, чтобы вставить эмодзи в позицию курсора. */
  innerRef?: RefObject<HTMLTextAreaElement | null>;
}) {
  const own = useRef<HTMLTextAreaElement>(null);
  const ref = innerRef ?? own;
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    // scrollHeight уже учитывает min-height из класса, поэтому поле не схлопывается
    el.style.height = `${el.scrollHeight}px`;
  }, [value, ref]);
  return <textarea ref={ref} rows={1} value={value} {...rest} />;
}

/* ── Строка настройки: подпись слева, контрол справа ── */
export function ControlRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 py-2.5">
      <span className="shrink-0 text-sm text-ink-muted">{label}</span>
      {children}
    </div>
  );
}

/* ── Компактный селект ── */
export interface SelectOption<T extends string> {
  id: T;
  label: string;
  /** Цветная точка перед подписью — для статусов. */
  dot?: string;
  icon?: IconName;
}

export function SoftSelect<T extends string>({
  value,
  options,
  onChange,
  align = "right",
  ariaLabel,
}: {
  value: T;
  options: SelectOption<T>[];
  onChange: (v: T) => void;
  align?: "left" | "right";
  ariaLabel: string;
}) {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);
  const ref = useDismiss(open, () => setOpen(false));
  const [up, setUp] = useState(false);
  const current = options.find((o) => o.id === value);
  const toggleOpen = () => {
    setUp(dropsUp(ref.current, 40 + options.length * 40));
    setOpen((v) => !v);
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={toggleOpen}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={ariaLabel}
        className="inline-flex items-center gap-2 rounded-xl px-2.5 py-1.5 text-sm font-medium text-ink transition duration-150 hover:bg-surface-soft"
      >
        {current?.dot && <span className={`h-2 w-2 shrink-0 rounded-full ${current.dot}`} />}
        {current?.icon && <Icon name={current.icon} size={14} className="text-ink-muted" aria-hidden="true" />}
        {current?.label ?? "—"}
        <Icon
          name="chevron-down"
          size={14}
          className={`text-ink-muted transition-transform duration-150 ${open ? "rotate-180" : ""}`}
          aria-hidden="true"
        />
      </button>

      {open && (
        <div
          role="listbox"
          className={`uc-pop-in absolute z-40 w-48 overflow-hidden rounded-2xl border border-border/70 p-1.5 shadow-lift ${
            up ? "bottom-full mb-1.5" : "top-full mt-1.5"
          } ${align === "right" ? "right-0" : "left-0"} ${menuSurfaceClass(surfaceStyle)}`}
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
              {o.dot && <span className={`h-2 w-2 shrink-0 rounded-full ${o.dot}`} />}
              {o.icon && <Icon name={o.icon} size={14} aria-hidden="true" />}
              {o.label}
              {o.id === value && <Icon name="check-bold" size={14} className="ml-auto text-brand" aria-hidden="true" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Каналы: один селект с чекбоксами вместо россыпи кнопок ── */
export function ChannelSelect({
  value,
  onChange,
}: {
  value: ChannelId[];
  onChange: (next: ChannelId[]) => void;
}) {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);
  const ref = useDismiss(open, () => setOpen(false));
  const [up, setUp] = useState(false);
  const toggleOpen = () => {
    setUp(dropsUp(ref.current, 320));
    setOpen((v) => !v);
  };

  const toggle = (id: ChannelId) =>
    onChange(value.includes(id) ? value.filter((x) => x !== id) : [...value, id]);

  const label =
    value.length === 0
      ? "Не выбраны"
      : value.length <= 2
        ? value.map((id) => CHANNELS[id].short ?? CHANNELS[id].label).join(", ")
        : `${CHANNELS[value[0]].short ?? CHANNELS[value[0]].label} и ещё ${value.length - 1}`;

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={toggleOpen}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="inline-flex max-w-full items-center gap-2 rounded-xl px-2.5 py-1.5 text-sm font-medium text-ink transition duration-150 hover:bg-surface-soft"
      >
        <span className="truncate">{label}</span>
        <Icon
          name="chevron-down"
          size={14}
          className={`shrink-0 text-ink-muted transition-transform duration-150 ${open ? "rotate-180" : ""}`}
          aria-hidden="true"
        />
      </button>

      {open && (
        <div
          role="listbox"
          aria-multiselectable="true"
          className={`uc-pop-in absolute right-0 z-40 max-h-72 w-60 overflow-y-auto rounded-2xl border border-border/70 p-1.5 shadow-lift ${
            up ? "bottom-full mb-1.5" : "top-full mt-1.5"
          } ${menuSurfaceClass(surfaceStyle)}`}
        >
          {/* Только названия: иконки соцсетей в списке создавали лишний шум */}
          {CHANNEL_ORDER.map((id) => {
            const ch = CHANNELS[id];
            const on = value.includes(id);
            return (
              <button
                key={id}
                type="button"
                role="option"
                aria-selected={on}
                onClick={() => toggle(id)}
                className={`flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left text-sm transition duration-150 hover:bg-surface-soft ${
                  on ? "text-ink" : "text-ink-muted"
                }`}
              >
                <span className="min-w-0 flex-1 truncate">{ch.label}</span>
                {on && <Icon name="check" size={14} className="shrink-0 text-brand" aria-hidden="true" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ── Дата и время публикации ──
   Дата в ISO, время — общий TimeInput с валидацией «ЧЧ:ММ». */

type FieldVariant = "inline" | "field";

/** Дата публикации: кнопка-значение и календарь с выбором месяца и года. */
export function DateField({
  value,
  onChange,
  originalDate,
  variant = "inline",
  ariaLabel = "Дата публикации",
}: {
  value: string;
  onChange: (iso: string) => void;
  originalDate?: string;
  variant?: FieldVariant;
  ariaLabel?: string;
}) {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);
  const anchor = useRef<HTMLDivElement>(null);

  return (
    <div ref={anchor} className={variant === "field" ? "relative" : "relative inline-flex"}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label={ariaLabel}
        className={
          variant === "field"
            ? `flex w-full items-center justify-between gap-2 rounded-2xl border bg-surface-soft px-4 py-2.5 text-left text-sm text-ink transition duration-150 ${
                open ? "border-brand/40" : "border-transparent hover:border-border"
              }`
            : "rounded-xl px-2.5 py-1.5 text-sm font-medium text-ink transition duration-150 hover:bg-surface-soft"
        }
      >
        {fmtDayMonth(value)}
        {variant === "field" && <Icon name="calendar" size={16} className="shrink-0 text-ink-muted" aria-hidden="true" />}
      </button>

      {/* Портал: в модалке и в панели с прокруткой обычный поповер обрезается */}
      <AnchoredPopover
        anchorRef={anchor}
        open={open}
        onClose={() => setOpen(false)}
        width={288}
        align={variant === "field" ? "left" : "right"}
        className={`rounded-2xl border border-border/70 p-2 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}
      >
        <MonthCalendar
          value={value}
          originalDate={originalDate}
          onSelect={(iso) => { onChange(iso); setOpen(false); }}
        />
      </AnchoredPopover>
    </div>
  );
}

/** Дата и время одной строкой — для панели свойств публикации. */
export function DateTimeField({
  date,
  time,
  originalDate,
  onDate,
  onTime,
}: {
  date: string;
  time: string;
  originalDate?: string;
  onDate: (iso: string) => void;
  onTime: (t: string) => void;
}) {
  return (
    <div className="flex items-center gap-1">
      <DateField value={date} onChange={onDate} originalDate={originalDate} />
      <TimeInput value={time} onChange={onTime} ariaLabel="Время публикации" />
    </div>
  );
}

/* ── Меню действий (Улучшить AI / ⋯ AI) ── */
export function ActionMenu({
  trigger,
  items,
  align = "right",
  width = "w-56",
  emphasis = false,
}: {
  trigger: ReactNode;
  items: { id: string; label: string; icon: IconName; onSelect: () => void }[];
  align?: "left" | "right";
  width?: string;
  /** Заметный вариант: заливка и рамка — для главного AI-действия экрана. */
  emphasis?: boolean;
}) {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);
  const ref = useDismiss(open, () => setOpen(false));
  const [up, setUp] = useState(false);
  const toggleOpen = () => {
    setUp(dropsUp(ref.current, 60 + items.length * 40));
    setOpen((v) => !v);
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={toggleOpen}
        aria-haspopup="menu"
        aria-expanded={open}
        className={`inline-flex items-center gap-1.5 rounded-full font-semibold text-brand transition duration-150 ${
          emphasis
            ? "border border-brand/35 bg-brand/12 px-3.5 py-2 text-[0.8125rem] shadow-soft hover:bg-brand/18"
            : "px-3 py-1.5 text-xs hover:bg-brand/10"
        }`}
      >
        {trigger}
      </button>
      {open && (
        <div
          role="menu"
          className={`uc-pop-in absolute z-40 ${width} overflow-hidden rounded-2xl border border-border/70 p-1.5 shadow-lift ${
            up ? "bottom-full mb-1.5" : "top-full mt-1.5"
          } ${align === "right" ? "right-0" : "left-0"} ${menuSurfaceClass(surfaceStyle)}`}
        >
          {items.map((it) => (
            <button
              key={it.id}
              type="button"
              role="menuitem"
              onClick={() => { setOpen(false); it.onSelect(); }}
              className="flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left text-sm text-ink transition duration-150 hover:bg-surface-soft"
            >
              <Icon name={it.icon} size={14} className="shrink-0 text-brand" aria-hidden="true" />
              {it.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
