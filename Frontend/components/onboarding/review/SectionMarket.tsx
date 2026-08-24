"use client";

import type { BrandProfile } from "@/lib/onboarding/types";
import { Field, TextInput } from "@/components/onboarding/Field";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { Panel, SectionHead } from "@/components/onboarding/OnboardingChrome";
import EditableList from "./EditableList";
import Icon from "@/components/ui/Icon";

export default function SectionMarket({ profile }: { profile: BrandProfile }) {
  const { updateProfile } = useOnboarding();
  const m = profile.market;
  const patchMarket = (patch: Partial<typeof m>) => updateProfile({ market: { ...m, ...patch } });

  const directList = m.directCompetitors?.length
    ? m.directCompetitors
    : (m.competitors?.slice(0, 3) || ["SMMplanner (https://smmplanner.com)", "LiveDune (https://livedune.com)", "Postmypost (https://postmypost.ru)"]);

  const networkList = m.networkCompetitors?.length
    ? m.networkCompetitors
    : ["Яндекс.Бизнес (https://business.yandex.ru)", "VK Реклама (https://ads.vk.com)", "TgStat (https://tgstat.ru)"];

  const localList = m.localCompetitors?.length
    ? m.localCompetitors
    : [`Локальные агентства г. ${m.geography || "Москва"}`, "Контент-фрилансеры", "Специалисты у дома"];

  const updateDirect = (directCompetitors: string[]) => {
    patchMarket({
      directCompetitors,
      competitors: [...directCompetitors, ...networkList, ...localList],
    });
  };

  const updateNetwork = (networkCompetitors: string[]) => {
    patchMarket({
      networkCompetitors,
      competitors: [...directList, ...networkCompetitors, ...localList],
    });
  };

  const updateLocal = (localCompetitors: string[]) => {
    patchMarket({
      localCompetitors,
      competitors: [...directList, ...networkList, ...localCompetitors],
    });
  };

  return (
    <div className="flex flex-col gap-6">
      <SectionHead
        icon="trending"
        kicker="Шаг 2 · Контекст"
        title="Рынок"
        text="С кем вы соревнуетесь за внимание и что сейчас важно вашим клиентам."
      />

      <div className="flex flex-col gap-4">
        <div>
          <h3 className="text-base font-semibold text-ink">Конкуренты</h3>
          <p className="text-xs text-ink-muted sm:text-sm">
            На кого ещё смотрит ваш клиент, выбирая между вами. Автоматически подобраны реальные сервисы из интернета.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {/* 1. Прямые конкуренты */}
          <div className="rounded-2xl border border-brand/20 bg-brand/[0.04] p-4.5 shadow-sm ring-1 ring-inset ring-brand/10">
            <div className="mb-3 flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand/15 text-brand">
                <Icon name="sparkles" size={16} aria-hidden="true" />
              </span>
              <div>
                <h4 className="text-sm font-semibold text-ink">Прямые конкуренты</h4>
                <span className="text-[11px] text-ink-muted">Аналогичные сервисы с ссылками</span>
              </div>
            </div>
            <EditableList
              value={directList}
              onChange={updateDirect}
              placeholder="https://... или название сервиса"
              addLabel="Добавить ссылку"
            />
          </div>

          {/* 2. Сетевые игроки */}
          <div className="rounded-2xl border border-border bg-card/60 p-4.5 shadow-sm ring-1 ring-inset ring-white/[0.04]">
            <div className="mb-3 flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-surface-soft text-ink-muted">
                <Icon name="shield" size={16} aria-hidden="true" />
              </span>
              <div>
                <h4 className="text-sm font-semibold text-ink">Сетевые игроки</h4>
                <span className="text-[11px] text-ink-muted">Федеральные сети и платформы</span>
              </div>
            </div>
            <EditableList
              value={networkList}
              onChange={updateNetwork}
              placeholder="https://... или бренд"
              addLabel="Добавить сеть"
            />
          </div>

          {/* 3. Локальные альтернативы */}
          <div className="rounded-2xl border border-border bg-card/60 p-4.5 shadow-sm ring-1 ring-inset ring-white/[0.04]">
            <div className="mb-3 flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-surface-soft text-ink-muted">
                <Icon name="grid" size={16} aria-hidden="true" />
              </span>
              <div>
                <h4 className="text-sm font-semibold text-ink">Локальные альтернативы</h4>
                <span className="text-[11px] text-ink-muted">Альтернативы и локальные игроки</span>
              </div>
            </div>
            <EditableList
              value={localList}
              onChange={updateLocal}
              placeholder="https://... или решение"
              addLabel="Добавить альтернативу"
            />
          </div>
        </div>
      </div>

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
