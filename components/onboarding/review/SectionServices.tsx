"use client";

import Icon from "@/components/ui/Icon";
import type { BrandProfile, ServiceItem } from "@/lib/onboarding/types";
import { TextArea, TextInput } from "@/components/onboarding/Field";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { SectionHead } from "@/components/onboarding/OnboardingChrome";

const GRADIENTS = [
  "from-success to-brand",
  "from-brand to-brand-purple",
  "from-brand-purple to-brand-pink",
];

export default function SectionServices({ profile }: { profile: BrandProfile }) {
  const { updateProfile } = useOnboarding();
  const services = profile.services;
  const setServices = (next: ServiceItem[]) => updateProfile({ services: next });
  const setAt = (i: number, patch: Partial<ServiceItem>) => setServices(services.map((s, idx) => (idx === i ? { ...s, ...patch } : s)));
  const removeAt = (i: number) => setServices(services.filter((_, idx) => idx !== i));
  const add = () => setServices([...services, { title: "", items: "" }]);

  return (
    <div className="flex flex-col gap-6">
      <SectionHead
        icon="grid"
        kicker="Шаг 4 · Предложение"
        tone="pink"
        title="Услуги и товары"
        text="То, о чём будут посты. Чем конкретнее список, тем точнее тексты."
      />
      <div className="flex flex-col gap-3">
        {services.map((s, i) => (
          <div key={i} className="flex items-start gap-4 rounded-[24px] border border-border bg-gradient-to-b from-brand/[0.08] to-card/85 p-4 shadow-soft ring-1 ring-inset ring-white/[0.04] backdrop-blur-xl">
            <span
              className={`mt-1 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${GRADIENTS[i % GRADIENTS.length]} text-white`}
            >
              <Icon name="sparkles" size={20} aria-hidden="true" />
            </span>
            <div className="flex min-w-0 flex-1 flex-col gap-2">
              <TextInput value={s.title} placeholder="Название услуги" onChange={(e) => setAt(i, { title: e.target.value })} />
              <TextArea value={s.items} placeholder="Что входит" className="min-h-16" onChange={(e) => setAt(i, { items: e.target.value })} />
            </div>
            <button
              type="button"
              onClick={() => removeAt(i)}
              aria-label="Удалить услугу"
              className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-ink-muted transition hover:bg-red-500/10 hover:text-red-500"
            >
              <Icon name="close" size={16} aria-hidden="true" />
            </button>
          </div>
        ))}
      </div>
      <button
        type="button"
        onClick={add}
        className="inline-flex w-fit items-center gap-1.5 rounded-full px-3 py-2 text-sm font-medium text-brand transition hover:bg-brand/10"
      >
        <Icon name="plus" size={16} aria-hidden="true" /> Добавить услугу
      </button>
    </div>
  );
}
