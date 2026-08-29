"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import Icon from "@/components/ui/Icon";
import UiCheckbox from "@/components/ui/Checkbox";
import { dropClass, useDropDirection } from "@/lib/useDropDirection";

export function SettingsCard({ title, desc, children, className = "" }: { title?: string; desc?: string; children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6 ${className}`}>
      {title && <h2 className="text-base font-bold text-ink sm:text-lg">{title}</h2>}
      {desc && <p className="mt-1 text-sm text-ink-muted">{desc}</p>}
      <div className={title ? "mt-4" : ""}>{children}</div>
    </section>
  );
}

// Лёгкое «стекло» на поверхности поля
const fieldCls =
  "w-full border border-border bg-surface-soft/70 px-4 py-2.5 text-sm text-ink outline-none backdrop-blur-sm transition focus:border-brand focus:ring-1 focus:ring-brand/25";

export function Field({ label, hint, value, onChange, type = "text", placeholder, editable = true }: { label: string; hint?: string; value: string; onChange: (v: string) => void; type?: string; placeholder?: string; editable?: boolean }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-semibold text-ink">
        {label} {hint && <span className="font-normal text-ink-muted">{hint}</span>}
      </span>
      <span className="relative block">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className={`${fieldCls} rounded-full ${editable ? "pr-10" : ""}`}
        />
        {editable && <Icon name="edit" size={15} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted" aria-hidden="true" />}
      </span>
    </label>
  );
}

export function TextArea({ label, value, onChange, placeholder }: { label: string; value: string; onChange: (v: string) => void; placeholder?: string }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-semibold text-ink">{label}</span>
      <textarea value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className={`min-h-24 resize-none rounded-2xl ${fieldCls}`} />
    </label>
  );
}

/** Кастомный «стеклянный» селект — без нативного хрома, с поповером как у меню. */
export function SelectField({ label, value, onChange, options, placeholder }: { label?: string; value: string; onChange: (v: string) => void; options: string[]; placeholder?: string }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  // max-h-60 = 240px, плюс отступ — столько места нужно снизу, иначе раскрываем вверх
  const dir = useDropDirection(open, ref, 252);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false); };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [open]);

  return (
    <div>
      {label && <span className="mb-1.5 block text-sm font-semibold text-ink">{label}</span>}
      <div ref={ref} className="relative">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-haspopup="listbox"
          aria-expanded={open}
          className={`${fieldCls} rounded-full flex items-center justify-between gap-2 text-left ${open ? "border-brand ring-1 ring-brand/25" : ""}`}
        >
          <span className={`truncate ${value ? "text-ink" : "text-ink-muted"}`}>{value || placeholder || "Выберите"}</span>
          <Icon name="chevron-down" size={16} className={`shrink-0 text-ink-muted transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true" />
        </button>
        {open && (
          <div role="listbox" className={`uc-pop-in absolute left-0 z-50 max-h-60 w-full overflow-auto rounded-2xl border border-white/10 bg-card/90 p-1.5 shadow-lift ring-1 ring-white/5 backdrop-blur-xl ${dropClass(dir)}`}>
            {options.map((o) => (
              <button
                key={o}
                type="button"
                role="option"
                aria-selected={o === value}
                onClick={() => { onChange(o); setOpen(false); }}
                className={`flex w-full items-center justify-between gap-2 rounded-xl px-3 py-2 text-left text-sm transition hover:bg-surface-soft ${o === value ? "font-medium text-brand" : "text-ink"}`}
              >
                <span className="truncate">{o}</span>
                {o === value && <Icon name="check" size={15} className="shrink-0 text-brand" aria-hidden="true" />}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/** Кастомный чекбокс — скруглённый, с брендовой заливкой и галочкой. */
export function Checkbox({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <label className="flex cursor-pointer items-center gap-2.5 text-left text-sm text-ink">
      <UiCheckbox checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

export function Toggle({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label?: string }) {
  return (
    <button type="button" role="switch" aria-checked={checked} aria-label={label} onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition ${checked ? "bg-brand" : "bg-ink-muted/40"}`}>
      <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition ${checked ? "translate-x-5" : "translate-x-0.5"}`} />
    </button>
  );
}

export function SaveButton({ onSave }: { onSave?: () => void }) {
  const [saved, setSaved] = useState(false);
  const save = () => { setSaved(true); onSave?.(); setTimeout(() => setSaved(false), 900); };
  return (
    <button type="button" onClick={save} className="btn-glass-blue inline-flex items-center justify-center gap-2 px-5 py-3 text-sm font-semibold">
      {saved ? <Icon name="check" size={16} aria-hidden="true" /> : null}
      {saved ? "Сохранено" : "Сохранить изменения"}
    </button>
  );
}
