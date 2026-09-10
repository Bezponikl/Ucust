import { listProjects } from "@/lib/api/projects";
import type { BrandProfile } from "@/lib/onboarding/types";

/** Проект в переключателе: имя и аватар показываются без чтения brandProfile каждого. */
export interface ProjectListItem {
  id: string;
  name: string;
  logo: string | null;
}

export interface WorkspaceSnapshot {
  hasProject: boolean;
  profile: BrandProfile | null;
  projectId: string | null;
  /** Имя из ProjectResponse.name — запасной вариант, когда brandProfile не заполнен. */
  projectName: string | null;
  /** Аватар проекта из ProjectResponse.logoUrl /s3/... — null для старых проектов. */
  projectLogo: string | null;
  /** Все проекты аккаунта — переключатель показывает их все. */
  projects: ProjectListItem[];
}

/**
 * Единственный источник данных рабочей области. Вынесен отдельно, чтобы
 * DashboardProvider — файл, который активно правится в витрине — менялся минимально.
 */
export async function loadWorkspace(projectId?: string): Promise<WorkspaceSnapshot> {
  try {
    const projects = await listProjects();
    const selected = projects.find((p) => p.id === projectId) ?? projects[0];
    if (!selected) {
      return {
        hasProject: false,
        profile: null,
        projectId: null,
        projectName: null,
        projectLogo: null,
        projects: [],
      };
    }

    let profile: BrandProfile | null = null;
    try {
      // brandProfile мог записать старый клиент — повреждённый JSON не должен
      // ронять весь дашборд, достаточно показать его без «мозга бренда».
      profile = selected.brandProfile ? (JSON.parse(selected.brandProfile) as BrandProfile) : null;
    } catch {
      profile = null;
    }

    return {
      hasProject: true,
      profile,
      projectId: selected.id,
      projectName: selected.name,
      projectLogo: selected.logoUrl,
      projects: projects.map((p) => ({ id: p.id, name: p.name, logo: p.logoUrl })),
    };
  } catch {
    // Сессия могла истечь или сервер недоступен — guard уведёт на вход,
    // а дашборд не должен падать в процессе.
    return {
      hasProject: false,
      profile: null,
      projectId: null,
      projectName: null,
      projectLogo: null,
      projects: [],
    };
  }
}