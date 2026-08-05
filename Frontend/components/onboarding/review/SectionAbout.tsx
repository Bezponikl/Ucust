"use client";

import type { BrandProfile } from "@/lib/onboarding/types";
import { Field, TextArea, TextInput } from "@/components/onboarding/Field";
import { Panel, SectionHead } from "@/components/onboarding/OnboardingChrome";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";

export default function SectionAbout({ profile }: { profile: BrandProfile }) {
  const { updateProfile } = useOnboarding();
  const name = profile.name.trim();
  const initial = name ? name.replace(/[«»"']/g, "").charAt(0).toUpperCase() : "?";

  return (
    <div className="flex flex-col gap-6">
      <SectionHead
        icon="brain"
        kicker="Шаг 1 · Профиль"
        title="О проекте"
        text="Так UCust понял ваш бизнес. Проверьте и поправьте — на этом строится весь контент."
      />

      {/* Визитка бренда: то, что ИИ держит в голове при каждой генерации */}
      <div className="relative overflow-hidden rounded-[24px] border border-border bg-gradient-to-br from-brand/30 via-brand/10 to-transparent p-5 sm:p-6">
        <div className="flex items-center gap-4">
          <span className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-brand font-display text-2xl font-black text-white shadow-lift">
            {initial}
          </span>
          <div className="min-w-0">
            <p className="truncate font-display text-xl font-extrabold text-ink sm:text-2xl">
              {name || "Ваш бренд"}
            </p>
            <p className="mt-0.5 truncate text-sm text-ink-muted">{profile.field || "Сфера не указана"}</p>
          </div>
        </div>

        {profile.tone.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {profile.tone.map((t) => (
              <span key={t} className="rounded-full bg-card/70 px-3 py-1 text-xs font-medium text-ink backdrop-blur-sm">
                {t}
              </span>
            ))}
          </div>
        )}
      </div>

      <Panel className="flex flex-col gap-5">
        <Field label="Название">
          <TextInput value={profile.name} onChange={(e) => updateProfile({ name: e.target.value })} />
        </Field>
        <Field label="Сфера деятельности">
          <TextInput value={profile.field} onChange={(e) => updateProfile({ field: e.target.value })} />
        </Field>
        <Field label="Позиционирование" hint="Одно-два предложения: чем вы отличаетесь и для кого работаете">
          <TextArea value={profile.positioning} onChange={(e) => updateProfile({ positioning: e.target.value })} />
        </Field>
      </Panel>
    </div>
  );
}
