import type { ReactNode } from "react";
import DashboardTopBar from "./DashboardTopBar";
import DashboardSidebar from "./DashboardSidebar";
import DashboardBottomNav from "./DashboardBottomNav";

export default function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-dvh bg-canvas">
      <DashboardTopBar />
      <div className="mx-auto flex w-full max-w-(--container-page)">
        <DashboardSidebar />
        {/* нижний отступ под bottom-nav на мобиле */}
        <main className="min-w-0 flex-1 px-4 py-6 pb-24 sm:px-6 lg:pb-10">{children}</main>
      </div>
      <DashboardBottomNav />
    </div>
  );
}
