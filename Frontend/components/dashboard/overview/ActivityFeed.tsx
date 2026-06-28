import type { AccentColor, ActivityItem } from "@/lib/dashboard/types";

const BORDER: Record<AccentColor, string> = {
  brand: "border-l-brand",
  purple: "border-l-brand-purple",
  pink: "border-l-brand-pink",
  orange: "border-l-brand-orange",
  success: "border-l-success",
};

export default function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
      <h2 className="mb-4 text-base font-bold text-ink sm:text-lg">Недавняя активность</h2>
      <ul className="flex flex-col gap-2.5">
        {items.map((a) => (
          <li
            key={a.id}
            className={`flex items-center justify-between gap-3 rounded-xl border-l-2 bg-surface-soft px-4 py-3 ${BORDER[a.color]}`}
          >
            <span className="text-sm text-ink">{a.text}</span>
            <span className="shrink-0 text-xs text-ink-muted">{a.time}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
