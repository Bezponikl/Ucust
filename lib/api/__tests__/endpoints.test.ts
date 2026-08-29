import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import path from "node:path";
import { endpoints, withQuery } from "@/lib/api/endpoints";

/**
 * Реестр путей сверяется с самим контрактом, а не с копией списка в тесте:
 * иначе расхождение фронта и бэка проходит незамеченным до первого 404.
 */
const CONTRACT = path.resolve(__dirname, "../../../docs/api/api-endpoints-public.json");

interface ContractEndpoint {
  method: string;
  path: string;
}

function readContract(): { basePath: string; endpoints: ContractEndpoint[] } {
  const raw = readFileSync(CONTRACT, "utf8");
  // Контракт приходит с висячими запятыми — JSON.parse их не прощает.
  const parsed = JSON.parse(raw.replace(/,(\s*[}\]])/g, "$1")) as {
    api: {
      basePath: string;
      services: Array<{
        controllers: Record<string, { endpoints: ContractEndpoint[] }>;
      }>;
    };
  };

  const list = parsed.api.services.flatMap((service) =>
    Object.values(service.controllers).flatMap((controller) => controller.endpoints),
  );
  return { basePath: parsed.api.basePath, endpoints: list };
}

/** `/projects/{id}` и `/projects/ID` приводятся к одному виду. */
function normalize(p: string): string {
  return p
    .split("?")[0]
    .split("/")
    .map((seg) => (/^\{.+\}$/.test(seg) || seg === "ID" ? ":p" : seg))
    .join("/");
}

/** Все пути реестра: константы как есть, функции — с подставленным «ID». */
function registryPaths(node: unknown): string[] {
  if (typeof node === "string") return [node];
  if (typeof node === "function") return [(node as (arg: string) => string)("ID")];
  if (node && typeof node === "object") {
    return Object.values(node).flatMap(registryPaths);
  }
  return [];
}

describe("реестр эндпоинтов", () => {
  const contract = readContract();
  const { oauth, ...apiGroups } = endpoints;
  const registry = new Set(registryPaths(apiGroups).map(normalize));

  it("контракт читается и не пустой", () => {
    expect(contract.basePath).toBe("/api/v0");
    expect(contract.endpoints.length).toBeGreaterThan(25);
  });

  it("покрывает каждый путь контракта", () => {
    const missing = contract.endpoints
      .map((e) => normalize(e.path.replace(contract.basePath, "")))
      .filter((p) => !registry.has(p));

    expect(missing).toEqual([]);
  });

  it("не выдумывает путей сверх контракта", () => {
    const known = new Set(
      contract.endpoints.map((e) => normalize(e.path.replace(contract.basePath, ""))),
    );
    const extra = [...registry].filter((p) => !known.has(p));

    expect(extra).toEqual([]);
  });

  it("знает адреса цепочки OAuth2", () => {
    expect(oauth.authorization("yandex")).toBe("/oauth2/authorization/yandex");
    expect(oauth.callback("yandex")).toBe("/login/oauth2/code/yandex");
  });

  it("подставляет параметры пути с экранированием", () => {
    expect(endpoints.projects.byId("a b/c")).toBe("/projects/a%20b%2Fc");
  });
});

describe("withQuery", () => {
  it("собирает параметры и экранирует значения", () => {
    expect(withQuery("/auth/confirm-email", { token: "a b&c" })).toBe(
      "/auth/confirm-email?token=a+b%26c",
    );
  });

  it("пропускает пустые значения", () => {
    expect(withQuery("/quota/me", { feature: undefined })).toBe("/quota/me");
    expect(withQuery("/quota/me", { feature: "" })).toBe("/quota/me");
  });

  it("сохраняет числа и флаги", () => {
    expect(withQuery("/posts", { page: 0, draft: false })).toBe("/posts?page=0&draft=false");
  });
});
