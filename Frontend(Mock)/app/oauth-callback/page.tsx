"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import Icon from "@/components/ui/Icon";
import { loginWithYandexToken } from "@/lib/api/auth";
import { setAccessToken } from "@/lib/api/client";
import { parseOAuthCallback } from "@/lib/api/oauth";
import { useSession } from "@/lib/session/SessionProvider";

/**
 * Точка возврата после входа через соцсеть. Бэк присылает access-токен строкой
 * запроса — так устроен redirect-флоу, поэтому первым же действием вычищаем его
 * из адреса, чтобы он не осел в истории браузера.
 *
 * Мобильная обёртка приложения сюда же приводит другой дорогой: нативный вход
 * Яндекса отдаёт токен провайдера, и его меняют на свой через `yandex-mobile`.
 * Отличает случаи параметр `yandexToken`.
 */
export default function OAuthCallbackPage() {
  const router = useRouter();
  const { reload } = useSession();
  const [failed, setFailed] = useState(false);
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    const search = window.location.search;
    const providerToken = new URLSearchParams(search).get("yandexToken");
    const { token, error } = parseOAuthCallback(search);
    window.history.replaceState(null, "", "/oauth-callback");

    const openDashboard = () =>
      reload().then(
        () => router.replace("/dashboard"),
        () => setFailed(true),
      );

    if (providerToken) {
      void loginWithYandexToken(providerToken).then(openDashboard, () =>
        router.replace("/login?error=oauth_failed"),
      );
      return;
    }

    if (error || !token) {
      router.replace(`/login?error=${error ?? "oauth_failed"}`);
      return;
    }

    setAccessToken(token);
    void openDashboard();
  }, [reload, router]);

  return (
    <AuthPageChrome>
      <div className="flex flex-col items-center text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-blue text-brand">
          <Icon name={failed ? "shield" : "check-bold"} size={24} aria-hidden="true" />
        </div>
        <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[1.75rem]">
          {failed ? "Что-то пошло не так" : "Входим…"}
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">
          {failed
            ? "Не удалось загрузить профиль. Попробуйте войти ещё раз."
            : "Проверяем данные из Яндекса и открываем кабинет."}
        </p>
      </div>

      {failed && (
        <button
          type="button"
          onClick={() => router.replace("/login")}
          className="btn-glass-blue mt-6 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
        >
          Вернуться ко входу
        </button>
      )}
    </AuthPageChrome>
  );
}
