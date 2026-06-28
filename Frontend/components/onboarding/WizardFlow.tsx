"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingTopBar from "./OnboardingTopBar";
import ProgressSteps from "./ProgressSteps";
import StepBusinessName from "./steps/StepBusinessName";
import StepAbout from "./steps/StepAbout";
import StepChannels from "./steps/StepChannels";
import AnalysisScreen from "./AnalysisScreen";
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
    <div className="flex min-h-dvh flex-col">
      <OnboardingTopBar />
      <main className="mx-auto w-full max-w-2xl flex-1 px-5 py-10 sm:px-6 sm:py-14">
        <ProgressSteps current={analyzing ? 3 : step} labels={LABELS} />
        <div className="mt-12">
          {analyzing ? (
            <AnalysisScreen onDone={() => router.push("/onboarding/review")} />
          ) : (
            <>
              {step === 0 && <StepBusinessName />}
              {step === 1 && <StepAbout />}
              {step === 2 && <StepChannels />}
              <div className="mt-10 flex gap-3">
                {step > 0 && (
                  <button
                    type="button"
                    onClick={() => setStep((s) => s - 1)}
                    className="btn-glass inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
                  >
                    Назад
                  </button>
                )}
                {step < 2 ? (
                  <button
                    type="button"
                    disabled={nextDisabled}
                    onClick={() => setStep((s) => s + 1)}
                    className="btn-glass-blue inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Далее
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={startAnalysis}
                    className="btn-glass-blue inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
                  >
                    Начать анализ
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
