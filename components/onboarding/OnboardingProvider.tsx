"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import type { BrandProfile, WizardInput } from "@/lib/onboarding/types";
import { EMPTY_INPUT } from "@/lib/onboarding/types";
import { analyzeBusiness } from "@/lib/onboarding/mock";
import { clearOnboarding, loadOnboarding, saveOnboarding } from "@/lib/onboarding/storage";

interface Ctx {
  input: WizardInput;
  profile: BrandProfile | null;
  /** true после восстановления состояния из sessionStorage (см. редирект в ReviewFlow). */
  hydrated: boolean;
  updateInput: (patch: Partial<WizardInput>) => void;
  /** Редактирование готового бренд-профиля на экране ревью (персистится автоматически). */
  updateProfile: (patch: Partial<BrandProfile>) => void;
  runAnalysis: () => Promise<void>;
  resetAll: () => void;
}

const OnboardingContext = createContext<Ctx | null>(null);

export function OnboardingProvider({ children }: { children: ReactNode }) {
  const [input, setInput] = useState<WizardInput>(EMPTY_INPUT);
  const [profile, setProfile] = useState<BrandProfile | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Восстанавливаем состояние из sessionStorage после монтирования. setState здесь
  // намеренный: на сервере хранилище недоступно, а lazy-init дал бы рассинхрон гидрации.
  useEffect(() => {
    const saved = loadOnboarding();
    /* eslint-disable react-hooks/set-state-in-effect */
    if (saved) {
      setInput(saved.input);
      setProfile(saved.profile);
    }
    setHydrated(true);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  // Персистим при изменениях (только после гидрации, чтобы не затереть сохранённое).
  useEffect(() => {
    if (hydrated) saveOnboarding({ input, profile });
  }, [hydrated, input, profile]);

  const updateInput = useCallback((patch: Partial<WizardInput>) => {
    setInput((prev) => ({ ...prev, ...patch }));
  }, []);

  const updateProfile = useCallback((patch: Partial<BrandProfile>) => {
    setProfile((prev) => (prev ? { ...prev, ...patch } : prev));
  }, []);

  const runAnalysis = useCallback(async () => {
    const result = await analyzeBusiness(input);
    setProfile(result);
  }, [input]);

  const resetAll = useCallback(() => {
    setInput(EMPTY_INPUT);
    setProfile(null);
    clearOnboarding();
  }, []);

  return (
    <OnboardingContext.Provider value={{ input, profile, hydrated, updateInput, updateProfile, runAnalysis, resetAll }}>
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding(): Ctx {
  const ctx = useContext(OnboardingContext);
  if (!ctx) throw new Error("useOnboarding must be used within OnboardingProvider");
  return ctx;
}
