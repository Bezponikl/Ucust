"use client";

import { useRef, type ChangeEvent, type ReactNode } from "react";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import type { Attachment } from "@/lib/dashboard/attachments";

/**
 * Поле запроса к ИИ: текст, прикреплённые фото и кнопка «+» живут в одной рамке —
 * как в привычных чатах с нейросетью. Фото уходят в запрос как контекст,
 * медиа публикации выбирается отдельно.
 */
export default function PromptComposer({
  value,
  onChange,
  placeholder,
  attachments,
  onAttach,
  onRemove,
  max,
  disabled = false,
  autoFocus = false,
  onSubmit,
  minHeight = "min-h-[168px]",
  footer,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  attachments: Attachment[];
  onAttach: (files: File[]) => void;
  onRemove: (id: string) => void;
  max: number;
  disabled?: boolean;
  autoFocus?: boolean;
  /** Ctrl/Cmd + Enter */
  onSubmit?: () => void;
  minHeight?: string;
  footer?: ReactNode;
}) {
  const fileInput = useRef<HTMLInputElement>(null);
  const full = attachments.length >= max;

  const pick = (e: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    if (files.length) onAttach(files);
    e.target.value = "";
  };

  return (
    <div
      className={`rounded-[24px] border border-transparent bg-surface-soft transition focus-within:border-brand/40 focus-within:bg-card ${
        disabled ? "opacity-60" : ""
      }`}
    >
      {/* Прикреплённые фото — над текстом, внутри той же рамки */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2 px-4 pt-4">
          {attachments.map((a) => (
            <div
              key={a.id}
              className="group relative h-16 w-16 overflow-hidden rounded-2xl border border-border bg-card"
            >
              <Image src={a.url} alt={a.name} fill unoptimized sizes="64px" className="object-cover" />
              <button
                type="button"
                onClick={() => onRemove(a.id)}
                aria-label={`Убрать фото ${a.name}`}
                className="absolute right-1 top-1 flex h-6 w-6 items-center justify-center rounded-full bg-ink/60 text-white backdrop-blur-sm transition hover:bg-ink/85"
              >
                <Icon name="close" size={12} aria-hidden="true" />
              </button>
            </div>
          ))}
        </div>
      )}

      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (onSubmit && e.key === "Enter" && (e.metaKey || e.ctrlKey)) onSubmit();
        }}
        disabled={disabled}
        autoFocus={autoFocus}
        placeholder={placeholder}
        className={`w-full resize-none bg-transparent px-5 pt-4 text-base leading-relaxed text-ink outline-none placeholder:text-ink-muted/70 disabled:cursor-not-allowed ${minHeight}`}
      />

      {/* Нижняя строка: «+» слева, подсказка справа */}
      <div className="flex items-center gap-3 px-3 pb-3">
        <button
          type="button"
          onClick={() => fileInput.current?.click()}
          disabled={disabled || full}
          title={full ? `Можно приложить не больше ${max} фото` : "Добавить фото"}
          aria-label="Добавить фото к запросу"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-ink-muted outline-none transition hover:text-ink focus-visible:ring-2 focus-visible:ring-brand/40 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Icon name="plus" size={26} aria-hidden="true" />
        </button>

        <span className="min-w-0 flex-1 truncate text-xs text-ink-muted">
          {attachments.length > 0
            ? `ИИ посмотрит ${attachments.length === 1 ? "снимок" : `на ${attachments.length} снимка`} и учтёт это в тексте`
            : footer}
        </span>
      </div>

      <input ref={fileInput} type="file" accept="image/*" multiple hidden onChange={pick} />
    </div>
  );
}
