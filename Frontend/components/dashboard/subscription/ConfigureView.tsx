"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import { SettingsCard } from "@/components/dashboard/settings/primitives";
import { toast } from "@/lib/toast";

// Базовая цена включает 10 публикаций, 1 бизнес и 1 пользователя.
const BASE = 1500;
const PER_PUBLICATION = 20; // за каждую публикацию свыше 10
const PER_BUSINESS = 50; // за каждый бизнес свыше 1
const PER_MEMBER = 150; // за каждого пользователя команды свыше 1

const PUB_MIN = 10;
const PUB_MAX = 150;
const BIZ_MIN = 1;
const BIZ_MAX = 20;
const MEMBER_MIN = 1;
const MEMBER_MAX = 10;

type AddonId =
  | "video"
  | "freegen"
  | "promo"
  | "watermark"
  | "inbox"
  | "autoreply"
  | "crm"
  | "analytics"
  | "priority"
  | "manager";

type Addon = { id: AddonId; label: string; price: number };

// Доп-возможности сгруппированы по смыслу — так конфигуратор читается,
// даже когда опций много.
const ADDON_GROUPS: { title: string; items: Addon[] }[] = [
  {
    title: "Контент",
    items: [
      { id: "video", label: "Генерация видео", price: 700 },
      { id: "freegen", label: "Генерация постов по запросу", price: 500 },
      { id: "promo", label: "Акции и промо", price: 400 },
      { id: "watermark", label: "Водяной знак бренда", price: 200 },
    ],
  },
  {
    title: "Клиенты",
    items: [
      { id: "inbox", label: "Единые входящие", price: 400 },
      { id: "autoreply", label: "ИИ-автоответы на отзывы и комментарии", price: 500 },
      { id: "crm", label: "CRM клиентов", price: 600 },
    ],
  },
  {
    title: "Аналитика и поддержка",
    items: [
      { id: "analytics", label: "Расширенная аналитика", price: 300 },
      { id: "priority", label: "Приоритетная поддержка", price: 300 },
      { id: "manager", label: "Персональный менеджер", price: 900 },
    ],
  },
];

const ALL_ADDONS: Addon[] = ADDON_GROUPS.flatMap((g) => g.items);

export default function ConfigureView() {
  const router = useRouter();
  const [publications, setPublications] = useState(25);
  const [businesses, setBusinesses] = useState(2);
  const [members, setMembers] = useState(1);
  const [addons, setAddons] = useState<Record<AddonId, boolean>>(
    () =>
      Object.fromEntries(ALL_ADDONS.map((a) => [a.id, false])) as Record<
        AddonId,
        boolean
      >,
  );

  const total = useMemo(() => {
    const addonsSum = ALL_ADDONS.reduce(
      (sum, a) => sum + (addons[a.id] ? a.price : 0),
      0,
    );
    return (
      BASE +
      (publications - PUB_MIN) * PER_PUBLICATION +
      (businesses - BIZ_MIN) * PER_BUSINESS +
      (members - MEMBER_MIN) * PER_MEMBER +
      addonsSum
    );
  }, [publications, businesses, members, addons]);

  const toggleAddon = (id: AddonId) =>
    setAddons((prev) => ({ ...prev, [id]: !prev[id] }));

  const start = () => {
    toast("Переход к оплате…");
    router.push("/dashboard/subscription");
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => router.push("/dashboard/subscription")}
          aria-label="Назад"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-border bg-card text-ink-muted transition hover:text-ink"
        >
          <Icon name="arrow-left" size={18} aria-hidden="true" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-ink sm:text-2xl">Настроить тариф</h1>
          <p className="mt-0.5 text-sm text-ink-muted">Выберите нужные опции — мы рассчитаем стоимость</p>
        </div>
      </div>

      <SettingsCard title="Объёмы">
        <div className="flex flex-col gap-6">
          <SliderRow
            label="Публикаций в месяц"
            value={publications}
            min={PUB_MIN}
            max={PUB_MAX}
            onChange={setPublications}
            hint={`от ${PUB_MIN} до ${PUB_MAX} публикаций`}
          />
          <SliderRow
            label="Количество бизнесов"
            value={businesses}
            min={BIZ_MIN}
            max={BIZ_MAX}
            onChange={setBusinesses}
            hint={`от ${BIZ_MIN} до ${BIZ_MAX} бизнесов`}
          />
          <SliderRow
            label="Пользователей в команде"
            value={members}
            min={MEMBER_MIN}
            max={MEMBER_MAX}
            onChange={setMembers}
            hint={`от ${MEMBER_MIN} до ${MEMBER_MAX} пользователей`}
          />
        </div>
      </SettingsCard>

      <SettingsCard title="Дополнительные возможности">
        <div className="flex flex-col gap-5">
          {ADDON_GROUPS.map((group) => (
            <div key={group.title}>
              <p className="kicker mb-2.5 text-xs text-ink-muted">{group.title}</p>
              <div className="flex flex-col gap-2.5">
                {group.items.map((addon) => (
                  <AddonRow
                    key={addon.id}
                    label={addon.label}
                    price={addon.price}
                    active={addons[addon.id]}
                    onToggle={() => toggleAddon(addon.id)}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </SettingsCard>

      {/* Цена не уезжает вниз: пока крутишь ползунки — итог виден на экране */}
      <div className="sticky bottom-3 z-30 flex flex-col gap-3 rounded-2xl border border-border/70 bg-card/85 px-5 py-4 shadow-lift backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between">
        <span className="flex items-baseline gap-2">
          <span className="text-sm font-semibold text-ink-muted">Итого:</span>
          <span className="font-display text-2xl font-extrabold tabular-nums text-ink sm:text-3xl">
            {total.toLocaleString("ru-RU")}
          </span>
          <span className="text-sm text-ink-muted">руб/мес</span>
        </span>

        <button
          type="button"
          onClick={start}
          className="btn-glass-blue inline-flex items-center justify-center px-6 py-3 text-sm font-semibold"
        >
          Начать с этим тарифом
        </button>
      </div>
    </div>
  );
}

function SliderRow({
  label,
  value,
  min,
  max,
  onChange,
  hint,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (v: number) => void;
  hint: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between gap-3">
        <span className="flex items-center gap-1.5 text-sm font-medium text-ink">
          {label}
          <Icon name="help" size={14} className="text-ink-muted/70" aria-hidden="true" />
        </span>
        <span className="font-display text-lg font-bold text-brand tabular-nums">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label={label}
        className="tariff-range mt-2.5 w-full"
      />
      <p className="mt-1 text-xs text-ink-muted">{hint}</p>
    </div>
  );
}

function AddonRow({
  label,
  price,
  active,
  onToggle,
}: {
  label: string;
  price: number;
  active: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-border bg-surface-soft px-4 py-3">
      <span className="flex items-center gap-1.5 text-sm font-medium text-ink">
        {label}
        <Icon name="help" size={14} className="text-ink-muted/70" aria-hidden="true" />
      </span>
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium text-ink-muted">+{price} руб</span>
        <button
          type="button"
          role="switch"
          aria-checked={active}
          aria-label={label}
          onClick={onToggle}
          className={`inline-flex h-6 w-11 shrink-0 items-center rounded-full p-0.5 transition-colors ${
            active ? "bg-brand" : "bg-border"
          }`}
        >
          <span
            className={`h-5 w-5 rounded-full bg-white shadow-sm transition-transform duration-200 ${
              active ? "translate-x-5" : "translate-x-0"
            }`}
          />
        </button>
      </div>
    </div>
  );
}
