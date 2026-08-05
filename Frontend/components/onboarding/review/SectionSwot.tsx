"use client";

import type { BrandProfile, SwotInfo } from "@/lib/onboarding/types";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { SectionHead } from "@/components/onboarding/OnboardingChrome";
import EditableList from "./EditableList";

const DOT = {
  success: "bg-success",
  pink: "bg-brand-pink",
  brand: "bg-brand",
  orange: "bg-brand-orange",
} as const;

function Quadrant({
  title,
  value,
  onChange,
  color,
}: {
  title: string;
  value: string[];
  onChange: (v: string[]) => void;
  color: keyof typeof DOT;
}) {
  return (
    <div className="rounded-[24px] border border-border bg-gradient-to-b from-brand/[0.08] to-card/85 p-5 shadow-soft ring-1 ring-inset ring-white/[0.04] backdrop-blur-xl">
      <p className="mb-3 flex items-center gap-2 font-bold text-ink">
        <span className={`h-2.5 w-2.5 rounded-full ${DOT[color]}`} aria-hidden="true" />
        {title}
      </p>
      <EditableList value={value} onChange={onChange} placeholder="Пункт" addLabel="Добавить" />
    </div>
  );
}

export default function SectionSwot({ profile }: { profile: BrandProfile }) {
  const { updateProfile } = useOnboarding();
  const s = profile.swot;
  const patch = (key: keyof SwotInfo, items: string[]) => updateProfile({ swot: { ...s, [key]: items } });

  return (
    <div className="flex flex-col gap-6">
      <SectionHead
        icon="scale"
        kicker="Шаг 3 · Позиция"
        tone="purple"
        title="Сильные и слабые стороны"
        text="На сильных сторонах ИИ строит аргументы в постах, слабые — обходит стороной."
      />
      <div className="grid gap-4 sm:grid-cols-2">
        <Quadrant title="Сильные стороны" value={s.strengths} onChange={(v) => patch("strengths", v)} color="success" />
        <Quadrant title="Слабые стороны" value={s.weaknesses} onChange={(v) => patch("weaknesses", v)} color="pink" />
        <Quadrant title="Возможности" value={s.opportunities} onChange={(v) => patch("opportunities", v)} color="brand" />
        <Quadrant title="Угрозы" value={s.threats} onChange={(v) => patch("threats", v)} color="orange" />
      </div>
    </div>
  );
}
