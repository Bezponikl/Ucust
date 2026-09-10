import { apiFetch } from "./client";
import { endpoints } from "./endpoints";
import type { TariffResponse } from "./types";

/** Витрина тарифов. Эндпоинт публичный — токен не нужен, работает и на лендинге. */
export function listTariffs(): Promise<TariffResponse[]> {
  return apiFetch<TariffResponse[]>(endpoints.tariffs.root);
}

export function getTariff(id: string): Promise<TariffResponse> {
  return apiFetch<TariffResponse>(endpoints.tariffs.byId(id));
}
