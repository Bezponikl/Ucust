import { describe, it, expect } from "vitest";
import { normalizePhone, validateProfileFields } from "@/lib/api/profileFields";

describe("normalizePhone", () => {
  it("превращает привычный формат в тот, что ждёт бэк", () => {
    expect(normalizePhone("+7 900 000-00-00")).toBe("79000000000");
  });

  it("принимает восьмёрку вместо семёрки", () => {
    expect(normalizePhone("8 (900) 123-45-67")).toBe("79001234567");
  });

  it("пустое значение остаётся пустым — телефон необязателен", () => {
    expect(normalizePhone("")).toBe("");
  });

  it("не пытается чинить заведомо короткий номер", () => {
    expect(normalizePhone("12345")).toBe("12345");
  });
});

describe("validateProfileFields", () => {
  it("пропускает корректные данные", () => {
    expect(
      validateProfileFields({ firstName: "Анна", lastName: "Иванова", phone: "79000000000" }),
    ).toBeNull();
  });

  it("отвергает латиницу в имени — бэк требует кириллицу", () => {
    expect(validateProfileFields({ firstName: "Anna", lastName: "Иванова" })).toMatch(/кириллиц/i);
  });

  it("разрешает дефис в фамилии", () => {
    expect(
      validateProfileFields({ firstName: "Анна", lastName: "Петрова-Водкина" }),
    ).toBeNull();
  });

  it("отвергает телефон не в формате 79XXXXXXXXX", () => {
    expect(
      validateProfileFields({ firstName: "Анна", lastName: "Иванова", phone: "89001234567" }),
    ).toMatch(/79/);
  });

  it("пустой телефон допустим", () => {
    expect(validateProfileFields({ firstName: "Анна", lastName: "Иванова", phone: "" })).toBeNull();
  });
});
