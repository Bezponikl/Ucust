"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingTopBar from "./OnboardingTopBar";
import ProgressSteps from "./ProgressSteps";
import StepBusinessName from "./steps/StepBusinessName";
import StepAbout from "./steps/StepAbout";
import StepChannels from "./steps/StepChannels";
import AnalysisScreen from "./AnalysisScreen";
import { OnboardingBackdrop } from "./OnboardingChrome";
import Icon from "@/components/ui/Icon";
import { useOnboarding } from "./OnboardingProvider";

const LABELS = ["Название", "О бизнесе", "Соцсети", "Анализ"];

export default function WizardFlow() {
  const router = useRouter();
  const { input, runAnalysis } = useOnboarding();
  const [step, setStep] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);

  const startAnalysis = () => {
    setAnalyzing(true);
    void runAnalysis();
  };

  const nextDisabled = step === 0 && input.name.trim().length === 0;

  return (
    <div className="uc-brand-canvas flex min-h-dvh flex-col">
      <OnboardingBackdrop />
      <OnboardingTopBar />
      <main className="relative z-10 mx-auto w-full max-w-2xl flex-1 px-5 py-10 sm:px-6 sm:py-14">
        <ProgressSteps current={analyzing ? 3 : step} labels={LABELS} />

        <div className="mt-10">
          {analyzing ? (
            <AnalysisScreen onDone={() => router.push("/onboarding/review")} />
          ) : (
            <>
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
                    onClick={startAnalysis}
                    className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold"
                  >
                    <Icon name="sparkles" size={16} aria-hidden="true" /> Собрать профиль
                  </button>
                )}
              </div>

              <p className="mt-4 text-center text-xs text-ink-muted">
                Всё можно поправить позже — профиль не высечен в камне
              </p>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
