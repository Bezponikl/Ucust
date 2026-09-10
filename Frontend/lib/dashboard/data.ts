import type { BrandProfile } from "@/lib/onboarding/types";
import type { DashboardData, ProjectListItem } from "./types";

/**
 * Данные обзора из рабочей области. Метрики площадок, рекомендации и план недели
 * появятся, когда бэк начнёт отдавать реальные показатели, — сейчас собирается
 * только то, что честно приходит вместе с проектом (имя бренда).
 *
 * Проект мог быть создан старой версией фронта без brandProfile — тогда имя
 * берём из ProjectResponse.name, чтобы шапка и страницы не падали в «Создать проект».
 */
export function buildDashboardData(
  profile: BrandProfile | null,
  projectName: string | null,
  projectLogo: string | null,
  projects: ProjectListItem[],
): DashboardData {
  return {
    businessName: profile?.name?.trim() || projectName?.trim() || null,
    businessLogo: projectLogo || null,
    projects,
    stats: [],
    chart: { reach: [], engagement: [], clicks: [] },
    tips: [],
    week: [],
    activity: [],
  };
}