import { describe, it, expect, vi, beforeEach } from "vitest";
import { setAccessToken } from "@/lib/api/client";
import { confirmEmail, changeEmailVerifyPassword } from "@/lib/api/auth";
import { whoAmI } from "@/lib/api/status";
import { deleteProject, getProject } from "@/lib/api/projects";
import { listTariffs } from "@/lib/api/tariffs";
import { getMyQuota, purchaseTariff } from "@/lib/api/quota";
import { generateAsync, pollTask, publishPost } from "@/lib/api/orchestration";
import { authorizeUrl } from "@/lib/api/oauth";

interface Call {
  url: string;
  method: string;
  auth: string | null;
  body: string | null;
}

let calls: Call[];

/** Мок сети: запоминает запрос и всегда отвечает одним и тем же телом. */
function stubFetch(body: unknown = {}) {
  calls = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init: RequestInit = {}) => {
      const headers = (init.headers ?? {}) as Record<string, string>;
      calls.push({
        url,
        method: init.method ?? "GET",
        auth: headers.Authorization ?? null,
        body: typeof init.body === "string" ? init.body : null,
      });
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }),
  );
}

describe("модули API бьют в адреса контракта", () => {
  beforeEach(() => setAccessToken("token"));

  it("подтверждение почты — GET с токеном в запросе", async () => {
    stubFetch();
    await confirmEmail("abc def");

    expect(calls[0].url).toBe("/api/v0/auth/confirm-email?token=abc+def");
    expect(calls[0].method).toBe("GET");
  });

  it("шаг 1 смены почты идёт под Bearer, остальные шаги — нет", async () => {
    stubFetch();
    await changeEmailVerifyPassword("secret");

    expect(calls[0].url).toBe("/api/v0/auth/change-email/verify-password");
    expect(calls[0].auth).toBe("Bearer token");
    expect(calls[0].body).toBe(JSON.stringify({ password: "secret" }));
  });

  it("кто я — данные шлюза по токену", async () => {
    stubFetch({ userId: "u1", roles: ["USER"], source: "gateway" });
    const me = await whoAmI();

    expect(calls[0].url).toBe("/api/v0/status/me");
    expect(me.roles).toEqual(["USER"]);
  });

  it("проект: чтение и удаление по одному адресу разными методами", async () => {
    stubFetch({ id: "p1" });
    await getProject("p1");
    await deleteProject("p1");

    expect(calls.map((c) => [c.method, c.url])).toEqual([
      ["GET", "/api/v0/projects/p1"],
      ["DELETE", "/api/v0/projects/p1"],
    ]);
  });

  it("тарифы публичные — уходят без Authorization", async () => {
    stubFetch([]);
    await listTariffs();

    expect(calls[0].url).toBe("/api/v0/tariffs");
    expect(calls[0].auth).toBeNull();
  });

  it("квота: фича попадает в параметры, без неё — чистый адрес", async () => {
    stubFetch();
    await getMyQuota("generation");
    await getMyQuota();

    expect(calls.map((c) => c.url)).toEqual([
      "/api/v0/quota/me?feature=generation",
      "/api/v0/quota/me",
    ]);
    expect(calls[0].auth).toBe("Bearer token");
  });

  it("покупка тарифа отправляет tariffId", async () => {
    stubFetch();
    await purchaseTariff("t1");

    expect(calls[0]).toMatchObject({
      url: "/api/v0/quota/me/purchase",
      method: "POST",
      body: JSON.stringify({ tariffId: "t1" }),
    });
  });

  it("генерация ставится в очередь и возвращает taskId", async () => {
    stubFetch({ taskId: "task-1" });
    const res = await generateAsync({ projectId: "p1", mode: "POST", count: 3 });

    expect(calls[0].url).toBe("/api/v0/orchestration/generate/async");
    expect(calls[0].method).toBe("POST");
    expect(res.taskId).toBe("task-1");
  });

  it("публикация поста — POST по адресу поста", async () => {
    stubFetch({ id: "post-1" });
    await publishPost("post-1");

    expect(calls[0].url).toBe("/api/v0/orchestration/posts/post-1/publish");
    expect(calls[0].method).toBe("POST");
  });

  it("опрос задачи прекращается, как только она готова", async () => {
    stubFetch({ taskId: "task-1", status: "DONE" });
    const task = await pollTask("task-1", {
      isDone: (t) => t.status === "DONE",
      intervalMs: 1,
    });

    expect(task.status).toBe("DONE");
    expect(calls).toHaveLength(1);
  });

  it("опрос сдаётся по таймауту, а не крутится вечно", async () => {
    stubFetch({ taskId: "task-1", status: "IN_PROGRESS" });

    await expect(
      pollTask("task-1", { isDone: () => false, intervalMs: 1, timeoutMs: 5 }),
    ).rejects.toThrow(/не завершилась/);
  });

  // Контракт перечисляет цепочку без префикса версии, но шлюз отвечает 302
  // только под ним — на `/oauth2/authorization/yandex` приходит 404.
  it("вход через Яндекс начинается под префиксом версии", () => {
    expect(authorizeUrl("yandex")).toBe("/api/v0/oauth2/authorization/yandex");
  });
});
