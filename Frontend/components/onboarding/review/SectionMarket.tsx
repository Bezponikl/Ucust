import type { BrandProfile } from "@/lib/onboarding/types";
import Chip from "@/components/onboarding/Chip";

export default function SectionMarket({ profile }: { profile: BrandProfile }) {
  const m = profile.market;
  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Рынок</h1>
        <p className="mt-2 text-sm text-ink-muted">Основная информация о вашем рынке</p>
      </header>
      <div className="rounded-2xl border border-border bg-card p-5">
        <p className="mb-3 text-sm font-semibold text-ink-muted">Конкуренты</p>
        <div className="flex flex-wrap gap-2">
          {m.competitors.map((c) => (
            <Chip key={c} color="purple">
              {c}
            </Chip>
          ))}
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-border bg-card p-5">
          <p className="mb-1 text-sm font-semibold text-ink-muted">География</p>
          <p className="text-sm text-ink">{m.geography}</p>
        </div>
        <div className="rounded-2xl border border-border bg-card p-5">
          <p className="mb-1 text-sm font-semibold text-ink-muted">Сегмент</p>
          <p className="text-sm text-ink">{m.segment}</p>
        </div>
      </div>
      <div className="rounded-2xl border border-border bg-card p-5">
        <p className="mb-3 text-sm font-semibold text-ink-muted">Тренды рынка</p>
        <div className="flex flex-wrap gap-2">
          {m.trends.map((t) => (
            <Chip key={t} color="success">
              {t}
            </Chip>
          ))}
        </div>
      </div>
    </div>
  );
}
