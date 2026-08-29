"use client";

import { useRef, useState } from "react";
import Icon from "@/components/ui/Icon";
import AnchoredPopover from "@/components/ui/AnchoredPopover";
import { MonthCalendar } from "@/components/dashboard/content/schedule";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import { menuSurfaceClass } from "@/lib/dashboard/surface";
import { fmtPeriod } from "@/lib/dashboard/date";

/**
 * Период действия акции одним полем: календарь берёт первый клик за начало,
 * второй — за окончание, и подсвечивает промежуток. Раньше здесь стояли два
 * нативных `input[type=date]`, по которым период было не видно.
 */
export default function DateRangeField({
  from,
  to,
  onChange,
  label = "Период действия",
}: {
  from: string;
  to: string;
  onChange: (from: string, to: string) => void;
  label?: string;
}) {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);
  // Пока выбрано только начало — ждём второй клик и держим подсказку на виду.
  const [pendingFrom, setPendingFrom] = useState<string | null>(null);
  const anchor = useRef<HTMLDivElement>(null);

  const pick = (iso: string) => {
    if (pendingFrom === null) {
      setPendingFrom(iso);
      return;
    }
    // Клик «назад по календарю» не должен давать перевёрнутый период.
    const [a, b] = iso < pendingFrom ? [iso, pendingFrom] : [pendingFrom, iso];
    onChange(a, b);
    setPendingFrom(null);
    setOpen(false);
  };

  const close = () => {
    setPendingFrom(null);
    setOpen(false);
  };

  const range = pendingFrom ? { from: pendingFrom, to: pendingFrom } : { from, to };

  return (
    <div ref={anchor} className="relative">
      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">
        {label}
      </span>
      <button
        type="button"
        onClick={() => (open ? close() : setOpen(true))}
        aria-expanded={open}
        aria-label={`${label}: ${fmtPeriod(from, to)}`}
        className={`flex w-full items-center justify-between gap-2 rounded-2xl border bg-surface-soft px-4 py-2.5 text-left text-sm font-medium text-ink transition duration-150 ${
          open ? "border-brand ring-1 ring-brand/25" : "border-border hover:border-brand/50"
        }`}
      >
        {fmtPeriod(from, to) || "Выберите даты"}
        <Icon name="calendar" size={16} className="shrink-0 text-ink-muted" aria-hidden="true" />
      </button>

      <AnchoredPopover
        anchorRef={anchor}
        open={open}
        onClose={close}
        width={288}
        align="left"
        className={`rounded-2xl border border-border/70 p-2 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}
      >
        <p className="px-1 pb-1.5 text-xs text-ink-muted">
          {pendingFrom ? "Теперь выберите дату окончания" : "Выберите дату начала"}
        </p>
        <MonthCalendar value={pendingFrom ?? from} onSelect={pick} range={range} />
      </AnchoredPopover>
    </div>
  );
}
