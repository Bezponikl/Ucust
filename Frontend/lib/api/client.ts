/**
 * Core API Client for UCust Frontend
 * Manages communication with Java Backend & AI Gateway.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080/api/v1";

export const AI_GATEWAY_URL =
  process.env.NEXT_PUBLIC_AI_URL ||
  (process.env.NEXT_PUBLIC_AI_GATEWAY_URL ? process.env.NEXT_PUBLIC_AI_GATEWAY_URL.replace(/\/api\/v1\/?$/, "") : "") ||
  "";

export const AI_WS_URL =
  process.env.NEXT_PUBLIC_AI_WS_URL || "ws://localhost:8000";

export interface ApiRequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

export async function apiClient<T>(
  endpoint: string,
  options: ApiRequestOptions = {},
  baseUrl: string = API_BASE_URL
): Promise<T> {
  const { params, headers, ...customConfig } = options;

  const cleanEndpoint = endpoint.replace(/^\/+/, "");
  let url = baseUrl ? `${baseUrl.replace(/\/+$/, "")}/${cleanEndpoint}` : `/${cleanEndpoint}`;

  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  // Get auth token if available (client-side)
  let authToken: string | null = null;
  if (typeof window !== "undefined") {
    try {
      authToken = localStorage.getItem("uc_auth_token") || sessionStorage.getItem("uc_auth_token");
    } catch {}
  }

  const defaultHeaders: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (authToken) {
    defaultHeaders["Authorization"] = `Bearer ${authToken}`;
  }

  const config: RequestInit = {
    method: customConfig.method || "GET",
    headers: {
      ...defaultHeaders,
      ...headers,
    },
    ...customConfig,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errData = await response.json();
      errorDetail = errData.message || errData.detail || JSON.stringify(errData);
    } catch {}
    throw new Error(`API Error [${response.status}]: ${errorDetail}`);
  }

  return (await response.json()) as T;
}
