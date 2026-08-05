"use client";

import ThemeToggle from "@/components/ThemeToggle";
import NotificationsPanel from "./NotificationsPanel";
import ProfileMenu from "./ProfileMenu";
import HelpButton from "./HelpButton";
import { useDashboard } from "./DashboardProvider";

export default function DashboardTopBar() {
  const { mobileChromeHidden, surfaceStyle } = useDashboard();
  return (
    <header className={`h-14 shrink-0 items-center justify-end px-6 sm:px-8 ${mobileChromeHidden ? "hidden lg:flex" : "flex"}`}>
      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle className="hidden sm:flex" glass={surfaceStyle === "glass"} />
        <HelpButton />
        <NotificationsPanel />
        <ProfileMenu />
      </div>
    </header>
  );
}
