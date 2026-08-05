"use client";

import { useState } from "react";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import { SettingsCard } from "@/components/dashboard/settings/primitives";
import { TARIFF_PLANS, CURRENT_SUBSCRIPTION, PAYMENT_HISTORY, type TariffAccent } from "@/lib/dashboard/subscription";
import { toast } from "@/lib/toast";

const ACCENT: Record<TariffAccent, { name: string; check: string }> = {
  blue: { name: "text-brand", check: "text-brand" },
  gradient: { name: "text-gradient", check: "tariff-check-gradient" },
  purple: { name: "text-brand-purple", check: "text-brand-purple" },
};

/** Обводка карточки: подсвечивается тем акцентом, к которому относится ТЕКУЩИЙ тариф пользователя. */
function cardSurfaceClass(accent: TariffAccent, isCurrent: boolean): string {
  if (!isCurrent) return "border border-border bg-card shadow-soft hover:shadow-lift";
  if (accent === "blue") return "border border-brand/40 bg-card shadow-lift ring-1 ring-brand/20";
  if (accent === "purple") return "border border-brand-purple/40 bg-card shadow-lift ring-1 ring-brand-purple/20";
  return "tariff-border-gradient shadow-lift"; // gradient — двойной background-clip, свой border+bg
}

const fmt = (n: number) => n.toLocaleString("ru-RU");

export default function SubscriptionSettings() {
  const currentPlan = TARIFF_PLANS.find((p) => p.id === CURRENT_SUBSCRIPTION.planId)!;
  const [cancelled, setCancelled] = useState(false);

  const payMock = () => toast("Переход к оплате…");
  // Статус отмены виден прямо в карточке — тост исчезает, а вопрос «отменил или нет» остаётся
  const cancelMock = () => {
    if (cancelled) {
      setCancelled(false);
      toast("Подписка продлена — списание пройдёт как обычно");
      return;
    }
    setCancelled(true);
    toast("Подписка будет отменена в конце оплаченного периода");
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Градиент для галочек тарифа с accent="gradient" — SVG fill не красится через CSS, нужен linearGradient */}
      <svg width="0" height="0" aria-hidden="true" focusable="false">
        <defs>
          {/* Те же стопы, что у --gradient-brand (120deg: blue → purple → pink → orange) */}
          <linearGradient id="tariff-check-gradient" x1="0" y1="0" x2="1" y2="0.35">
            <stop offset="0%" stopColor="#4f7dff" />
            <stop offset="38%" stopColor="#7b5cff" />
            <stop offset="72%" stopColor="#ff5fa2" />
            <stop offset="100%" stopColor="#ff8c4b" />
          </linearGradient>
        </defs>
      </svg>

      <div>
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Подписка</h1>
        <p className="mt-0.5 text-sm text-ink-muted">Текущий тариф, смена плана и история платежей</p>
      </div>

      {/* ── Текущий тариф ── */}
      <div className="rounded-[24px] border border-brand/30 bg-brand/[0.03] p-5 shadow-soft sm:p-6">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm text-ink-muted">
              Ваш тариф: <span className="font-semibold text-brand">{currentPlan.name}</span>
            </p>
            <p className="font-display text-2xl font-extrabold text-ink sm:text-3xl">
              {fmt(currentPlan.price)} ₽<span className="text-sm font-normal text-ink-muted">/мес</span>
            </p>
          </div>
          <div className="flex flex-col gap-1.5 sm:items-end">
            <p className="text-xs text-ink-muted sm:text-right">
              {cancelled ? "Доступ сохраняется до" : "Дата следующего списания"}: {CURRENT_SUBSCRIPTION.renewsOn}
            </p>
            {cancelled && (
              <span className="uc-pop-in inline-flex items-center gap-1.5 rounded-full border border-brand-orange/40 bg-brand-orange/10 px-2.5 py-1 text-[0.6875rem] font-semibold text-brand-orange">
                <Icon name="clock" size={12} aria-hidden="true" /> Отмена запланирована
              </span>
            )}
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div className="flex items-center justify-between rounded-2xl border border-border bg-card px-4 py-3">
            <span className="text-sm text-ink-muted">Проекты</span>
            <span className="font-display text-lg font-bold text-ink">
              {CURRENT_SUBSCRIPTION.usedProjects}/{currentPlan.maxProjects}
            </span>
          </div>
          <div className="flex items-center justify-between rounded-2xl border border-border bg-card px-4 py-3">
            <span className="text-sm text-ink-muted">Посты</span>
            <span className="font-display text-lg font-bold text-ink">
              {CURRENT_SUBSCRIPTION.usedPosts}/{currentPlan.maxPosts}
            </span>
          </div>
        </div>

        <div className="mt-4 flex flex-col gap-2.5 sm:flex-row">
          <a href="#plans" className="btn-glass-blue inline-flex items-center justify-center px-5 py-2.5 text-sm font-semibold sm:w-auto">
            Сменить тариф
          </a>
          <button type="button" onClick={cancelMock} className="btn-glass inline-flex items-center justify-center px-5 py-2.5 text-sm font-semibold sm:w-auto">
            {cancelled ? "Возобновить подписку" : "Отменить подписку"}
          </button>
        </div>
      </div>

      {/* ── Полные карточки тарифов (как на лендинге) ── */}
      <div id="plans" className="grid grid-cols-1 gap-5 scroll-mt-6 sm:grid-cols-2 lg:grid-cols-3 stagger-grid">
        {TARIFF_PLANS.map((plan) => {
          const a = ACCENT[plan.accent];
          const isCurrent = plan.id === CURRENT_SUBSCRIPTION.planId;
          return (
            <div
              key={plan.id}
              className={`relative isolate flex flex-col rounded-[28px] p-6 transition hover:-translate-y-0.5 sm:p-7 ${cardSurfaceClass(plan.accent, isCurrent)}`}
            >
              <div className="mb-4 flex items-start justify-between gap-3">
                <h3 className={`font-display text-xl font-extrabold tracking-tight ${a.name}`}>{plan.name}</h3>
                {plan.highlighted && (
                  <span className="tariff-badge-gradient inline-flex items-center rounded-full px-2.5 py-1 text-[0.6875rem] font-semibold text-brand-purple">
                    Популярный
                  </span>
                )}
              </div>

              <p className="text-sm leading-relaxed text-ink-muted">{plan.tagline}</p>

              <p className="mt-5 flex items-baseline gap-1.5">
                <span className="font-display text-4xl font-extrabold tracking-tight text-ink sm:text-5xl">{fmt(plan.price)}</span>
                <span className="font-display text-sm text-ink-muted">₽/мес</span>
              </p>

              <ul className="mt-6 mb-7 flex flex-col gap-3 border-t border-border pt-5">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2.5 text-sm text-ink">
                    <Icon name="check-bold" size={18} className={`shrink-0 ${a.check}`} aria-hidden="true" />
                    {feature}
                  </li>
                ))}
              </ul>

              {isCurrent ? (
                <span className="mt-auto inline-flex cursor-default items-center justify-center gap-1.5 rounded-full border border-border bg-surface-soft px-6 py-3 text-sm font-semibold text-ink-muted">
                  <Icon name="check-bold" size={15} aria-hidden="true" /> Ваш тариф
                </span>
              ) : (
                <button type="button" onClick={payMock} className="btn-glass-blue mt-auto inline-flex items-center justify-center px-6 py-3 text-sm font-semibold">
                  Оплатить через ЮKassa
                </button>
              )}
            </div>
          );
        })}

        {/* Гибкий настраиваемый тариф — полноценная страница настройки, не модалка */}
        <div className="relative isolate flex flex-col rounded-[28px] border border-border bg-card p-6 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift sm:p-7">
          <div className="mb-4 flex items-center gap-2.5">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[12px] bg-brand-purple/12 text-brand-purple">
              <Icon name="sliders" size={18} aria-hidden="true" />
            </span>
            <h3 className="font-display text-xl font-extrabold tracking-tight text-brand-purple">Свой тариф</h3>
          </div>

          <p className="text-sm leading-relaxed text-ink-muted">Настройте под свои нужды.</p>

          <p className="mt-5 flex items-baseline gap-1.5">
            <span className="font-display text-lg font-medium text-ink-muted">от</span>
            <span className="font-display text-4xl font-extrabold tracking-tight text-ink sm:text-5xl">1 500</span>
            <span className="font-display text-sm text-ink-muted">₽/мес</span>
          </p>
          <p className="mt-1 text-xs text-ink-muted">Цена зависит от выбранных опций</p>

          <ul className="mt-6 mb-7 flex flex-col gap-3 border-t border-border pt-5">
            {[
              "Любое число постов и бизнесов",
              "Видео, акции и водяной знак бренда",
              "Единые входящие, ИИ-ответы и CRM",
              "Команда и персональный менеджер",
            ].map((feature) => (
              <li key={feature} className="flex items-center gap-2.5 text-sm text-ink">
                <Icon name="check-bold" size={18} className="shrink-0 text-brand-purple" aria-hidden="true" />
                {feature}
              </li>
            ))}
          </ul>

          <Link
            href="/dashboard/subscription/configure"
            className="btn-glass-blue mt-auto inline-flex items-center justify-center px-6 py-3 text-sm font-semibold"
          >
            Настроить
          </Link>
        </div>
      </div>

      <SettingsCard title="История платежей">
        <ul className="flex flex-col gap-2">
          {PAYMENT_HISTORY.map((r) => (
            <li key={r.id} className="flex items-center gap-3 rounded-2xl border border-border bg-surface-soft px-4 py-3">
              <Icon name="receipt" size={18} className="shrink-0 text-ink-muted" aria-hidden="true" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-ink">
                  {r.plan} · {r.amount.toLocaleString("ru-RU")} ₽
                </p>
                <p className="truncate text-xs text-ink-muted">{r.date}</p>
              </div>
              <span className={`shrink-0 text-xs font-medium ${r.status === "Оплачено" ? "text-success" : "text-red-500"}`}>
                {r.status}
              </span>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-ink-muted">
          Оплата обрабатывается сервисом ЮKassa — данные банковской карты не хранятся и не
          передаются UCust.
        </p>
      </SettingsCard>
    </div>
  );
}
