"use client";

import { useEffect } from "react";
import Icon from "@/components/ui/Icon";
import { setTourState } from "@/lib/dashboard/tour";

/**
 * Финальный шаг онбординга: спрашиваем, показать ли, как работает платформа.
 * Ответ пишем в uc_tour — дашборд запускает подсказки только при «pending».
 */
export default function TourPrompt({
  open,
  onDone,
}: {
  open: boolean;
  onDone: () => void;
}) {
  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = prev; };
  }, [open]);

  if (!open) return null;

  const choose = (withTour: boolean) => {
    setTourState(withTour ? "pending" : "skipped");
    onDone();
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="uc-fade-in absolute inset-0 bg-ink/50 backdrop-blur-sm" aria-hidden="true" />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="tour-prompt-title"
        className="uc-modal-in relative w-full max-w-md overflow-hidden rounded-[28px] border border-border bg-gradient-to-b from-success/10 via-card to-card p-6 text-center shadow-lift sm:p-8"
      >
        {/* Мягкое свечение за иконкой — момент завершения стоит отметить */}
        <span className="relative mx-auto flex h-14 w-14 items-center justify-center">
          <span aria-hidden="true" className="absolute -inset-3 rounded-full bg-success/20 blur-xl" />
          <span className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-success/18 text-success">
            <Icon name="check-bold" size={28} aria-hidden="true" />
          </span>
        </span>

        <h2 id="tour-prompt-title" className="mt-4 text-xl font-bold text-ink">
          Профиль готов
        </h2>
        <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-ink-muted">
          UCust уже знает, чем вы занимаетесь, и готов вести соцсети. Показать, где что
          находится? Это займёт меньше минуты.
        </p>

        <div className="mt-6 flex flex-col gap-2">
          <button
            type="button"
            onClick={() => choose(true)}
            className="btn-glass-blue inline-flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold"
          >
            <Icon name="sparkles" size={16} aria-hidden="true" /> Как работает платформа
          </button>
          <button
            type="button"
            onClick={() => choose(false)}
            className="inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-medium text-ink-muted transition hover:text-ink"
          >
            Разберусь сам
          </button>
        </div>

        <p className="mt-4 flex items-center justify-center gap-1.5 text-xs text-ink-muted">
          <Icon name="help" size={13} aria-hidden="true" />
          Подсказки всегда можно вернуть в меню профиля
        </p>
      </div>
    </div>
  );
}
