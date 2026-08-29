import StatCard from "../StatCard";
import type { IconName } from "@/lib/icons/solar";
import type { Stat, StatIcon } from "@/lib/dashboard/types";

const ICONS: Record<StatIcon, IconName> = {
  views:       "eye",
  engagement:  "trending",
  subscribers: "user-plus",
  reviews:     "message",
};

/** Клик по показателю ведёт туда, где его можно разобрать подробно. */
const HREFS: Record<StatIcon, string> = {
  views:       "/dashboard/analytics?metric=reach",
  engagement:  "/dashboard/analytics?metric=engagement",
  subscribers: "/dashboard/analytics?metric=subscribers",
  reviews:     "/dashboard/reviews",
};

export default function StatCards({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4 stagger-grid">
      {stats.map((s) => (
        <StatCard
          key={s.id}
          id={s.id}
          icon={ICONS[s.icon]}
          iconTone={s.color}
          value={s.value}
          label={s.label}
          delta={s.delta}
          deltaTone={s.hintTone === "warning" ? "warning" : "success"}
          hint={s.hint}
          hintTone={s.hintTone}
          sparkline={s.sparkline}
          href={HREFS[s.icon]}
        />
      ))}
    </div>
  );
}
