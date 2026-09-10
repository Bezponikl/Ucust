import { apiFetch } from "./client";
import { endpoints } from "./endpoints";
import type { ProjectRequest, ProjectResponse } from "./types";

export function listProjects(): Promise<ProjectResponse[]> {
  return apiFetch<ProjectResponse[]>(endpoints.projects.root, { auth: true });
}

export function getProject(id: string): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(endpoints.projects.byId(id), { auth: true });
}

export function createProject(req: ProjectRequest): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(endpoints.projects.root, {
    method: "POST",
    auth: true,
    body: JSON.stringify(req),
  });
}

export function updateProject(
  id: string,
  req: Partial<ProjectRequest>,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(endpoints.projects.byId(id), {
    method: "PATCH",
    auth: true,
    body: JSON.stringify(req),
  });
}

export function deleteProject(id: string): Promise<void> {
  return apiFetch<void>(endpoints.projects.byId(id), { method: "DELETE", auth: true });
}

export function uploadLogo(id: string, file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  return apiFetch<string>(endpoints.projects.logo(id), { method: "POST", auth: true, body: form });
}
