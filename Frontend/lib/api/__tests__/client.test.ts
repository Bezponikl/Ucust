import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiFetch, setAccessToken } from "@/lib/api/client";

const okJson = (body: unknown) =>
  new Response(JSON.stringify(body), {
    status: 200,
    headers: { "content-type": "application/json" },
  });

describe("apiFetch", () => {
  beforeEach(() => setAccessToken("expired"));

  it("на 401 обновляет токен и повторяет запрос", async () => {
    const calls: string[] = [];
    const fetchMock = vi.fn(async (url: string) => {
      calls.push(url);
      if (url.endsWith("/auth/refresh")) return okJson({ accessToken: "fresh", type: "Bearer" });
      return calls.filter((c) => c.endsWith("/user/me")).length === 1
        ? new Response("", { status: 401 })
        : okJson({ id: "1" });
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await apiFetch<{ id: string }>("/user/me", { auth: true });

    expect(result).toEqual({ id: "1" });
    expect(calls.filter((c) => c.endsWith("/auth/refresh"))).toHaveLength(1);
  });

  it("параллельные 401 обновляют токен одним запросом, а не тремя", async () => {
    const refreshCalls: string[] = [];
    let meCalls = 0;
    const fetchMock = vi.fn(async (url: string) => {
      if (url.endsWith("/auth/refresh")) {
        refreshCalls.push(url);
        await new Promise((r) => setTimeout(r, 10));
        return okJson({ accessToken: "fresh", type: "Bearer" });
      }
      meCalls += 1;
      return meCalls <= 3 ? new Response("", { status: 401 }) : okJson({ id: "1" });
    });
    vi.stubGlobal("fetch", fetchMock);

    await Promise.all([
      apiFetch("/user/me", { auth: true }),
      apiFetch("/user/me", { auth: true }),
      apiFetch("/user/me", { auth: true }),
    ]);

    expect(refreshCalls).toHaveLength(1);
  });

  it("бросает ApiError с текстом из тела ответа", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(JSON.stringify({ message: "Email занят", code: "EMAIL_TAKEN" }), {
            status: 400,
            headers: { "content-type": "application/json" },
          }),
      ),
    );

    await expect(apiFetch("/auth/register", { method: "POST" })).rejects.toMatchObject({
      status: 400,
      message: "Email занят",
      code: "EMAIL_TAKEN",
    });
  });

  it("не пытается обновить токен для запросов без auth", async () => {
    const calls: string[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        calls.push(url);
        return new Response("", { status: 401 });
      }),
    );

    await expect(apiFetch("/auth/login", { method: "POST" })).rejects.toMatchObject({ status: 401 });
    expect(calls.some((c) => c.endsWith("/auth/refresh"))).toBe(false);
  });

  it("разворачивает успешный ApiResponse в data", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(
            JSON.stringify({
              success: true,
              data: { id: "1", email: "a@b.c" },
              error: null,
              pagination: null,
            }),
            { status: 200, headers: { "content-type": "application/json" } },
          ),
      ),
    );

    const result = await apiFetch<{ id: string; email: string }>("/user/me", { auth: true });

    expect(result).toEqual({ id: "1", email: "a@b.c" });
  });

  it("не трогает строковые ответы (logo, /status/hello)", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => okJson("hello")));

    const result = await apiFetch<string>("/status/hello", { auth: true });

    expect(result).toBe("hello");
  });
});
