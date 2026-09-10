import { describe, it, expect } from "vitest";
import { ApiError, parseErrorBody, toMessage } from "@/lib/api/errors";

describe("parseErrorBody", () => {
  it("достаёт код и текст из формата бэка {success, error:{code, message}}", () => {
    expect(
      parseErrorBody({
        success: false,
        error: { code: "USER_ALREADY_EXISTS", message: "A user with this email already exists" },
      }),
    ).toEqual({ code: "USER_ALREADY_EXISTS", message: "A user with this email already exists" });
  });

  it("понимает плоский формат {code, message}", () => {
    expect(parseErrorBody({ code: "VALIDATION_ERROR", message: "Passwords do not match" })).toEqual({
      code: "VALIDATION_ERROR",
      message: "Passwords do not match",
    });
  });

  it("не принимает служебный текст Spring за сообщение пользователю", () => {
    // Ответ шлюза при 500: {"status":500,"error":"Internal Server Error",...}
    expect(parseErrorBody({ status: 500, error: "Internal Server Error", path: "/api/v0/x" })).toEqual({
      code: undefined,
      message: "",
    });
  });

  it("переживает пустое тело", () => {
    expect(parseErrorBody(null)).toEqual({ code: undefined, message: "" });
  });
});

describe("toMessage", () => {
  it("переводит занятую почту", () => {
    expect(
      toMessage(new ApiError(409, "A user with this email already exists", "USER_ALREADY_EXISTS")),
    ).toBe("Аккаунт с такой почтой уже существует — попробуйте войти");
  });

  it("переводит несовпадение паролей", () => {
    expect(toMessage(new ApiError(400, "Passwords do not match", "VALIDATION_ERROR"))).toBe(
      "Пароли не совпадают",
    );
  });

  it("переводит требование к длине пароля", () => {
    expect(
      toMessage(new ApiError(400, "Password must be between 8 and 50 characters", "VALIDATION_ERROR")),
    ).toBe("Пароль — от 8 до 50 символов");
  });

  it("переводит требование кириллицы в фамилии", () => {
    expect(
      toMessage(
        new ApiError(400, "The surname must be in Cyrillic and may contain a hyphen.", "VALIDATION_ERROR"),
      ),
    ).toBe("Фамилия — кириллицей, можно с дефисом");
  });

  it("не показывает английский текст, если перевода нет", () => {
    expect(toMessage(new ApiError(400, "Some unmapped backend text", "VALIDATION_ERROR"))).toBe(
      "Проверьте правильность заполнения полей",
    );
  });

  it("объясняет протухшую ссылку из письма", () => {
    expect(toMessage(new ApiError(400, "", "LINK_EXPIRED"))).toBe(
      "Ссылка устарела — запросите новую",
    );
  });

  it("подставляет понятный текст для 401", () => {
    expect(toMessage(new ApiError(401, ""))).toBe("Неверная почта или пароль");
  });

  it("не показывает пользователю технические детали 500", () => {
    expect(toMessage(new ApiError(500, "NullPointerException at line 42"))).toBe(
      "Сервис временно недоступен, попробуйте позже",
    );
  });

  it("переживает не-ApiError", () => {
    expect(toMessage(new TypeError("fetch failed"))).toBe("Не удалось связаться с сервером");
  });
});
