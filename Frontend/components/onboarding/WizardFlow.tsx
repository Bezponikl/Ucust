"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingTopBar from "./OnboardingTopBar";
import ProgressSteps from "./ProgressSteps";
import StepBusinessName from "./steps/StepBusinessName";
import StepAbout from "./steps/StepAbout";
import StepChannels from "./steps/StepChannels";
import { OnboardingBackdrop } from "./OnboardingChrome";
import Icon from "@/components/ui/Icon";
import { useOnboarding } from "./OnboardingProvider";

const LABELS = ["Название", "О бизнесе", "Соцсети"];

export default function WizardFlow() {
  const router = useRouter();
  const { input, runAnalysis } = useOnboarding();
  const [step, setStep] = useState(0);
  const [building, setBuilding] = useState(false);

  const buildProfile = async () => {
    setBuilding(true);
    try {
      await runAnalysis();
      router.push("/onboarding/review");
    } finally {
      setBuilding(false);
    }
  };

  const nextDisabled = step === 0 && input.name.trim().length === 0;

  return (
    <div className="uc-brand-canvas flex min-h-dvh flex-col">
      <OnboardingBackdrop />
      <OnboardingTopBar />
      <main className="relative z-10 mx-auto w-full max-w-2xl flex-1 px-5 py-10 sm:px-6 sm:py-14">
        <ProgressSteps current={step} labels={LABELS} />

        <div className="mt-10">
          <div className="rounded-[28px] border border-border bg-gradient-to-b from-brand/[0.09] to-card/85 p-6 shadow-soft ring-1 ring-inset ring-white/[0.04] backdrop-blur-xl sm:p-8">
            {step === 0 && <StepBusinessName />}
            {step === 1 && <StepAbout />}
            {step === 2 && <StepChannels />}
          </div>

          <div className="mt-6 flex items-center gap-3">
            {step > 0 && (
              <button
                type="button"
                onClick={() => setStep((s) => s - 1)}
                className="btn-glass inline-flex items-center justify-center gap-2 px-5 py-3.5 text-sm font-semibold"
              >
                <Icon name="arrow-left" size={16} aria-hidden="true" /> Назад
              </button>
            )}
            {step < 2 ? (
              <button
                type="button"
                disabled={nextDisabled}
                onClick={() => setStep((s) => s + 1)}
                className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
              >
                Дальше <Icon name="arrow-right" size={16} aria-hidden="true" />
              </button>
            ) : (
              <button
                type="button"
                onClick={buildProfile}
                disabled={building}
                className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
              >
                <Icon name="check-bold" size={16} aria-hidden="true" />
                {building ? "Готовим профиль…" : "Проверить профиль"}
              </button>
            )}
          </div>

          <p className="mt-4 text-center text-xs text-ink-muted">
            Всё можно поправить позже — профиль не высечен в камне
          </p>
        </div>
      </main>
    </div>
  );
}