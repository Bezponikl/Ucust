"use client";

import type { ReactNode } from "react";
import { useDashboard } from "./DashboardProvider";

/**
 * Единая «рамка» страницы дашборда — скруглённая карточка с бордером и тенью,
 * вписанная в отступы main (как у Входящих, но без их split-view/full-screen логики).
 * Заливка переключается в Оформлении: сплошная (по умолчанию) или «жидкое стекло».
 * На мобилке/планшете (<lg) ничего не меняет — контент как раньше, edge-to-edge.
 */
export default function PageWindow({ children }: { children: ReactNode }) {
  const { surfaceStyle } = useDashboard();
  const surfaceClass =
    surfaceStyle === "glass"
      ? "lg:bg-card/78 lg:dark:bg-card/55 lg:backdrop-blur-xl"
      : "lg:bg-card";

  return (
    <div
      className={`lg:min-h-[calc(100dvh-56px-44px)] lg:rounded-3xl lg:border lg:border-border lg:p-6 lg:shadow-soft ${surfaceClass}`}
    >
      {children}
    </div>
  );
}
