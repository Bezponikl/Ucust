"use client";

import Image from "next/image";
import { Gift, Plus } from "lucide-react";
import { CHANNELS } from "@/lib/channels";
import {
  PROMOS,
  PROMO_STATUS_LABEL,
  promoCounts,
  type PromoStatus,
} from "@/lib/dashboard/promos";

const STATUS_BADGE: Record<PromoStatus, string> = {
  active: "bg-success/15 text-success",
  scheduled: "bg-brand/12 text-brand",
  finished: "bg-ink-muted/15 text-ink-muted",
};

export default function PromosView() {
  const counts = promoCounts();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink sm:text-3xl">Акции</h1>
          <p className="mt-1 text-sm text-ink-muted">Промо и специальные предложения</p>
        </div>
        <button type="button" className="btn-glass-blue inline-flex items-center gap-2 self-start rounded-xl px-4 py-2.5 text-sm font-semibold">
          <Plus size={16} aria-hidden="true" /> Создать акцию
        </button>
      </div>

      <div className="grid grid-cols-3 gap-3 sm:gap-4">
        {([
          { label: "Активные", value: counts.active, tint: "text-success" },
          { label: "Запланированные", value: counts.scheduled, tint: "text-brand" },
          { label: "Завершённые", value: counts.finished, tint: "text-ink-muted" },
        ] as const).map((s) => (
          <div key={s.label} className="rounded-[20px] border border-border bg-card p-4 shadow-soft">
            <p className={`font-display text-2xl font-extrabold ${s.tint}`}>{s.value}</p>
            <p className="text-xs text-ink-muted sm:text-sm">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {PROMOS.map((p) => (
          <div key={p.id} className="flex flex-col rounded-[24px] border border-border bg-card p-5 shadow-soft">
            <div className="mb-3 flex items-start justify-between gap-3">
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-pink/15 text-brand-pink">
                <Gift size={20} aria-hidden="true" />
              </span>
              <span className={`rounded-full px-3 py-1 text-xs font-medium ${STATUS_BADGE[p.status]}`}>
                {PROMO_STATUS_LABEL[p.status]}
              </span>
            </div>
            <h3 className="text-base font-bold text-ink">{p.title}</h3>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">{p.description}</p>

            <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
              <div>
                <p className="text-xs text-ink-muted">{p.period}</p>
                <span className="mt-1 flex items-center gap-1">
                  {p.channels.map((id) => {
                    const ch = CHANNELS[id];
                    return ch.icon && ch.iconType !== "wordmark" ? (
                      <Image key={id} src={ch.icon} alt={ch.label} width={16} height={16} className="h-4 w-4 object-contain" />
                    ) : null;
                  })}
                </span>
              </div>
              <div className="text-right">
                <p className="font-display text-lg font-bold text-ink">{p.metricValue}</p>
                <p className="text-xs text-ink-muted">{p.metricLabel}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
