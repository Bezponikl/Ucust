import { describe, it, expect, vi, beforeEach } from "vitest";

describe("loadWorkspace", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it("берёт имя проекта из brandProfile, когда он заполнен", async () => {
    vi.doMock("@/lib/api/projects", () => ({
      listProjects: vi.fn(async () => [
        { id: "p1", name: "Имя в проекте", logoUrl: "http://localhost:8100/s3/a.png", brandProfile: JSON.stringify({ name: "Имя в профиле" }) },
      ]),
    }));
    const { loadWorkspace: load } = await import("@/lib/dashboard/source");

    const ws = await load();

    expect(ws.hasProject).toBe(true);
    expect(ws.projectId).toBe("p1");
    expect(ws.profile?.name).toBe("Имя в профиле");
    expect(ws.projectName).toBe("Имя в проекте");
    expect(ws.projectLogo).toBe("http://localhost:8100/s3/a.png");
    expect(ws.projects).toEqual([
      { id: "p1", name: "Имя в проекте", logo: "http://localhost:8100/s3/a.png" },
    ]);
  });

  it("не падает, когда brandProfile пустой, и отдаёт имя из проекта", async () => {
    vi.doMock("@/lib/api/projects", () => ({
      listProjects: vi.fn(async () => [
        { id: "p1", name: "EcoCoffee Roasters", brandProfile: null, logoUrl: null },
      ]),
    }));
    const { loadWorkspace: load } = await import("@/lib/dashboard/source");

    const ws = await load();

    expect(ws.hasProject).toBe(true);
    expect(ws.projectId).toBe("p1");
    expect(ws.profile).toBeNull();
    expect(ws.projectName).toBe("EcoCoffee Roasters");
    expect(ws.projectLogo).toBeNull();
  });

  it("отдаёт все проекты и выбирает первый, пока активный не задан", async () => {
    vi.doMock("@/lib/api/projects", () => ({
      listProjects: vi.fn(async () => [
        { id: "p1", name: "Кофейня", logoUrl: null, brandProfile: null },
        { id: "p2", name: "Барбершоп", logoUrl: null, brandProfile: null },
      ]),
    }));
    const { loadWorkspace: load } = await import("@/lib/dashboard/source");

    const ws = await load();

    expect(ws.projectId).toBe("p1");
    expect(ws.projectName).toBe("Кофейня");
    expect(ws.projects).toHaveLength(2);
    expect(ws.projects.map((p) => p.id)).toEqual(["p1", "p2"]);
  });

  it("выбирает запрошенный проект по id, а не первый", async () => {
    vi.doMock("@/lib/api/projects", () => ({
      listProjects: vi.fn(async () => [
        { id: "p1", name: "Кофейня", logoUrl: null, brandProfile: null },
        { id: "p2", name: "Барбершоп", logoUrl: null, brandProfile: null },
      ]),
    }));
    const { loadWorkspace: load } = await import("@/lib/dashboard/source");

    const ws = await load("p2");

    expect(ws.projectId).toBe("p2");
    expect(ws.projectName).toBe("Барбершоп");
  });

  it("возвращает пустое состояние, когда проектов нет", async () => {
    vi.doMock("@/lib/api/projects", () => ({
      listProjects: vi.fn(async () => []),
    }));
    const { loadWorkspace: load } = await import("@/lib/dashboard/source");

    const ws = await load();

    expect(ws).toEqual({
      hasProject: false,
      profile: null,
      projectId: null,
      projectName: null,
      projectLogo: null,
      projects: [],
    });
  });
});