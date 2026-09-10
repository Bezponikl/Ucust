import { listProjects } from "@/lib/api/projects";
import type { BrandProfile } from "@/lib/onboarding/types";

export interface WorkspaceSnapshot {
  hasProject: boolean;
  profile: BrandProfile | null;
  projectId: string | null;
}

/**
 * Единственный источник данных рабочей области. Вынесен отдельно, чтобы
 * DashboardProvider — файл, который активно правится в витрине — менялся минимально.
 */
export async function loadWorkspace(): Promise<WorkspaceSnapshot> {
  try {
    const projects = await listProjects();
    const first = projects[0];
    if (!first) return { hasProject: false, profile: null, projectId: null };

    let profile: BrandProfile | null = null;
    try {
      // brandProfile мог записать старый клиент — повреждённый JSON не должен
      // ронять весь дашборд, достаточно показать его без «мозга бренда».
      profile = first.brandProfile ? (JSON.parse(first.brandProfile) as BrandProfile) : null;
    } catch {
      profile = null;
    }

    return { hasProject: true, profile, projectId: first.id };
  } catch {
    // Сессия могла истечь или сервер недоступен — guard уведёт на вход,
    // а дашборд не должен падать в процессе.
    return { hasProject: false, profile: null, projectId: null };
  }
}
