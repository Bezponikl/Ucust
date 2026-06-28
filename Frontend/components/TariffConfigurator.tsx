"use client";

import { useMemo, useState } from "react";
import { SlidersHorizontal, HelpCircle } from "lucide-react";
import ModalShell from "./ModalShell";

// Базовая цена включает 10 публикаций и 1 проект.
const BASE = 1500;
const PER_PUBLICATION = 20; // за каждую публикацию свыше 10
const PER_PROJECT = 50; // за каждый проект свыше 1

const PUB_MIN = 10;
const PUB_MAX = 100;
const PROJ_MIN = 1;
const PROJ_MAX = 10;

const ADDONS = [
  { id: "stats", label: "Подробная статистика", price: 300 },
  { id: "plan", label: "План публикаций", price: 400 },
  { id: "reviews", label: "Автоответы на отзывы", price: 500 },
] as const;

type AddonId = (typeof ADDONS)[number]["id"];

export default function TariffConfigurator({
  open,
  onClose,
  onStart,
}: {
  open: boolean;
  onClose: () => void;
  onStart: () => void;
}) {
  const [publications, setPublications] = useState(25);
  const [projects, setProjects] = useState(2);
  const [addons, setAddons] = useState<Record<AddonId, boolean>>({
    stats: false,
    plan: false,
    reviews: false,
  });

  const total = useMemo(() => {
    const addonsSum = ADDONS.reduce(
      (sum, a) => sum + (addons[a.id] ? a.price : 0),
      0,
    );
    return (
      BASE +
      (publications - PUB_MIN) * PER_PUBLICATION +
      (projects - PROJ_MIN) * PER_PROJECT +
      addonsSum
    );
  }, [publications, projects, addons]);

  const toggleAddon = (id: AddonId) =>
    setAddons((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <ModalShell open={open} onClose={onClose} labelledBy="tariff-configurator-title">
      <div className="flex items-center gap-2.5">
        <SlidersHorizontal size={22} className="shrink-0 text-brand" aria-hidden="true" />
        <h2 id="tariff-configurator-title" className="text-xl font-bold text-ink sm:text-2xl">
          Настройте свой тариф
        </h2>
      </div>
      <p className="mt-1.5 text-sm text-ink-muted">
        Выберите нужные опции и мы рассчитаем стоимость
      </p>

      <div className="mt-6 flex flex-col gap-6">
        <SliderRow
          label="Количество публикаций в месяц"
          value={publications}
          min={PUB_MIN}
          max={PUB_MAX}
          onChange={setPublications}
          hint={`от ${PUB_MIN} до ${PUB_MAX} публикаций`}
        />
        <SliderRow
          label="Количество проектов"
          value={projects}
          min={PROJ_MIN}
          max={PROJ_MAX}
          onChange={setProjects}
          hint={`от ${PROJ_MIN} до ${PROJ_MAX} проектов`}
        />
      </div>

      <p className="mt-7 text-sm font-semibold text-ink">Дополнительные возможности</p>
      <div className="mt-3 flex flex-col gap-2.5">
        {ADDONS.map((addon) => (
          <AddonRow
            key={addon.id}
            label={addon.label}
            price={addon.price}
            active={addons[addon.id]}
            onToggle={() => toggleAddon(addon.id)}
          />
        ))}
      </div>

      <div className="panel-blue-glass mt-6 flex items-center justify-between rounded-2xl px-5 py-4">
        <span className="text-base font-semibold text-ink">Итого:</span>
        <span className="flex items-baseline gap-1.5">
          <span className="font-display text-2xl font-extrabold text-ink sm:text-3xl">
            {total.toLocaleString("ru-RU")}
          </span>
          <span className="text-sm text-ink-muted">руб/мес</span>
        </span>
      </div>

      <button
        type="button"
        onClick={onStart}
        className="btn-glass-blue mt-5 inline-flex w-full items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
      >
        Начать с этим тарифом
      </button>
    </ModalShell>
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
          <HelpCircle size={14} className="text-ink-muted/70" aria-hidden="true" />
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
        <HelpCircle size={14} className="text-ink-muted/70" aria-hidden="true" />
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
