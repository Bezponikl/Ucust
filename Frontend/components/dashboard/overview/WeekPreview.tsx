import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { PlanDay, PostStatus } from "@/lib/dashboard/types";
import { CHANNELS } from "@/lib/channels";

const STATUS_DOT: Record<PostStatus, string> = {
  published: "bg-success",
  scheduled: "bg-brand",
  draft: "bg-ink-muted",
  none: "bg-transparent",
};

export default function WeekPreview({ week }: { week: PlanDay[] }) {
  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-bold text-ink sm:text-lg">Контент-план</h2>
        <Link href="/dashboard/content" className="inline-flex items-center gap-1 text-sm font-medium text-brand hover:text-brand-hover">
          Все посты <ArrowRight size={14} aria-hidden="true" />
        </Link>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {week.map((d) => (
          <div key={d.day} className="flex min-w-[84px] flex-1 flex-col items-center gap-2 rounded-2xl border border-border bg-surface-soft px-2 py-3">
            <span className="text-xs text-ink-muted">{d.weekday}</span>
            <span className="font-display text-lg font-bold text-ink">{d.day}</span>
            <span className={`h-2 w-2 rounded-full ${STATUS_DOT[d.status]}`} aria-hidden="true" />
            <span className="flex h-5 items-center gap-1">
              {d.channels.map((id) => {
                const ch = CHANNELS[id];
                return ch.icon && ch.iconType !== "wordmark" ? (
                  <Image key={id} src={ch.icon} alt={ch.label} width={16} height={16} className="h-4 w-4 object-contain" />
                ) : null;
              })}
            </span>
          </div>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
        <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-success" /> Опубликован</span>
        <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-brand" /> Запланирован</span>
        <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-ink-muted" /> Черновик</span>
      </div>
    </div>
  );
}
