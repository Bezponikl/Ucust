import { describe, it, expect } from "vitest";
import { businessToProjectPatch, industryToLabel, labelToIndustry, projectToBusiness } from "@/lib/api/mapBusiness";
import { quotaView, subscriptionView, tariffView, formatDate } from "@/lib/api/mapBilling";
import { isTaskFailed, isTaskFinished, taskPostId, taskText, toDashboardPost } from "@/lib/api/mapGeneration";
import { EMPTY_BUSINESS } from "@/lib/dashboard/businesses";
import type { ProjectResponse } from "@/lib/api/types";

const project: ProjectResponse = {
  id: "p1",
  ownerId: "u1",
  logoUrl: "https://cdn/logo.png",
  name: "Кофейня",
  industry: "CAFE_RESTAURANT",
  city: "Москва",
  toneOfVoice: "FRIENDLY",
  description: "Кофе и выпечка",
  socialLinks: { website: "https://coffee.ru", instagram: "https://insta/coffee" },
  businessHours: { openTime: "08:00:00", closeTime: "20:00:00", offDays: ["SUNDAY"] },
};

describe("проект ↔ настройки бизнеса", () => {
  it("разворачивает проект в поля экрана", () => {
    const business = projectToBusiness(project);

    expect(business).toMatchObject({
      id: "p1",
      name: "Кофейня",
      category: "Кафе и рестораны",
      address: "Москва",
      site: "https://coffee.ru",
      workStart: "08:00",
      workEnd: "20:00",
      daysOff: [6],
    });
  });

  it("возвращает правки в формате контракта", () => {
    const patch = businessToProjectPatch(
      { ...projectToBusiness(project), name: "Новая кофейня", daysOff: [0, 6] },
      project,
    );

    expect(patch.name).toBe("Новая кофейня");
    expect(patch.industry).toBe("CAFE_RESTAURANT");
    expect(patch.businessHours?.offDays).toEqual(["MONDAY", "SUNDAY"]);
    // Поля, которых нет на экране, не теряются.
    expect(patch.socialLinks?.instagram).toBe("https://insta/coffee");
  });

  it("не отправляет пустой город: у бэка поле обязательное", () => {
    const patch = businessToProjectPatch({ ...EMPTY_BUSINESS, address: "" }, null);
    expect(patch.city).toBe("Не указан");
  });

  it("переводит отрасль в обе стороны", () => {
    expect(industryToLabel("FITNESS")).toBe("Фитнес и спорт");
    expect(labelToIndustry("Фитнес и спорт")).toBe("FITNESS");
    expect(labelToIndustry("Незнакомая сфера")).toBe("OTHER");
  });
});

describe("биллинг", () => {
  it("достаёт название и цену из разных имён полей", () => {
    expect(tariffView({ id: "t1", name: "Старт", price: 1500 })).toMatchObject({
      name: "Старт",
      price: 1500,
    });
    expect(tariffView({ id: "t2", title: "Бизнес", monthlyPrice: "3500" })).toMatchObject({
      name: "Бизнес",
      price: 3500,
    });
  });

  it("не выдумывает цену, если её нет", () => {
    expect(tariffView({ id: "t3" }).price).toBeNull();
  });

  it("считает остаток квоты, когда сервер прислал только лимит и расход", () => {
    expect(quotaView({ limit: 30, used: 12 })).toEqual({ limit: 30, used: 12, remaining: 18 });
    expect(quotaView({ limit: 30, remaining: 18 })).toEqual({ limit: 30, used: 12, remaining: 18 });
    expect(quotaView(null)).toEqual({ limit: null, used: null, remaining: null });
  });

  it("читает подписку и из плоского ответа, и из вложенного тарифа", () => {
    expect(subscriptionView({ tariffId: "t1", tariffName: "Бизнес" })).toMatchObject({
      tariffId: "t1",
      tariffName: "Бизнес",
    });
    expect(subscriptionView({ tariff: { id: "t2", name: "Старт" } })).toMatchObject({
      tariffId: "t2",
      tariffName: "Старт",
    });
  });

  it("приводит дату к человеческому виду, а мусор оставляет как есть", () => {
    expect(formatDate("2026-08-11T00:00:00Z")).toContain("2026");
    expect(formatDate("через месяц")).toBe("через месяц");
    expect(formatDate(null)).toBeNull();
  });
});

describe("генерация", () => {
  it("считает задачу готовой по статусу", () => {
    expect(isTaskFinished({ taskId: "1", status: "DONE" })).toBe(true);
    expect(isTaskFinished({ taskId: "1", status: "IN_PROGRESS" })).toBe(false);
  });

  it("считает задачу готовой, если текст уже пришёл", () => {
    expect(isTaskFinished({ taskId: "1", status: "PROCESSING", content: "Готовый пост" })).toBe(true);
  });

  it("ошибку с результатом ошибкой не считает", () => {
    expect(isTaskFailed({ taskId: "1", status: "FAILED" })).toBe(true);
    expect(isTaskFailed({ taskId: "1", status: "FAILED", text: "Пост" })).toBe(false);
  });

  it("достаёт текст и id поста из вложенных форм ответа", () => {
    expect(taskText({ taskId: "1", status: "DONE", post: { id: "x", text: "Текст" } })).toBe("Текст");
    expect(taskPostId({ taskId: "1", status: "DONE", posts: [{ id: "x", text: "Текст" }] })).toBe("x");
    expect(taskText({ taskId: "1", status: "DONE" })).toBeNull();
  });

  it("превращает пост бэка в карточку контент-плана", () => {
    const post = toDashboardPost({
      id: "post-1",
      content: "Первая строка\nвторая строка",
      status: "SCHEDULED",
      type: "VIDEO",
      channels: ["VK", "telegram", "myspace"],
      scheduledAt: "2026-08-14T09:30:00",
      imageUrl: "https://cdn/pic.jpg",
    });

    expect(post).toMatchObject({
      id: "post-1",
      title: "Первая строка",
      status: "scheduled",
      type: "video",
      channels: ["vk", "telegram"],
      day: 14,
      image: "https://cdn/pic.jpg",
    });
  });

  it("пост без даты и статуса не роняет календарь", () => {
    const post = toDashboardPost({ id: "post-2" });
    expect(post).toMatchObject({ day: 1, time: "—", status: "draft", channels: [] });
  });
});
