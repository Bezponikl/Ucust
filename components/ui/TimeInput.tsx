"use client";

import { useEffect, useRef, useState } from "react";
import Icon from "@/components/ui/Icon";
import { maskTime, validateTime } from "@/lib/dashboard/date";

export type TimeInputVariant = "inline" | "field" | "settings";

/**
 * Ввод времени: ровно 4 цифры, часы 00–23, минуты 00–59.
 * Двоеточие подставляется маской, ошибка показывается после ввода (на blur).
 * Один компонент на редактор публикации, планирование и настройки бизнеса.
 */
export default function TimeInput({
  value,
  onChange,
  variant = "inline",
  ariaLabel = "Время",
  label,
}: {
  value: string;
  onChange: (t: string) => void;
  variant?: TimeInputVariant;
  ariaLabel?: string;
  /** Подпись над полем — для варианта настроек. */
  label?: string;
}) {
  const [draft, setDraft] = useState(value);
  const [error, setError] = useState<string | null>(null);
  const touched = useRef(false);

  // Значение могли поменять снаружи, пока поле не редактируют
  useEffect(() => { if (!touched.current) setDraft(value); }, [value]);

  const commit = (raw: string) => {
    touched.current = false;
    const res = validateTime(raw);
    if ("error" in res) {
      setError(res.error);
      return;
    }
    setError(null);
    setDraft(res.value);
    onChange(res.value);
  };

  const inputClass =
    variant === "settings"
      ? `w-full rounded-full border bg-surface-soft/70 px-4 py-2.5 pr-10 text-sm text-ink outline-none backdrop-blur-sm transition ${
          error ? "border-[#e5484d]" : "border-border focus:border-brand focus:ring-1 focus:ring-brand/25"
        }`
      : variant === "field"
        ? `w-full rounded-2xl border bg-surface-soft px-4 py-2.5 text-sm text-ink outline-none transition duration-150 ${
            error ? "border-[#e5484d]" : "border-transparent focus:border-brand/40"
          }`
        : `w-[4.5rem] rounded-xl bg-transparent px-1.5 py-1.5 text-center text-sm font-medium text-ink outline-none transition duration-150 hover:bg-surface-soft focus:bg-surface-soft ${
            error ? "ring-1 ring-[#e5484d]" : "focus:ring-1 focus:ring-brand/40"
          }`;

  const field = (
    <div className={variant === "inline" ? "relative flex items-center" : "relative"}>
      <input
        value={draft}
        onChange={(e) => { touched.current = true; setDraft(maskTime(e.target.value)); if (error) setError(null); }}
        onBlur={(e) => commit(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); commit(draft); } }}
        inputMode="numeric"
        placeholder="чч:мм"
        maxLength={5}
        aria-label={ariaLabel}
        aria-invalid={error ? true : undefined}
        className={inputClass}
      />
      {variant === "settings" && (
        <Icon
          name="clock"
          size={15}
          className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted"
          aria-hidden="true"
        />
      )}
      {error && (
        <p
          role="alert"
          className={`z-40 text-xs text-[#e5484d] ${
            variant === "inline"
              ? "absolute right-0 top-full mt-1 whitespace-nowrap rounded-lg border border-border bg-card px-2 py-1 shadow-lift"
              : "mt-1"
          }`}
        >
          {error}
        </p>
      )}
    </div>
  );

  if (!label) return field;

  return (
    <div>
      <span className="mb-1.5 block text-sm font-semibold text-ink">{label}</span>
      {field}
    </div>
  );
}
