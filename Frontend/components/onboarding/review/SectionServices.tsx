import { Sparkles } from "lucide-react";
import type { BrandProfile } from "@/lib/onboarding/types";

const GRADIENTS = [
  "from-success to-brand",
  "from-brand to-brand-purple",
  "from-brand-purple to-brand-pink",
];

export default function SectionServices({ profile }: { profile: BrandProfile }) {
  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Услуги и товары</h1>
        <p className="mt-2 text-sm text-ink-muted">Что вы предлагаете клиентам</p>
      </header>
      <div className="flex flex-col gap-3">
        {profile.services.map((s, i) => (
          <div key={s.title} className="flex items-center gap-4 rounded-2xl border border-border bg-card p-4">
            <span
              className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${GRADIENTS[i % GRADIENTS.length]} text-white`}
            >
              <Sparkles size={20} aria-hidden="true" />
            </span>
            <span className="leading-tight">
              <span className="block font-semibold text-ink">{s.title}</span>
              <span className="block text-sm text-ink-muted">{s.items}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
