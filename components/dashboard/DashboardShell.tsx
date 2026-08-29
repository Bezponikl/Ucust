import type { ReactNode } from "react";
import DashboardTopBar from "./DashboardTopBar";
import DashboardSidebar from "./DashboardSidebar";
import DashboardBottomNav from "./DashboardBottomNav";
import BackgroundLayer from "./BackgroundLayer";
import ProjectGuard from "./ProjectGuard";
import SetupTracker from "./SetupTracker";
import TourGuide from "./TourGuide";
import Toaster from "@/components/ui/Toaster";

export default function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-dvh overflow-hidden">
      <BackgroundLayer />
      {/* Сайдбар — только десктоп, мобиле — bottom nav */}
      <DashboardSidebar />

      {/* Правая колонка: тонкий топбар + прокручиваемый контент */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <DashboardTopBar />
        <main className="uc-scroll-fade flex-1 overflow-y-auto px-6 py-5 pb-24 sm:px-8 lg:pb-6">
          <div className="mx-auto w-full max-w-(--container-dash)">
            <ProjectGuard>{children}</ProjectGuard>
          </div>
        </main>
      </div>

      <DashboardBottomNav />
      <SetupTracker />
      <TourGuide />
      <Toaster />
    </div>
  );
}
