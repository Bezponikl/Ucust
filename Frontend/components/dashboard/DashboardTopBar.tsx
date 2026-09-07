"use client";

import NotificationsPanel from "./NotificationsPanel";
import ProfileMenu from "./ProfileMenu";
import { useDashboard } from "./DashboardProvider";

export default function DashboardTopBar() {
  const { mobileChromeHidden } = useDashboard();
  return (
    <header className={`z-30 h-14 shrink-0 items-center justify-end border-b border-border/50 bg-card/70 px-6 backdrop-blur-xl dark:bg-card/55 sm:px-8 ${mobileChromeHidden ? "hidden lg:flex" : "flex"}`}>
      <div className="flex items-center gap-2 sm:gap-3">
        <NotificationsPanel />
        <ProfileMenu />
      </div>
    </header>
  );
}
