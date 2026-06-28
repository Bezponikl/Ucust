"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { DashboardData } from "@/lib/dashboard/types";
import { getDashboardData } from "@/lib/dashboard/mock";
import { loadOnboarding } from "@/lib/onboarding/storage";

interface Ctx {
  data: DashboardData | null;
  hydrated: boolean;
}

const DashboardContext = createContext<Ctx | null>(null);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Профиль доступен только в sessionStorage (клиент) — собираем данные после монтирования.
  useEffect(() => {
    const saved = loadOnboarding();
    /* eslint-disable react-hooks/set-state-in-effect */
    setData(getDashboardData(saved?.profile ?? null));
    setHydrated(true);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  return <DashboardContext.Provider value={{ data, hydrated }}>{children}</DashboardContext.Provider>;
}

export function useDashboard(): Ctx {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error("useDashboard must be used within DashboardProvider");
  return ctx;
}
