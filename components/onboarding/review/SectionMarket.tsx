"use client";

import type { BrandProfile } from "@/lib/onboarding/types";
import { Field, TextArea, TextInput } from "@/components/onboarding/Field";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { Panel, SectionHead } from "@/components/onboarding/OnboardingChrome";
import EditableList from "./EditableList";
import CompetitorList from "./CompetitorList";

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
      {/* Парсер отдаёт конкурента строкой «Название (ссылка)» — в одном поле
          она обрезается на середине домена. Карточка разносит имя и домен. */}
      <Panel title="Конкуренты" hint="На кого ещё смотрит ваш клиент, выбирая между вами. Часть нашли автоматически — проверьте и дополните">
        <CompetitorList
          value={m.competitors}
          onChange={(competitors) => patchMarket({ competitors })}
        />
      </Panel>
      <div className="grid gap-4 sm:grid-cols-2">
        <Panel>
          <Field label="География">
            <TextInput value={m.geography} onChange={(e) => patchMarket({ geography: e.target.value })} />
          </Field>
        </Panel>
        <Panel>
          {/* Сегмент парсер описывает целым предложением — в однострочном поле
              оно обрезалось на середине, поэтому здесь текстовая область. */}
          <Field label="Сегмент">
            <TextArea
              rows={3}
              value={m.segment}
              onChange={(e) => patchMarket({ segment: e.target.value })}
              className="min-h-20"
            />
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
