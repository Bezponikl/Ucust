"use client";

import type { BrandProfile } from "@/lib/onboarding/types";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { Panel, SectionHead } from "@/components/onboarding/OnboardingChrome";
import EditableList from "./EditableList";

export default function SectionGoals({ profile }: { profile: BrandProfile }) {
  const { updateProfile } = useOnboarding();

  return (
    <div className="flex flex-col gap-6">
      <SectionHead
        icon="star"
        kicker="Шаг 5 · Результат"
        tone="orange"
        title="Цели"
        text="Ради чего всё это. По целям ИИ решает, о чём писать чаще и с каким призывом."
      />
      <Panel title="Цели контента" hint="Например: приводить новых гостей, возвращать постоянных">
        <EditableList
          value={profile.goals}
          onChange={(goals) => updateProfile({ goals })}
          placeholder="Цель"
          addLabel="Добавить цель"
        />
      </Panel>
      <Panel title="Стиль общения с клиентами" hint="Каким голосом бренд говорит в постах и ответах">
        <EditableList
          value={profile.tone}
          onChange={(tone) => updateProfile({ tone })}
          placeholder="Например: дружелюбный"
          addLabel="Добавить стиль"
        />
      </Panel>
    </div>
  );
}
