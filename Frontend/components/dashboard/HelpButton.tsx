"use client";

import { useState } from "react";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import { useDashboard } from "./DashboardProvider";
import { menuSurfaceClass, topbarButtonClass } from "@/lib/dashboard/surface";
import { startTour } from "@/lib/dashboard/tour";

/** Кнопка «?» в топбаре: вернуть подсказки, если их пропустили при онбординге. */
export default function HelpButton() {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        type="button"
        data-tour="help"
        onClick={() => setOpen((v) => !v)}
        aria-label="Помощь и подсказки"
        aria-expanded={open}
        className={`${topbarButtonClass(surfaceStyle)} flex h-9 w-9 items-center justify-center`}
      >
        <Icon name="help" size={17} aria-hidden="true" />
      </button>

      {open && (
        <>
          <button type="button" aria-hidden className="fixed inset-0 z-20 cursor-default" onClick={() => setOpen(false)} />
          <div
            className={`absolute right-0 z-30 mt-2 w-56 overflow-hidden rounded-xl border border-border py-1 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}
          >
            <button
              type="button"
              onClick={() => { setOpen(false); startTour(); }}
              className="flex w-full items-center gap-2.5 px-3 py-2.5 text-left text-sm text-ink transition hover:bg-surface-soft"
            >
              <Icon name="sparkles" size={15} className="text-brand" aria-hidden="true" />
              Показать подсказки
            </button>
            <Link
              href="/dashboard/support"
              onClick={() => setOpen(false)}
              className="flex w-full items-center gap-2.5 px-3 py-2.5 text-left text-sm text-ink transition hover:bg-surface-soft"
            >
              <Icon name="message" size={15} className="text-ink-muted" aria-hidden="true" />
              Написать в поддержку
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
