import type { Metadata } from "next";
import type { ReactNode } from "react";
import { OnboardingProvider } from "@/components/onboarding/OnboardingProvider";

export const metadata: Metadata = { robots: { index: false, follow: true } };

export default function OnboardingLayout({ children }: { children: ReactNode }) {
  return (
    <OnboardingProvider>
      <div className="min-h-dvh bg-canvas">{children}</div>
    </OnboardingProvider>
  );
}
