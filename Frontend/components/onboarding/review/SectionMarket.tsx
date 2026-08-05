"use client";

import type { BrandProfile } from "@/lib/onboarding/types";
import { Field, TextInput } from "@/components/onboarding/Field";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { Panel, SectionHead } from "@/components/onboarding/OnboardingChrome";
import EditableList from "./EditableList";

export default function SectionMarket({ profile }: { profile: BrandProfile }) {
  const { updateProfile } = useOnboarding();
  const m = profile.market;
  const patchMarket = (patch: Partial<typeof m>) => updateProfile({ market: { ...m, ...patch } });

  return (
    <div className="flex flex-col gap-6">
      <SectionHead
        icon="trending"
        kicker="Шаг 2 · Контекст"
        title="Рынок"
        text="С кем вы соревнуетесь за внимание и что сейчас важно вашим клиентам."
      />
      <Panel title="Конкуренты" hint="На кого ещё смотрит ваш клиент, выбирая между вами">
        <EditableList
          value={m.competitors}
          onChange={(competitors) => patchMarket({ competitors })}
          placeholder="Название конкурента"
          addLabel="Добавить конкурента"
        />
      </Panel>
      <div className="grid gap-4 sm:grid-cols-2">
        <Panel>
          <Field label="География">
            <TextInput value={m.geography} onChange={(e) => patchMarket({ geography: e.target.value })} />
          </Field>
        </Panel>
        <Panel>
          <Field label="Сегмент">
            <TextInput value={m.segment} onChange={(e) => patchMarket({ segment: e.target.value })} />
          </Field>
        </Panel>
      </div>
      <Panel title="Тренды рынка" hint="Что влияет на спрос — это подсказывает темы для постов">
        <EditableList
          value={m.trends}
          onChange={(trends) => patchMarket({ trends })}
          placeholder="Тренд рынка"
          addLabel="Добавить тренд"
        />
      </Panel>
    </div>
  );
}
