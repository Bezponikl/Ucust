"use client";

import ComingSoon from "@/components/dashboard/ComingSoon";

export default function AnalyticsView() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Аналитика</h1>
        <p className="mt-0.5 text-sm text-ink-muted">Как растёт ваш бизнес в соцсетях</p>
      </div>

      <ComingSoon
        icon="trending"
        title="Аналитика скоро появится"
        text="Как только площадки начнут отдавать метрики, здесь будут охваты, реакции, подписчики и разбор публикаций — по периодам и каналам. Пока без выдуманных цифр."
      />
    </div>
  );
}