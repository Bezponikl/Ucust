import { Eye, TrendingUp, UserPlus, MessageSquare, type LucideIcon } from "lucide-react";
import type { AccentColor, Stat, StatIcon } from "@/lib/dashboard/types";

const ICONS: Record<StatIcon, LucideIcon> = {
  views: Eye,
  engagement: TrendingUp,
  subscribers: UserPlus,
  reviews: MessageSquare,
};

const BG: Record<AccentColor, string> = {
  brand: "bg-brand/12 text-brand",
  purple: "bg-brand-purple/15 text-brand-purple",
  pink: "bg-brand-pink/15 text-brand-pink",
  orange: "bg-brand-orange/15 text-brand-orange",
  success: "bg-success/15 text-success",
};

export default function StatCards({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
      {stats.map((s) => {
        const Icon = ICONS[s.icon];
        return (
          <div key={s.id} className="rounded-[20px] border border-border bg-card p-4 shadow-soft sm:p-5">
            <span className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl ${BG[s.color]}`}>
              <Icon size={18} aria-hidden="true" />
            </span>
            <p className="flex items-baseline gap-2">
              <span className="font-display text-2xl font-extrabold text-ink">{s.value}</span>
              {s.delta && <span className="text-xs font-semibold text-success">{s.delta}</span>}
            </p>
            <p className="mt-0.5 text-sm font-medium text-ink">{s.label}</p>
            <p className="text-xs text-ink-muted">{s.hint}</p>
          </div>
        );
      })}
    </div>
  );
}
