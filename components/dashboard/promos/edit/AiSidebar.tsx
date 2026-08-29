"use client";

import { useEffect } from "react";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";

export interface AiSuggestion {
  id: string;
  label: string;
  hint: string;
  icon: IconName;
}

export const AI_SUGGESTIONS: AiSuggestion[] = [
  { id: "headline", label: "Улучшить заголовок", hint: "Сделать короче и цепляюще", icon: "sparkles" },
  { id: "description", label: "Написать описание", hint: "По условиям акции", icon: "file-text" },
  { id: "attractive", label: "Сделать акцию привлекательнее", hint: "Усилить выгоду и срочность", icon: "trending" },
  { id: "banner", label: "Создать баннер", hint: "Обложка под ваш бренд", icon: "image" },
  { id: "code", label: "Подобрать промокод", hint: "Короткий и запоминающийся", icon: "link" },
  { id: "post", label: "Сгенерировать пост", hint: "Готовая публикация в соцсети", icon: "send" },
  { id: "mailing", label: "Написать рассылку", hint: "Письмо для базы клиентов", icon: "mail" },
  { id: "stories", label: "Создать Stories", hint: "Вертикальный формат", icon: "clapperboard" },
];

/**
 * Помощник рядом с формой: выдвижная панель со сценариями ИИ.
 * Держим списком действий, а не чатом — так понятнее, что именно произойдёт.
 */
export default function AiSidebar({
  open,
  onClose,
  busy,
  onRun,
}: {
  open: boolean;
  onClose: () => void;
  busy: string | null;
  onRun: (id: string) => void;
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <>
      {/* На узких экранах панель перекрывает контент, на широких — стоит сбоку */}
      <button
        type="button"
        aria-label="Закрыть помощника"
        onClick={onClose}
        className="fixed inset-0 z-40 cursor-default bg-ink/40 backdrop-blur-sm xl:hidden"
      />
      <aside
        className="uc-pop-in fixed right-0 top-0 z-50 flex h-dvh w-[20rem] flex-col border-l border-border/70 bg-card/95 backdrop-blur-xl xl:sticky xl:top-0 xl:z-0 xl:h-fit xl:max-h-[calc(100dvh-9rem)] xl:w-full xl:rounded-[20px] xl:border xl:bg-card/70"
        aria-label="AI-помощник"
      >
        <header className="flex items-center justify-between gap-2 border-b border-border/70 px-4 py-3.5">
          <span className="inline-flex items-center gap-2 text-sm font-bold text-ink">
            <Icon name="sparkles" size={16} className="text-brand" aria-hidden="true" /> AI предлагает
          </span>
          <button
            type="button"
            onClick={onClose}
            aria-label="Закрыть помощника"
            className="flex h-8 w-8 items-center justify-center rounded-full text-ink-muted transition duration-200 hover:bg-surface-soft hover:text-ink"
          >
            <Icon name="close" size={16} aria-hidden="true" />
          </button>
        </header>

        <div className="flex min-h-0 flex-1 flex-col gap-1 overflow-y-auto p-2">
          {AI_SUGGESTIONS.map((s) => {
            const loading = busy === s.id;
            return (
              <button
                key={s.id}
                type="button"
                onClick={() => onRun(s.id)}
                disabled={loading}
                className="flex items-start gap-3 rounded-2xl px-3 py-2.5 text-left transition duration-200 hover:bg-surface-soft disabled:opacity-60"
              >
                <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-brand/10 text-brand">
                  <Icon name={loading ? "refresh" : s.icon} size={15} className={loading ? "animate-spin" : ""} aria-hidden="true" />
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-medium text-ink">{loading ? "Генерирую…" : s.label}</span>
                  <span className="block text-xs text-ink-muted">{s.hint}</span>
                </span>
              </button>
            );
          })}
        </div>

        <p className="border-t border-border/70 px-4 py-3 text-xs leading-relaxed text-ink-muted">
          Результат сразу подставится в форму — можно отредактировать перед сохранением.
        </p>
      </aside>
    </>
  );
}
