import Link from "next/link";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";

export type StatTone = "brand" | "purple" | "pink" | "orange" | "success";
export type DeltaTone = StatTone | "warning" | "muted";

const ICON_BG: Record<StatTone, string> = {
  brand:   "bg-brand/12 text-brand",
  purple:  "bg-brand-purple/15 text-brand-purple",
  pink:    "bg-brand-pink/15 text-brand-pink",
  orange:  "bg-brand-orange/15 text-brand-orange",
  success: "bg-success/15 text-success",
};

const SPARKLINE_STROKE: Record<StatTone, string> = {
  brand:   "#3B82F6",
  purple:  "#8B5CF6",
  pink:    "#EC4899",
  orange:  "#F97316",
  success: "#22C55E",
};

const DELTA_TONE_CLASS: Record<DeltaTone, string> = {
  brand:   "text-brand",
  purple:  "text-brand-purple",
  pink:    "text-brand-pink",
  orange:  "text-brand-orange",
  success: "text-success",
  warning: "text-brand-orange",
  muted:   "text-ink-muted",
};

function smoothPath(pts: [number, number][]): string {
  if (pts.length === 0) return "";
  let d = `M ${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
  for (let i = 1; i < pts.length; i++) {
    const [x0, y0] = pts[i - 1];
    const [x1, y1] = pts[i];
    const mx = ((x0 + x1) / 2).toFixed(1);
    d += ` C ${mx},${y0.toFixed(1)} ${mx},${y1.toFixed(1)} ${x1.toFixed(1)},${y1.toFixed(1)}`;
  }
  return d;
}

function Sparkline({ data, tone, uid }: { data: number[]; tone: StatTone; uid: string }) {
  if (data.length < 2) return null;
  const W = 200; const H = 48;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const padX = 1; const padY = 4;

  const pts: [number, number][] = data.map((v, i) => [
    padX + (i / (data.length - 1)) * (W - padX * 2),
    H - padY - ((v - min) / range) * (H - padY * 2),
  ]);

  const linePath = smoothPath(pts);
  const areaPath = `${linePath} L ${pts[pts.length - 1][0].toFixed(1)},${H} L ${pts[0][0].toFixed(1)},${H} Z`;
  const color = SPARKLINE_STROKE[tone];
  const gradId = `sg-${uid}`;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="mt-3 h-12 w-full" aria-hidden="true" preserveAspectRatio="none">
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.28" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill={`url(#${gradId})`} />
      <path d={linePath} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function StatCard({
  id = "stat",
  icon,
  iconTone = "brand",
  value,
  label,
  delta,
  deltaTone = "success",
  hint,
  hintTone = "muted",
  sparkline,
  href,
}: {
  id?: string;
  icon: IconName;
  iconTone?: StatTone;
  value: string;
  label: string;
  delta?: string;
  deltaTone?: DeltaTone;
  hint?: string;
  hintTone?: "muted" | "warning";
  sparkline?: number[];
  /** Если задан — карточка ведёт в подробный отчёт. */
  href?: string;
}) {
  const Wrapper = href ? Link : "div";
  const wrapperProps = href
    ? { href, className: "group flex flex-col rounded-[20px] border border-border bg-card p-4 shadow-soft outline-none transition hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-lift focus-visible:ring-2 focus-visible:ring-brand/50 sm:p-5" }
    : { className: "flex flex-col rounded-[20px] border border-border bg-card p-4 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift sm:p-5" };

  return (
    <Wrapper {...(wrapperProps as { href: string; className: string })}>
      {/* Top: icon + label */}
      <div className="mb-3 flex items-center justify-between gap-2">
        <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${ICON_BG[iconTone]}`}>
          <Icon name={icon} size={16} aria-hidden="true" />
        </span>
        <span className="flex min-w-0 items-center gap-1">
          <span className="truncate text-xs font-medium text-ink-muted">{label}</span>
          {href && (
            <Icon
              name="chevron-right"
              size={13}
              className="shrink-0 text-ink-muted opacity-0 transition group-hover:opacity-100"
              aria-hidden="true"
            />
          )}
        </span>
      </div>

      {/* Value + delta */}
      <div className="flex flex-wrap items-baseline gap-2">
        <span className="font-display text-2xl font-extrabold text-ink">{value}</span>
        {delta && (
          <span className={`text-xs font-semibold ${DELTA_TONE_CLASS[deltaTone]}`}>{delta}</span>
        )}
      </div>

      {/* Sparkline */}
      {sparkline && <Sparkline data={sparkline} tone={iconTone} uid={id} />}

      {/* Hint */}
      {hint && (
        <p className={`mt-2 text-[0.6875rem] ${
          hintTone === "warning" ? "font-semibold text-brand-orange" : "text-ink-muted"
        }`}>
          {hint}
        </p>
      )}
    </Wrapper>
  );
}
