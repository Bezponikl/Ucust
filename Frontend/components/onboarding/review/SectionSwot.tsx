import type { BrandProfile } from "@/lib/onboarding/types";

const DOT = {
  success: "bg-success",
  pink: "bg-brand-pink",
  brand: "bg-brand",
  orange: "bg-brand-orange",
} as const;

function Quadrant({ title, items, color }: { title: string; items: string[]; color: keyof typeof DOT }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <p className="mb-3 flex items-center gap-2 font-bold text-ink">
        <span className={`h-2.5 w-2.5 rounded-full ${DOT[color]}`} aria-hidden="true" />
        {title}
      </p>
      <ul className="flex flex-col gap-1.5">
        {items.map((it) => (
          <li key={it} className="text-sm text-ink-muted">
            · {it}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function SectionSwot({ profile }: { profile: BrandProfile }) {
  const s = profile.swot;
  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">SWOT анализ</h1>
        <p className="mt-2 text-sm text-ink-muted">Сильные и слабые стороны вашего бизнеса</p>
      </header>
      <div className="grid gap-4 sm:grid-cols-2">
        <Quadrant title="Сильные стороны" items={s.strengths} color="success" />
        <Quadrant title="Слабые стороны" items={s.weaknesses} color="pink" />
        <Quadrant title="Возможности" items={s.opportunities} color="brand" />
        <Quadrant title="Угрозы" items={s.threats} color="orange" />
      </div>
    </div>
  );
}
