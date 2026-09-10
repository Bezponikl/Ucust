import { apiFetch } from "./client";
import { endpoints } from "./endpoints";
import type { CheckQuotaResponse, SubscriptionOverview } from "./types";

/** Остаток по одной фиче. По умолчанию бэк считает `generation`. */
export function getMyQuota(feature?: string): Promise<CheckQuotaResponse> {
  return apiFetch<CheckQuotaResponse>(endpoints.quota.me(feature), { auth: true });
}

/**
 * Свой тариф вместе с квотами по всем фичам. Бэк отвечает 404, когда подписки
 * нет вовсе, — это не сбой, а «пользователь ещё не покупал тариф».
 */
export function getMySubscription(): Promise<SubscriptionOverview> {
  return apiFetch<SubscriptionOverview>(endpoints.quota.myTariff, { auth: true });
}

/** Покупка тарифа. На бэке пока заглушка: платёж не проводится, подписка выдаётся. */
export function purchaseTariff(tariffId: string): Promise<SubscriptionOverview> {
  return apiFetch<SubscriptionOverview>(endpoints.quota.purchase, {
    method: "POST",
    auth: true,
    body: JSON.stringify({ tariffId }),
  });
}
