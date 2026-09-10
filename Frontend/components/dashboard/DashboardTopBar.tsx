"use client";

import ProfileMenu from "./ProfileMenu";
import ProjectSwitcher from "./ProjectSwitcher";
import { useDashboard } from "./DashboardProvider";

export default function DashboardTopBar() {
  const { mobileChromeHidden } = useDashboard();
  return (
    <header className={`z-30 h-14 shrink-0 items-center justify-end gap-3 border-b border-border/50 bg-card/70 px-4 backdrop-blur-xl dark:bg-card/55 sm:px-6 lg:px-8 ${mobileChromeHidden ? "hidden lg:flex" : "flex"}`}>
      {/* Селектор проекта живёт в сайдбаре (lg+), а на мобильных — здесь в шапке */}
      <div className="min-w-0 flex-1 lg:hidden">
        <ProjectSwitcher />
      </div>
      <div className="flex items-center gap-2 sm:gap-3">
        <ProfileMenu />
      </div>
    </header>
  );
}
