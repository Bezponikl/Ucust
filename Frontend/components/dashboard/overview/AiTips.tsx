import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import type { AccentColor, AiTip } from "@/lib/dashboard/types";

const DOT: Record<AccentColor, string> = {
  brand: "bg-brand",
  purple: "bg-brand-purple",
  pink: "bg-brand-pink",
  orange: "bg-brand-orange",
  success: "bg-success",
};

export default function AiTips({ tips }: { tips: AiTip[] }) {
  return (
    <div>
      <h2 className="mb-3 flex items-center gap-2 text-base font-bold text-ink sm:text-lg">
        <Sparkles size={18} className="text-brand" aria-hidden="true" />
        Рекомендации AI
      </h2>
      <div className="grid gap-3 lg:grid-cols-3">
        {tips.map((t) => (
          <div key={t.id} className="flex flex-col rounded-[20px] border border-border bg-card p-4 shadow-soft">
            <p className="flex items-start gap-2 text-sm font-semibold text-ink">
              <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${DOT[t.color]}`} aria-hidden="true" />
              {t.title}
            </p>
            <p className="mt-1.5 pl-4 text-xs leading-relaxed text-ink-muted">{t.text}</p>
            <Link
              href={t.href}
              className="btn-glass-blue mt-4 inline-flex items-center justify-center gap-1.5 rounded-xl px-4 py-2.5 text-xs font-semibold"
            >
              Перейти <ArrowRight size={14} aria-hidden="true" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
