"use client";

import { useDashboard } from "./DashboardProvider";

/** Полноэкранный фоновый слой позади сайдбара/топбара/контента (см. /dashboard/appearance). */
export default function BackgroundLayer() {
  const { background } = useDashboard();

  // Без выбранного фото стеклу не во что «упереться»: карточки выглядят мутными,
  // а не стеклянными. Поэтому по умолчанию под ними лежит мягкий фирменный
  // градиент — он даёт стеклу что преломлять и не спорит с контентом.
  if (!background) {
    return (
      <div className="pointer-events-none fixed inset-0 -z-10 bg-canvas" aria-hidden="true">
        <div
          className="absolute inset-0 opacity-80 dark:opacity-50"
          style={{
            backgroundImage:
              "radial-gradient(60rem 40rem at 10% -12%, var(--color-brand-tint), transparent 62%)," +
              "radial-gradient(52rem 36rem at 98% 6%, var(--color-brand-tint), transparent 58%)," +
              "radial-gradient(46rem 34rem at 60% 110%, var(--color-brand-tint), transparent 60%)",
          }}
        />
      </div>
    );
  }

  return (
    <div className="pointer-events-none fixed inset-0 -z-10" aria-hidden="true">
      <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${background})` }} />
      {/* Затемняющий scrim для читаемости текста поверх фото — сильнее в тёмной теме */}
      <div className="absolute inset-0 bg-white/25 dark:bg-black/45" />
    </div>
  );
}
