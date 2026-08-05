import type { InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from "react";

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">{label}</span>
      {children}
      {hint && <span className="mt-1.5 block text-xs text-ink-muted">{hint}</span>}
    </label>
  );
}

// Поля читаются как строки досье: мягкая подложка, спокойная рамка и заметная
// бренд-подсветка в фокусе — вместо тёмных капсул-провалов.
const base =
  "w-full rounded-2xl border border-border/70 bg-surface-soft px-4 py-3 text-sm text-ink placeholder:text-ink-muted/60 outline-none transition hover:border-border focus:border-brand focus:bg-card focus:ring-2 focus:ring-brand/20";

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`${base} ${props.className ?? ""}`} />;
}

export function TextArea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={`${base} min-h-28 resize-none leading-relaxed ${props.className ?? ""}`} />;
}
