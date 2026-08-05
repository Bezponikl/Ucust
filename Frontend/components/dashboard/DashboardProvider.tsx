"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { DashboardData } from "@/lib/dashboard/types";
import { getDashboardData } from "@/lib/dashboard/mock";
import { loadOnboarding } from "@/lib/onboarding/storage";

const BG_STORAGE_KEY = "uc_bg";
const SURFACE_STORAGE_KEY = "uc_surface";

export type SurfaceStyle = "solid" | "glass";

interface Ctx {
  data: DashboardData | null;
  hydrated: boolean;
  /** Есть ли созданный проект («мозг бренда» из онбординга). false — сразу после регистрации. */
  hasProject: boolean;
  /** Скрывает топбар и мобильную нижнюю навигацию (полноэкранные страницы вроде открытого чата) */
  mobileChromeHidden: boolean;
  setMobileChromeHidden: (hidden: boolean) => void;
  /** CSS background-image значение (путь до пресета или data URL) — null = стандартный фон */
  background: string | null;
  setBackground: (v: string | null) => void;
  /** Заливка окон страниц: сплошная (по умолчанию) или полупрозрачное «жидкое стекло» */
  surfaceStyle: SurfaceStyle;
  setSurfaceStyle: (v: SurfaceStyle) => void;
}

const DashboardContext = createContext<Ctx | null>(null);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const [hasProject, setHasProject] = useState(false);
  const [mobileChromeHidden, setMobileChromeHidden] = useState(false);
  const [background, setBackgroundState] = useState<string | null>(null);
  const [surfaceStyle, setSurfaceStyleState] = useState<SurfaceStyle>("solid");

  // Профиль доступен только в sessionStorage (клиент) — собираем данные после монтирования.
  useEffect(() => {
    const saved = loadOnboarding();
    /* eslint-disable react-hooks/set-state-in-effect */
    setData(getDashboardData(saved?.profile ?? null));
    setHasProject(saved?.profile != null);
    setHydrated(true);
    try {
      const savedBg = localStorage.getItem(BG_STORAGE_KEY);
      if (savedBg) setBackgroundState(savedBg);
      const savedSurface = localStorage.getItem(SURFACE_STORAGE_KEY);
      if (savedSurface === "glass" || savedSurface === "solid") setSurfaceStyleState(savedSurface);
    } catch {}
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  const setBackground = (v: string | null) => {
    setBackgroundState(v);
    try {
      if (v) localStorage.setItem(BG_STORAGE_KEY, v);
      else localStorage.removeItem(BG_STORAGE_KEY);
    } catch {}
  };

  const setSurfaceStyle = (v: SurfaceStyle) => {
    setSurfaceStyleState(v);
    try {
      localStorage.setItem(SURFACE_STORAGE_KEY, v);
    } catch {}
  };

  return (
    <DashboardContext.Provider
      value={{
        data,
        hydrated,
        hasProject,
        mobileChromeHidden,
        setMobileChromeHidden,
        background,
        setBackground,
        surfaceStyle,
        setSurfaceStyle,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard(): Ctx {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error("useDashboard must be used within DashboardProvider");
  return ctx;
}
