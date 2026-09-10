import Link from "next/link";
import Icon from "@/components/ui/Icon";
import type { AccentColor, AiTip } from "@/lib/dashboard/types";

const CHIP: Record<AccentColor, string> = {
  brand: "bg-brand/10 text-brand",
  purple: "bg-brand-purple/10 text-brand-purple",
  pink: "bg-brand-pink/10 text-brand-pink",
  orange: "bg-brand-orange/10 text-brand-orange",
  success: "bg-success/10 text-success",
};

const HOVER_BORDER: Record<AccentColor, string> = {
  brand: "hover:border-brand/40",
  purple: "hover:border-brand-purple/40",
  pink: "hover:border-brand-pink/40",
  orange: "hover:border-brand-orange/40",
  success: "hover:border-success/40",
};

/** Лёгкая подсветка в цвет совета: карточки перестают выглядеть одинаковыми. */
const TINT: Record<AccentColor, string> = {
  brand: "from-brand/[0.07]",
  purple: "from-brand-purple/[0.07]",
  pink: "from-brand-pink/[0.07]",
  orange: "from-brand-orange/[0.07]",
  success: "from-success/[0.07]",
};

export default function AiTips({ tips }: { tips: AiTip[] }) {
  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-base font-bold text-ink sm:text-lg">
          <Icon name="sparkles" size={18} className="text-brand" aria-hidden="true" />
          Рекомендации UCust
        </h2>
        <span className="text-xs font-medium text-ink-muted">{tips.length} на сегодня</span>
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3 [&>*]:min-w-0 stagger-grid">
        {tips.map((t) => (
          <div
            key={t.id}
            className={`flex h-full flex-col rounded-[20px] border border-border bg-gradient-to-br to-card p-5 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift ${TINT[t.color]} ${HOVER_BORDER[t.color]}`}
          >
            <span
              className={`inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${CHIP[t.color]}`}
              aria-hidden="true"
            >
              <Icon name={t.icon} size={16} />
            </span>

            <p className="mt-3.5 text-sm font-semibold leading-snug text-ink">{t.title}</p>
            <p className="mt-1.5 flex-1 text-[0.8125rem] leading-relaxed text-ink-muted">{t.text}</p>

            <Link
              href={t.href}
              className="btn-glass-blue mt-4 inline-flex w-full items-center justify-center gap-1.5 px-4 py-2.5 text-xs font-semibold"
            >
              Перейти <Icon name="arrow-right" size={14} aria-hidden="true" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
