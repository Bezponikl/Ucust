import type { ReactNode } from "react";
import { OnboardingProvider } from "@/components/onboarding/OnboardingProvider";

export default function OnboardingLayout({ children }: { children: ReactNode }) {
  return (
    <OnboardingProvider>
      <div className="min-h-dvh bg-canvas">{children}</div>
    </OnboardingProvider>
  );
}
