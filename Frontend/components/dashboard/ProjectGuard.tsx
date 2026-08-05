"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useDashboard } from "./DashboardProvider";
import { requiresProject } from "./nav";

/**
 * До создания проекта разделы контента, входящих, акций и аналитики пустые —
 * держим пользователя на дашборде, даже если он пришёл по прямой ссылке.
 */
export default function ProjectGuard({ children }: { children: ReactNode }) {
  const { hasProject, hydrated } = useDashboard();
  const pathname = usePathname();
  const router = useRouter();

  const blocked = hydrated && !hasProject && requiresProject(pathname);

  useEffect(() => {
    if (blocked) router.replace("/dashboard");
  }, [blocked, router]);

  if (blocked) return null;
  return <>{children}</>;
}
