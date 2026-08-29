"use client";

import type { ReactNode } from "react";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";

/**
 * Общий визуальный язык онбординга: мягкое бренд-свечение вместо плоской
 * заливки, стеклянные панели и единая шапка секции.
 */

/** Фон: два приглушённых пятна света. Живёт под контентом, кликов не ловит. */
export function OnboardingBackdrop() {
  return (
    /* z-0, а не -z-10: отрицательный слой уходит под непрозрачный фон body */
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div className="absolute -left-40 -top-56 h-[36rem] w-[36rem] rounded-full bg-brand/25 blur-[110px] dark:bg-brand/30" />
      <div className="absolute -right-28 top-1/4 h-[30rem] w-[30rem] rounded-full bg-brand-purple/20 blur-[120px] dark:bg-brand-purple/24" />
      <div className="absolute bottom-[-14rem] left-1/3 h-[28rem] w-[28rem] rounded-full bg-brand-orange/14 blur-[130px]" />
    </div>
  );
}

/** Панель контента: карточка со стеклом и тонким верхним бликом. */
export function Panel({
  children,
  className = "",
  title,
  hint,
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  hint?: string;
}) {
  return (
    <section
      className={`rounded-[24px] border border-border bg-gradient-to-b from-brand/[0.08] to-card/85 p-5 shadow-soft ring-1 ring-inset ring-white/[0.04] backdrop-blur-xl sm:p-6 ${className}`}
    >
      {title && (
        <header className="mb-4">
          <h2 className="text-sm font-bold text-ink">{title}</h2>
          {hint && <p className="mt-0.5 text-xs text-ink-muted">{hint}</p>}
        </header>
      )}
      {children}
    </section>
  );
}

/** Шапка секции: значок механики + кикер + заголовок. */
export function SectionHead({
  icon,
  kicker,
  title,
  text,
  tone = "brand",
}: {
  icon: IconName;
  kicker: string;
  title: string;
  text: string;
  tone?: "brand" | "purple" | "pink" | "orange";
}) {
  const TONE = {
    brand:  "bg-brand/12 text-brand",
    purple: "bg-brand-purple/15 text-brand-purple",
    pink:   "bg-brand-pink/15 text-brand-pink",
    orange: "bg-brand-orange/15 text-brand-orange",
  } as const;

  return (
    <header className="flex items-start gap-4">
      <span className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${TONE[tone]}`}>
        <Icon name={icon} size={22} aria-hidden="true" />
      </span>
      <div className="min-w-0">
        <span className="text-xs font-semibold uppercase tracking-[0.14em] text-ink-muted">{kicker}</span>
        <h1 className="mt-1 text-2xl font-bold leading-tight text-ink sm:text-3xl">{title}</h1>
        <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">{text}</p>
      </div>
    </header>
  );
}
