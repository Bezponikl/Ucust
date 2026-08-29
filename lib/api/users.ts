import { apiFetch } from "./client";
import { endpoints } from "./endpoints";
import type { ProfileResponse, UpdateProfileRequest } from "./types";

export function getMe(): Promise<ProfileResponse> {
  return apiFetch<ProfileResponse>(endpoints.user.me, { auth: true });
}

export function updateMe(req: UpdateProfileRequest): Promise<ProfileResponse> {
  return apiFetch<ProfileResponse>(endpoints.user.me, {
    method: "PATCH",
    auth: true,
    body: JSON.stringify(req),
  });
}

export async function uploadAvatar(file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  // Бэк отвечает ApiResponse<String>; обёртку уже развернул apiFetch.
  return apiFetch<string>(endpoints.user.avatar, {
    method: "POST",
    auth: true,
    body: form,
  });
}
