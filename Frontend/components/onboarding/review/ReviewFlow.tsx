"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingTopBar from "../OnboardingTopBar";
import { OnboardingBackdrop } from "../OnboardingChrome";
import Icon from "@/components/ui/Icon";
import { useOnboarding } from "../OnboardingProvider";
import ProfileSidebar from "./ProfileSidebar";
import SectionAbout from "./SectionAbout";
import SectionMarket from "./SectionMarket";
import SectionSwot from "./SectionSwot";
import SectionServices from "./SectionServices";
import SectionGoals from "./SectionGoals";
import TourPrompt from "./TourPrompt";

export default function ReviewFlow() {
  const router = useRouter();
  const { profile, hydrated } = useOnboarding();
  const [section, setSection] = useState(0);
  const [askTour, setAskTour] = useState(false);

  // Редиректим только после гидрации из sessionStorage — иначе на прямой загрузке
  // /review профиль ещё null и нас бы выкинуло на визард до восстановления состояния.
  useEffect(() => {
    if (hydrated && profile === null) router.replace("/onboarding");
  }, [hydrated, profile, router]);

  if (!profile) return null;

  const sections = [
    <SectionAbout key="about" profile={profile} />,
    <SectionMarket key="market" profile={profile} />,
    <SectionSwot key="swot" profile={profile} />,
    <SectionServices key="services" profile={profile} />,
    <SectionGoals key="goals" profile={profile} />,
  ];

  return (
    <div className="uc-brand-canvas flex min-h-dvh flex-col">
      <OnboardingBackdrop />
      <OnboardingTopBar />
      <div className="relative z-10 mx-auto flex w-full max-w-(--container-page) flex-1 flex-col gap-8 px-4 py-8 sm:px-6 lg:flex-row lg:gap-12">
        <ProfileSidebar current={section} onSelect={setSection} />
        <main className="min-w-0 flex-1 pb-12">
          {sections[section]}

          <div className="mt-10 flex items-center gap-3">
            {section > 0 && (
              <button
                type="button"
                onClick={() => setSection((s) => s - 1)}
                className="btn-glass inline-flex items-center justify-center gap-2 px-5 py-3.5 text-sm font-semibold"
              >
                <Icon name="arrow-left" size={16} aria-hidden="true" /> Назад
              </button>
            )}
            {section < 4 ? (
              <button
                type="button"
                onClick={() => setSection((s) => s + 1)}
                className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold sm:flex-none sm:min-w-56"
              >
                Дальше <Icon name="arrow-right" size={16} aria-hidden="true" />
              </button>
            ) : (
              <button
                type="button"
                onClick={() => setAskTour(true)}
                className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold sm:flex-none sm:min-w-64"
              >
                <Icon name="check-bold" size={16} aria-hidden="true" /> Всё верно — в кабинет
              </button>
            )}
            <span className="ml-auto hidden text-xs text-ink-muted sm:block">
              Раздел {section + 1} из 5 · правки сохраняются сразу
            </span>
          </div>
        </main>
      </div>

      <TourPrompt open={askTour} onDone={() => router.push("/dashboard")} />
    </div>
  );
}
