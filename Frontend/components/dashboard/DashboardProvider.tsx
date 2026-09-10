"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import type { DashboardData } from "@/lib/dashboard/types";
import { buildDashboardData } from "@/lib/dashboard/data";
import { loadWorkspace } from "@/lib/dashboard/source";

const BG_STORAGE_KEY = "uc_bg";
const SURFACE_STORAGE_KEY = "uc_surface";
const PROJECT_STORAGE_KEY = "uc_active_project";

export type SurfaceStyle = "solid" | "glass";

interface Ctx {
  data: DashboardData | null;
  hydrated: boolean;
  /** Есть ли созданный проект («мозг бренда» из онбординга). false — сразу после регистрации. */
  hasProject: boolean;
  /** id проекта на бэке — с ним работают разделы контента, генерации и настроек бизнеса. */
  projectId: string | null;
  /** Перечитать проект с сервера: после правок в настройках бизнеса. */
  reloadWorkspace: () => Promise<void>;
  /** Переключить активный проект (из селектора) — обновляет projectId и данные. */
  switchProject: (id: string) => Promise<void>;
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
  const [projectId, setProjectId] = useState<string | null>(null);
  const [mobileChromeHidden, setMobileChromeHidden] = useState(false);
  const [background, setBackgroundState] = useState<string | null>(null);
  // По умолчанию «жидкое стекло»: на сплошной заливке карточки сливались с фоном.
  const [surfaceStyle, setSurfaceStyleState] = useState<SurfaceStyle>("glass");
  // Актуальный id проекта: reloadWorkspace перечитывает то, что выбрано сейчас.
  const activeProjectId = useRef<string | null>(null);

  // Персист выбора в localStorage: после полной перезагрузки активным
  // становится последний выбранный проект, а не первый из списка.
  const rememberProject = useCallback((id: string | null) => {
    try {
      if (id) localStorage.setItem(PROJECT_STORAGE_KEY, id);
      else localStorage.removeItem(PROJECT_STORAGE_KEY);
    } catch {}
  }, []);

  const applyWorkspace = useCallback(
    async (targetId?: string) => {
      // Селектор может звать переключение, а reloadWorkspace — просто «перечитать текущее».
      const ws = await loadWorkspace(targetId ?? activeProjectId.current ?? undefined);
      activeProjectId.current = ws.projectId;
      rememberProject(ws.projectId);
      setData(buildDashboardData(ws.profile, ws.projectName, ws.projectLogo, ws.projects));
      setHasProject(ws.hasProject);
      setProjectId(ws.projectId);
    },
    [rememberProject],
  );

  // Профиль приходит с сервера либо из sessionStorage — решает loadWorkspace.
  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect */
    let savedProject: string | null = null;
    try {
      savedProject = localStorage.getItem(PROJECT_STORAGE_KEY);
    } catch {}
    void applyWorkspace(savedProject ?? undefined).then(() => setHydrated(true));
    try {
      const savedBg = localStorage.getItem(BG_STORAGE_KEY);
      if (savedBg) setBackgroundState(savedBg);
      const savedSurface = localStorage.getItem(SURFACE_STORAGE_KEY);
      if (savedSurface === "glass" || savedSurface === "solid") setSurfaceStyleState(savedSurface);
    } catch {}
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [applyWorkspace]);

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

  const switchProject = useCallback(
    async (id: string) => {
      await applyWorkspace(id);
    },
    [applyWorkspace],
  );

  return (
    <DashboardContext.Provider
      value={{
        data,
        hydrated,
        hasProject,
        projectId,
        reloadWorkspace: applyWorkspace,
        switchProject,
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
