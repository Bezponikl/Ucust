import type { ReactNode } from "react";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";

/** Честная заглушка для блоков, у которых пока нет бэкенда. */
export default function ComingSoon({
  icon = "clock",
  title,
  text,
  action,
}: {
  icon?: IconName;
  title: string;
  text: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex min-h-52 flex-col items-center justify-center gap-3 rounded-[24px] border border-dashed border-border bg-card/50 px-6 py-10 text-center">
      <span className="relative flex h-14 w-14 items-center justify-center">
        <span className="absolute inset-0 rounded-2xl bg-brand/12" aria-hidden="true" />
        <span className="relative flex h-11 w-11 items-center justify-center rounded-xl bg-brand/15 text-brand">
          <Icon name={icon} size={22} aria-hidden="true" />
        </span>
      </span>
      <span className="rounded-full bg-surface-soft px-3 py-1 text-xs font-semibold uppercase tracking-wider text-ink-muted">
        Скоро
      </span>
      <p className="max-w-md text-lg font-bold text-ink">{title}</p>
      <p className="max-w-md text-sm leading-relaxed text-ink-muted">{text}</p>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}