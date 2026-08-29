import { describe, expect, it } from "vitest";
import { formatCompetitor, hostOf, normalizeUrl, parseCompetitor } from "../competitors";

describe("parseCompetitor", () => {
  it("разбирает строку парсера «Название (ссылка)»", () => {
    expect(parseCompetitor("SMMplanner (https://smmplanner.com)")).toEqual({
      name: "SMMplanner",
      url: "https://smmplanner.com",
      host: "smmplanner.com",
    });
  });

  it("оставляет название без ссылки как есть", () => {
    expect(parseCompetitor("Локальные агентства г. Москва")).toEqual({
      name: "Локальные агентства г. Москва",
      url: "",
      host: "",
    });
  });

  it("не теряет точки в названии и режет www в домене", () => {
    const c = parseCompetitor("Яндекс.Бизнес (https://www.business.yandex.ru/ads)");
    expect(c.name).toBe("Яндекс.Бизнес");
    expect(c.host).toBe("business.yandex.ru");
  });

  it("для голой ссылки подставляет домен вместо названия", () => {
    expect(parseCompetitor("https://tgstat.ru").name).toBe("tgstat.ru");
  });

  it("переживает пустую строку — карточка добавляется пустой", () => {
    expect(parseCompetitor("")).toEqual({ name: "", url: "", host: "" });
  });
});

describe("formatCompetitor", () => {
  it("собирает обратно тот же формат, что отдаёт парсер", () => {
    const raw = "LiveDune (https://livedune.ru)";
    expect(formatCompetitor(parseCompetitor(raw))).toBe(raw);
  });

  it("без ссылки пишет только название", () => {
    expect(formatCompetitor({ name: "Фрилансеры", url: "" })).toBe("Фрилансеры");
  });
});

describe("normalizeUrl", () => {
  it("дописывает https к домену из адресной строки", () => {
    expect(normalizeUrl("smmplanner.com")).toBe("https://smmplanner.com");
  });

  it("не трогает готовый адрес", () => {
    expect(normalizeUrl("http://example.com")).toBe("http://example.com");
  });
});

describe("hostOf", () => {
  it("возвращает домен без протокола даже для битого адреса", () => {
    expect(hostOf("www.example.com/path")).toBe("example.com");
  });
});
