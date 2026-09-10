"use client";

import { useRef, type ReactNode } from "react";
import Icon from "@/components/ui/Icon";
import EmojiPicker from "@/components/ui/EmojiPicker";
import type { IconName } from "@/lib/icons/solar";

/* Единая «воздушная» карточка секции: 20px радиус, тонкая граница, без теней */
export function Card({
  title,
  hint,
  children,
  className = "",
  action,
}: {
  title?: string;
  hint?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}) {
  return (
    <section className={`rounded-[20px] border border-border/70 bg-card/70 p-5 backdrop-blur-sm sm:p-6 ${className}`}>
      {(title || action) && (
        <header className="mb-5 flex items-start justify-between gap-3">
          <div className="min-w-0">
            {title && <h2 className="text-sm font-bold text-ink">{title}</h2>}
            {hint && <p className="mt-0.5 text-xs text-ink-muted">{hint}</p>}
          </div>
          {action}
        </header>
      )}
      {children}
    </section>
  );
}

/** Кнопка ИИ у поля: «Сгенерировать» до заполнения, «Улучшить» — после. */
export function AiFieldButton({
  loading,
  filled,
  onClick,
  labelEmpty = "Сгенерировать",
  labelFilled = "Улучшить текст",
}: {
  loading: boolean;
  filled: boolean;
  onClick: () => void;
  labelEmpty?: string;
  labelFilled?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={loading}
      className="inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold text-brand transition duration-200 hover:bg-brand/10 disabled:opacity-50"
    >
      {loading ? (
        <><Icon name="refresh" size={12} className="animate-spin" aria-hidden="true" /> Генерирую…</>
      ) : (
        <><Icon name="sparkles" size={12} aria-hidden="true" /> {filled ? labelFilled : labelEmpty}</>
      )}
    </button>
  );
}

const inputBase =
  "w-full rounded-xl border border-border/70 bg-surface-soft/60 px-4 py-2.5 text-sm text-ink outline-none transition duration-200 placeholder:text-ink-muted/60 focus:border-brand/50 focus:bg-card";

/** Текстовое поле с подписью и необязательной кнопкой ИИ. */
export function TextField({
  label,
  value,
  onChange,
  placeholder,
  hint,
  ai,
  mono = false,
  inputMode,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  hint?: string;
  ai?: { loading: boolean; onClick: () => void; labelEmpty?: string; labelFilled?: string };
  mono?: boolean;
  inputMode?: "numeric" | "text";
}) {
  return (
    <div className="min-w-0">
      {/* Фиксированная высота строки — поля с кнопкой ИИ и без неё стоят на одной линии */}
      <div className="mb-1.5 flex min-h-6 items-center justify-between gap-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">{label}</label>
        {ai && <AiFieldButton loading={ai.loading} filled={value.trim().length > 0} onClick={ai.onClick} labelEmpty={ai.labelEmpty} labelFilled={ai.labelFilled} />}
      </div>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        inputMode={inputMode}
        aria-label={label}
        className={`${inputBase} ${mono ? "font-mono tracking-widest" : ""} ${ai?.loading ? "animate-pulse opacity-60" : ""}`}
      />
      {hint && <p className="mt-1.5 text-xs text-ink-muted">{hint}</p>}
    </div>
  );
}

/** Многострочное поле: счётчик слева, эмодзи в самом поле — как в редакторе публикации. */
export function TextAreaField({
  label,
  value,
  onChange,
  placeholder,
  rows = 3,
  ai,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  rows?: number;
  ai?: { loading: boolean; onClick: () => void; labelEmpty?: string; labelFilled?: string };
}) {
  const ref = useRef<HTMLTextAreaElement>(null);
  return (
    <div className="min-w-0">
      {/* Фиксированная высота строки — поля с кнопкой ИИ и без неё стоят на одной линии */}
      <div className="mb-1.5 flex min-h-6 items-center justify-between gap-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">{label}</label>
        {ai && <AiFieldButton loading={ai.loading} filled={value.trim().length > 0} onClick={ai.onClick} labelEmpty={ai.labelEmpty} labelFilled={ai.labelFilled} />}
      </div>
      <div className="rounded-xl border border-border/70 bg-surface-soft/60 transition duration-200 focus-within:border-brand/50 focus-within:bg-card">
        <textarea
          ref={ref}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          rows={rows}
          aria-label={label}
          className={`w-full resize-none bg-transparent px-4 pt-2.5 text-sm leading-relaxed text-ink outline-none placeholder:text-ink-muted/60 ${
            ai?.loading ? "animate-pulse opacity-60" : ""
          }`}
        />
        <div className="flex items-center justify-between gap-2 px-3 pb-2">
          <span className="text-xs text-ink-muted/70">{value.length} символов</span>
          <EmojiPicker targetRef={ref} value={value} onChange={onChange} />
        </div>
      </div>
    </div>
  );
}

/** Плитки выбора — механика акции и подобные переключатели. */
export function ChoiceCards<T extends string>({
  value,
  options,
  onChange,
  ariaLabel,
}: {
  value: T;
  options: { id: T; label: string; icon: IconName; hint?: string }[];
  onChange: (v: T) => void;
  ariaLabel: string;
}) {
  return (
    <div role="radiogroup" aria-label={ariaLabel} className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
      {options.map((o) => {
        const on = o.id === value;
        return (
          <button
            key={o.id}
            type="button"
            role="radio"
            aria-checked={on}
            onClick={() => onChange(o.id)}
            className={`flex flex-col items-start gap-2 rounded-2xl border p-3.5 text-left transition duration-200 ${
              on
                ? "border-brand bg-brand/10 text-ink"
                : "border-border/70 bg-surface-soft/40 text-ink-muted hover:border-brand/30 hover:text-ink"
            }`}
          >
            <span className={`flex h-9 w-9 items-center justify-center rounded-xl ${on ? "bg-brand/15 text-brand" : "bg-card/70"}`}>
              <Icon name={o.icon} size={17} aria-hidden="true" />
            </span>
            <span className="text-sm font-semibold">{o.label}</span>
            {o.hint && <span className="text-xs text-ink-muted">{o.hint}</span>}
          </button>
        );
      })}
    </div>
  );
}
