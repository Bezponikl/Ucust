"use client";

import { useDashboard } from "./DashboardProvider";

/** Полноэкранный фоновый слой позади сайдбара/топбара/контента (см. /dashboard/appearance). */
export default function BackgroundLayer() {
  const { background } = useDashboard();
  if (!background) return null;

  return (
    <div className="pointer-events-none fixed inset-0 -z-10" aria-hidden="true">
      <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${background})` }} />
      {/* Затемняющий scrim для читаемости текста поверх фото — сильнее в тёмной теме */}
      <div className="absolute inset-0 bg-white/25 dark:bg-black/45" />
    </div>
  );
}
