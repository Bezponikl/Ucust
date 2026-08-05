import Link from "next/link";
import Icon from "@/components/ui/Icon";
import type { PlanDay, PostStatus } from "@/lib/dashboard/types";

// Тинт-фон + акцент числа + точка статуса
const STATUS: Record<Exclude<PostStatus, "none">, { cell: string; num: string; dot: string }> = {
  published: { cell: "border-success/25 bg-success/8", num: "text-success", dot: "bg-success" },
  scheduled: { cell: "border-brand/25 bg-brand/8", num: "text-brand", dot: "bg-brand" },
  draft: { cell: "border-border bg-surface-soft", num: "text-ink", dot: "bg-ink-muted" },
};

export default function WeekPreview({ week }: { week: PlanDay[] }) {
  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-bold text-ink sm:text-lg">Контент-план</h2>
        <Link
          href="/dashboard/content"
          className="inline-flex items-center gap-1 text-sm font-medium text-brand hover:text-brand-hover"
        >
          Все посты <Icon name="arrow-right" size={14} aria-hidden="true" />
        </Link>
      </div>

      <div className="grid grid-cols-7 gap-1.5 sm:gap-2">
        {week.map((d) => {
          // Подпись дня недели — над обводкой, сама ячейка (в рамке) содержит число + статус
          const label = <span className="text-[0.6875rem] text-ink-muted">{d.weekday}</span>;

          if (d.status === "none") {
            // Пустой день — кнопка «добавить пост»
            return (
              <div key={d.day} className="flex flex-col items-center gap-1.5">
                {label}
                <Link
                  href={`/dashboard/create?day=${d.day}`}
                  title={`${d.weekday} · создать пост`}
                  aria-label={`${d.weekday} ${d.day} — создать пост`}
                  className="group flex aspect-square w-full flex-col items-center justify-center gap-1.5 rounded-2xl border border-dashed border-border transition hover:border-brand hover:bg-brand/5"
                >
                  <span className="font-display text-lg font-bold text-ink-muted">{d.day}</span>
                  <span className="flex h-1.5 items-center text-ink-muted transition group-hover:text-brand">
                    <Icon name="plus" size={12} aria-hidden="true" />
                  </span>
                </Link>
              </div>
            );
          }

          const s = STATUS[d.status];
          return (
            <div key={d.day} className="flex flex-col items-center gap-1.5">
              {label}
              <Link
                href={`/dashboard/content?day=${d.day}`}
                title={`${d.weekday} ${d.day}`}
                aria-label={`${d.weekday} ${d.day}`}
                className={`flex aspect-square w-full flex-col items-center justify-center gap-1.5 rounded-2xl border transition hover:-translate-y-0.5 hover:shadow-lift ${s.cell}`}
              >
                <span className={`font-display text-lg font-bold ${s.num}`}>{d.day}</span>
                <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} aria-hidden="true" />
              </Link>
            </div>
          );
        })}
      </div>

      <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
        <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-success" /> Опубликован</span>
        <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-brand" /> Запланирован</span>
        <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-ink-muted" /> Черновик</span>
        <span className="inline-flex items-center gap-1.5"><Icon name="plus" size={12} className="text-ink-muted" /> Свободно</span>
      </div>
    </div>
  );
}
