"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingTopBar from "../OnboardingTopBar";
import { useOnboarding } from "../OnboardingProvider";
import ProfileSidebar from "./ProfileSidebar";
import SectionAbout from "./SectionAbout";
import SectionMarket from "./SectionMarket";
import SectionSwot from "./SectionSwot";
import SectionServices from "./SectionServices";
import SectionGoals from "./SectionGoals";

export default function ReviewFlow() {
  const router = useRouter();
  const { profile, hydrated } = useOnboarding();
  const [section, setSection] = useState(0);

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
    <div className="flex min-h-dvh flex-col">
      <OnboardingTopBar />
      <div className="mx-auto flex w-full max-w-(--container-page) flex-1 flex-col gap-6 px-4 py-6 sm:px-6 lg:flex-row lg:gap-10">
        <ProfileSidebar current={section} onSelect={setSection} />
        <main className="min-w-0 flex-1 pb-10 lg:pt-6">
          {sections[section]}
          <div className="mt-10 flex gap-3">
            {section > 0 && (
              <button
                type="button"
                onClick={() => setSection((s) => s - 1)}
                className="btn-glass inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
              >
                Назад
              </button>
            )}
            {section < 4 ? (
              <button
                type="button"
                onClick={() => setSection((s) => s + 1)}
                className="btn-glass-blue inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
              >
                Далее
              </button>
            ) : (
              <button
                type="button"
                onClick={() => router.push("/dashboard")}
                className="btn-glass-blue inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
              >
                Готово — перейти в дашборд
              </button>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
