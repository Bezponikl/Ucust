import type { BrandProfile } from "@/lib/onboarding/types";
import Chip from "@/components/onboarding/Chip";

const DOTS = ["bg-brand-orange", "bg-brand-purple", "bg-brand-pink", "bg-brand"];
const TONE_COLORS = ["orange", "purple", "pink", "brand"] as const;

export default function SectionGoals({ profile }: { profile: BrandProfile }) {
  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Цели</h1>
        <p className="mt-2 text-sm text-ink-muted">Чего хотим достичь с помощью контента</p>
      </header>
      <div className="flex flex-col gap-3">
        {profile.goals.map((g, i) => (
          <div key={g} className="flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3.5">
            <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${DOTS[i % DOTS.length]}`} aria-hidden="true" />
            <span className="text-sm text-ink">{g}</span>
          </div>
        ))}
      </div>
      <div className="rounded-2xl border border-border bg-card p-5">
        <p className="mb-3 text-sm font-semibold text-ink-muted">Стиль общения с клиентами</p>
        <div className="flex flex-wrap gap-2">
          {profile.tone.map((t, i) => (
            <Chip key={t} color={TONE_COLORS[i % TONE_COLORS.length]}>
              {t}
            </Chip>
          ))}
        </div>
      </div>
    </div>
  );
}
