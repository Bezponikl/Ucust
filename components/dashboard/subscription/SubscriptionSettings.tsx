"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import ModalShell from "@/components/ModalShell";
import { SettingsCard } from "@/components/dashboard/settings/primitives";
import { TARIFF_PLANS, CURRENT_SUBSCRIPTION, PAYMENT_HISTORY, type TariffAccent } from "@/lib/dashboard/subscription";
import { toast } from "@/lib/toast";
import { toMessage } from "@/lib/api/errors";
import { getTariff, listTariffs } from "@/lib/api/tariffs";
import { getMyQuota, getMySubscription, purchaseTariff } from "@/lib/api/quota";
import {
  formatDate,
  quotaView,
  subscriptionView,
  tariffView,
  type QuotaView,
  type SubscriptionView,
  type TariffView,
} from "@/lib/api/mapBilling";

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
  const [cancelled, setCancelled] = useState(false);
  /** Тарифы бэка. null — биллинг ещё не ответил или недоступен. */
  const [tariffs, setTariffs] = useState<TariffView[] | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionView | null>(null);
  const [quota, setQuota] = useState<QuotaView>({ limit: null, used: null, remaining: null });
  const [billingOffline, setBillingOffline] = useState(false);
  const [confirmTariff, setConfirmTariff] = useState<TariffView | null>(null);
  // Отмена подписки — необратимое для месяца действие, спрашиваем подтверждение
  const [confirmCancel, setConfirmCancel] = useState(false);
  const [busy, setBusy] = useState(false);

  const loadBilling = useCallback(async () => {
    // Три независимых запроса: подписки может не быть (404), а тарифы обязаны
    // отвечать даже гостю — поэтому падение одного не гасит остальные.
    const [tariffsRes, subRes, quotaRes] = await Promise.allSettled([
      listTariffs(),
      getMySubscription(),
      getMyQuota(),
    ]);

    setBillingOffline(tariffsRes.status === "rejected");
    if (tariffsRes.status === "fulfilled") setTariffs(tariffsRes.value.map(tariffView));
    setSubscription(subRes.status === "fulfilled" ? subscriptionView(subRes.value) : null);
    setQuota(quotaView(quotaRes.status === "fulfilled" ? quotaRes.value : null));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadBilling();
  }, [loadBilling]);

  const byName = new Map(
    (tariffs ?? []).map((t) => [(t.name ?? "").trim().toLowerCase(), t] as const),
  );
  /** Оформление берём из витрины, id и цену — из тарифа бэка, если он его знает. */
  const cards = TARIFF_PLANS.map((plan) => ({
    plan,
    server: byName.get(plan.name.toLowerCase()) ?? null,
  }));
  const extraTariffs = (tariffs ?? []).filter(
    (t) => !TARIFF_PLANS.some((p) => p.name.toLowerCase() === (t.name ?? "").trim().toLowerCase()),
  );

  const currentPlan = TARIFF_PLANS.find((p) => p.id === CURRENT_SUBSCRIPTION.planId)!;
  const currentServer = subscription?.tariffId
    ? (tariffs ?? []).find((t) => t.id === subscription.tariffId) ?? null
    : null;
  const currentName = subscription?.tariffName ?? currentServer?.name ?? currentPlan.name;
  const currentPrice = currentServer?.price ?? currentPlan.price;
  const renewsOn = formatDate(subscription?.renewsOn ?? null) ?? CURRENT_SUBSCRIPTION.renewsOn;
  const isCurrent = (server: TariffView | null, planId: string) =>
    subscription?.tariffId ? server?.id === subscription.tariffId : planId === CURRENT_SUBSCRIPTION.planId;

  /** Перед списанием перечитываем тариф: цена на витрине могла устареть. */
  const openPurchase = async (server: TariffView) => {
    setConfirmTariff(server);
    try {
      setConfirmTariff(tariffView(await getTariff(server.id)));
    } catch {
      /* не страшно: покажем то, что уже есть в списке */
    }
  };

  const confirmPurchase = async () => {
    if (!confirmTariff) return;
    setBusy(true);
    try {
      setSubscription(subscriptionView(await purchaseTariff(confirmTariff.id)));
      setConfirmTariff(null);
      await loadBilling();
      toast("Тариф подключён");
    } catch (err) {
      toast(toMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const payMock = () => toast("Тариф пока не заведён на сервере — оплата недоступна");
  // Статус отмены виден прямо в карточке — тост исчезает, а вопрос «отменил или нет» остаётся
  const cancelMock = () => {
    if (cancelled) {
      setCancelled(false);
      toast("Подписка продлена — списание пройдёт как обычно");
      return;
    }
    setConfirmCancel(true);
  };

  const doCancel = () => {
    setConfirmCancel(false);
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
        {billingOffline && (
          <p
            role="status"
            className="mt-2 inline-flex items-center gap-1.5 rounded-full border border-brand-orange/40 bg-brand-orange/10 px-3 py-1 text-xs font-medium text-brand-orange"
          >
            <Icon name="clock" size={13} aria-hidden="true" />
            Биллинг не отвечает — показаны стандартные условия, оплата недоступна
          </p>
        )}
      </div>

      {/* ── Текущий тариф ── */}
      <div className="rounded-[24px] border border-brand/30 bg-brand/[0.03] p-5 shadow-soft sm:p-6">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm text-ink-muted">
              Ваш тариф: <span className="font-semibold text-brand">{currentName}</span>
            </p>
            <p className="font-display text-2xl font-extrabold text-ink sm:text-3xl">
              {fmt(currentPrice)} ₽<span className="text-sm font-normal text-ink-muted">/мес</span>
            </p>
          </div>
          <div className="flex flex-col gap-1.5 sm:items-end">
            <p className="text-xs text-ink-muted sm:text-right">
              {cancelled ? "Доступ сохраняется до" : "Дата следующего списания"}: {renewsOn}
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
            <span className="text-sm text-ink-muted">Генерации</span>
            <span className="font-display text-lg font-bold text-ink">
              {quota.used ?? CURRENT_SUBSCRIPTION.usedPosts}/{quota.limit ?? currentPlan.maxPosts}
            </span>
          </div>
        </div>

        {/* Отмена уходит к правому краю и теряет вес кнопки: рядом с «Сменить тариф»
            её задевали случайно. Само действие — только через подтверждение. */}
        <div className="mt-5 flex flex-col gap-3 border-t border-brand/15 pt-4 sm:flex-row sm:items-center">
          <a href="#plans" className="btn-glass-blue inline-flex items-center justify-center px-5 py-2.5 text-sm font-semibold sm:w-auto">
            Сменить тариф
          </a>
          <button
            type="button"
            onClick={cancelMock}
            className={`inline-flex items-center justify-center gap-1.5 rounded-full px-4 py-2.5 text-sm font-medium transition sm:ml-auto sm:w-auto ${
              cancelled
                ? "text-brand hover:bg-brand/10"
                : "text-ink-muted hover:bg-surface-soft hover:text-ink"
            }`}
          >
            <Icon name={cancelled ? "refresh" : "close"} size={15} aria-hidden="true" />
            {cancelled ? "Возобновить подписку" : "Отменить подписку"}
          </button>
        </div>
      </div>

      {/* ── Полные карточки тарифов (как на лендинге) ── */}
      <div id="plans" className="grid grid-cols-1 gap-6 scroll-mt-6 sm:grid-cols-2 lg:grid-cols-3 stagger-grid">
        {cards.map(({ plan, server }) => {
          const a = ACCENT[plan.accent];
          const current = isCurrent(server, plan.id);
          return (
            <div
              key={plan.id}
              className={`relative isolate flex flex-col rounded-[28px] p-6 transition hover:-translate-y-0.5 sm:p-7 ${cardSurfaceClass(plan.accent, current)}`}
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
                <span className="font-display text-4xl font-extrabold tracking-tight text-ink sm:text-5xl">
                  {fmt(server?.price ?? plan.price)}
                </span>
                <span className="font-display text-sm text-ink-muted">₽/мес</span>
              </p>

              <ul className="mt-6 mb-6 flex flex-col gap-3 border-t border-border pt-6">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2.5 text-sm text-ink">
                    <Icon name="check-bold" size={18} className={`shrink-0 ${a.check}`} aria-hidden="true" />
                    {feature}
                  </li>
                ))}
              </ul>

              {current ? (
                <span className="mt-auto inline-flex cursor-default items-center justify-center gap-1.5 rounded-full border border-border bg-surface-soft px-6 py-3 text-sm font-semibold text-ink-muted">
                  <Icon name="check-bold" size={15} aria-hidden="true" /> Ваш тариф
                </span>
              ) : (
                <button
                  type="button"
                  onClick={() => (server ? void openPurchase(server) : payMock())}
                  className="btn-glass-blue mt-auto inline-flex items-center justify-center px-6 py-3 text-sm font-semibold"
                >
                  Оплатить через ЮKassa
                </button>
              )}
            </div>
          );
        })}

        {/* Тарифы, заведённые на бэке сверх витрины: показываем как есть */}
        {extraTariffs.map((server) => {
          const current = subscription?.tariffId === server.id;
          return (
            <div
              key={server.id}
              className={`relative isolate flex flex-col rounded-[28px] p-6 transition hover:-translate-y-0.5 sm:p-7 ${cardSurfaceClass("blue", current)}`}
            >
              <h3 className="font-display text-xl font-extrabold tracking-tight text-brand">
                {server.name ?? "Тариф"}
              </h3>
              {server.description && (
                <p className="mt-2 text-sm leading-relaxed text-ink-muted">{server.description}</p>
              )}

              <p className="mt-5 flex items-baseline gap-1.5">
                <span className="font-display text-4xl font-extrabold tracking-tight text-ink sm:text-5xl">
                  {server.price === null ? "—" : fmt(server.price)}
                </span>
                <span className="font-display text-sm text-ink-muted">₽/мес</span>
              </p>

              {server.features.length > 0 && (
                <ul className="mt-6 mb-6 flex flex-col gap-3 border-t border-border pt-6">
                  {server.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2.5 text-sm text-ink">
                      <Icon name="check-bold" size={18} className="shrink-0 text-brand" aria-hidden="true" />
                      {feature}
                    </li>
                  ))}
                </ul>
              )}

              {current ? (
                <span className="mt-auto inline-flex cursor-default items-center justify-center gap-1.5 rounded-full border border-border bg-surface-soft px-6 py-3 text-sm font-semibold text-ink-muted">
                  <Icon name="check-bold" size={15} aria-hidden="true" /> Ваш тариф
                </span>
              ) : (
                <button
                  type="button"
                  onClick={() => void openPurchase(server)}
                  className="btn-glass-blue mt-auto inline-flex items-center justify-center px-6 py-3 text-sm font-semibold"
                >
                  Подключить
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

          <ul className="mt-6 mb-6 flex flex-col gap-3 border-t border-border pt-6">
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

      {/* Подтверждение отмены: тариф перестаёт продлеваться, вернуть — только заново */}
      <ModalShell open={confirmCancel} onClose={() => setConfirmCancel(false)} labelledBy="cancel-sub-title">
        <div className="flex flex-col">
          <h2 id="cancel-sub-title" className="text-lg font-bold text-ink">Отменить подписку?</h2>
          <p className="mt-1.5 text-sm text-ink-muted">
            Тариф «{currentName}» перестанет продлеваться. Доступ и текущие квоты сохранятся
            до {renewsOn} — после этой даты автопубликации остановятся.
          </p>
          <div className="mt-6 flex flex-col gap-2 sm:flex-row-reverse">
            <button
              type="button"
              onClick={doCancel}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-full bg-red-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-600"
            >
              Отменить подписку
            </button>
            <button
              type="button"
              onClick={() => setConfirmCancel(false)}
              className="inline-flex flex-1 items-center justify-center rounded-full border border-border px-5 py-3 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft"
            >
              Оставить тариф
            </button>
          </div>
        </div>
      </ModalShell>

      {/* Подтверждение смены тарифа: списание — не то действие, которое делают одним кликом */}
      <ModalShell
        open={Boolean(confirmTariff)}
        onClose={() => setConfirmTariff(null)}
        labelledBy="buy-tariff-title"
      >
        <div className="flex flex-col">
          <h2 id="buy-tariff-title" className="text-lg font-bold text-ink">
            Подключить тариф «{confirmTariff?.name ?? "—"}»?
          </h2>
          <p className="mt-1.5 text-sm text-ink-muted">
            {confirmTariff?.price === null || confirmTariff?.price === undefined
              ? "Стоимость уточняется у сервиса биллинга."
              : `Спишется ${fmt(confirmTariff.price)} ₽ за месяц. Квоты обновятся сразу.`}
          </p>

          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={() => setConfirmTariff(null)}
              className="inline-flex flex-1 items-center justify-center rounded-full border border-border px-5 py-3 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft"
            >
              Отмена
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => void confirmPurchase()}
              className="btn-glass-blue inline-flex flex-1 items-center justify-center px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
            >
              {busy ? "Подключаем…" : "Подключить"}
            </button>
          </div>
        </div>
      </ModalShell>
    </div>
  );
}
