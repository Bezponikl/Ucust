import { describe, it, expect } from "vitest";
import { parseOAuthCallback, oauthErrorMessage, parseLinkSocialHint } from "@/lib/api/oauth";

describe("parseOAuthCallback", () => {
  it("достаёт токен из адреса возврата", () => {
    expect(parseOAuthCallback("?token=abc.def.ghi")).toEqual({ token: "abc.def.ghi", error: null });
  });

  it("достаёт код ошибки", () => {
    expect(parseOAuthCallback("?error=email_not_found")).toEqual({
      token: null,
      error: "email_not_found",
    });
  });

  it("пустой запрос — ни токена, ни ошибки", () => {
    expect(parseOAuthCallback("")).toEqual({ token: null, error: null });
  });

  it("не путает чужие параметры с токеном", () => {
    expect(parseOAuthCallback("?code=xyz&state=1")).toEqual({ token: null, error: null });
  });
});

describe("parseLinkSocialHint", () => {
  it("собирает данные провайдера для привязки к парольному аккаунту", () => {
    const search =
      "?error=email_exists_link_required&email=ivan%40example.com&provider=YANDEX&providerUserId=42";
    expect(parseLinkSocialHint(search)).toEqual({
      email: "ivan@example.com",
      provider: "YANDEX",
      providerUserId: "42",
    });
  });

  it("другая ошибка — не наш случай", () => {
    expect(parseLinkSocialHint("?error=email_not_found")).toBeNull();
  });

  it("без данных провайдера привязывать нечего", () => {
    expect(parseLinkSocialHint("?error=email_exists_link_required&email=ivan%40example.com")).toBeNull();
  });

  it("успешный вход подсказки не даёт", () => {
    expect(parseLinkSocialHint("?token=abc.def.ghi")).toBeNull();
  });
});

describe("oauthErrorMessage", () => {
  it("объясняет столкновение с парольным аккаунтом", () => {
    expect(oauthErrorMessage("email_exists_link_required")).toBe(
      "На эту почту уже есть аккаунт с паролем — войдите по паролю, и соцсеть привяжется к нему",
    );
  });

  it("объясняет отсутствие почты у провайдера", () => {
    expect(oauthErrorMessage("email_not_found")).toBe(
      "Соцсеть не поделилась адресом почты — разрешите доступ или войдите по паролю",
    );
  });

  it("даёт нейтральный текст при сбое", () => {
    expect(oauthErrorMessage("oauth_failed")).toBe(
      "Не удалось войти через соцсеть — попробуйте ещё раз",
    );
  });

  it("незнакомый код тоже не оставляет пользователя без объяснения", () => {
    expect(oauthErrorMessage("something_new")).toBe(
      "Не удалось войти через соцсеть — попробуйте ещё раз",
    );
  });

  it("без ошибки ничего не показываем", () => {
    expect(oauthErrorMessage(null)).toBeNull();
  });
});
