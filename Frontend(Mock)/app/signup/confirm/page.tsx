"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import Icon from "@/components/ui/Icon";
import { confirmEmail } from "@/lib/api/auth";
import { toMessage } from "@/lib/api/errors";
import { clearWorkspace } from "@/lib/onboarding/storage";

const AUTO_REDIRECT_SECONDS = 3;

/** checking — токен из письма проверяется сервером; done — аккаунт активирован. */
type Status = "checking" | "done" | "failed";

export default function ConfirmEmailPage() {
  const router = useRouter();
  // Ссылка из письма приходит с токеном. Без него страница просто подтверждает
  // пользователю, что шаг пройден: сам переход по ссылке уже случился.
  const [status, setStatus] = useState<Status>("checking");
  const [error, setError] = useState<string | null>(null);
  const [secondsLeft, setSecondsLeft] = useState(AUTO_REDIRECT_SECONDS);
  const redirected = useRef(false);

  const handleContinue = () => {
    if (redirected.current) return;
    redirected.current = true;
    // Новый аккаунт начинает с чистого листа: демо-проект из «Войти» живёт
    // в sessionStorage той же вкладки и иначе показал бы заполненный дашборд.
    clearWorkspace();
    try {
      sessionStorage.setItem("uc_show_setup", "1");
    } catch {}
    // Онбординг больше не открывается сразу: пользователь попадает на пустой
    // дашборд и заводит проект оттуда, когда осмотрится.
    router.push("/dashboard");
  };

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("token");
    if (!token) {
      setStatus("done"); // eslint-disable-line react-hooks/set-state-in-effect
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        await confirmEmail(token);
        if (!cancelled) setStatus("done");
      } catch (err) {
        if (cancelled) return;
        setError(toMessage(err));
        setStatus("failed");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (status !== "done") return;
    if (secondsLeft <= 0) {
      handleContinue();
      return;
    }
    const timeout = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, secondsLeft]);

  return (
    <AuthPageChrome>
      <div className="flex flex-col items-center text-center" aria-live="polite">
        {status === "checking" && (
          <>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-blue text-brand">
              <Icon name="mail" size={24} aria-hidden="true" />
            </div>
            <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[1.75rem]">
              Подтверждаем почту
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">
              Проверяем ссылку из письма — это займёт пару секунд.
            </p>
          </>
        )}

        {status === "done" && (
          <>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-blue text-brand">
              <Icon name="mail-check" size={24} aria-hidden="true" />
            </div>
            <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[1.75rem]">Почта подтверждена</h1>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">
              Регистрация завершена. Открываем кабинет через {secondsLeft} с — профиль проекта
              создадите оттуда, за пару минут.
            </p>
          </>
        )}

        {status === "failed" && (
          <>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-500/15 text-red-500">
              <Icon name="mail" size={24} aria-hidden="true" />
            </div>
            <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[1.75rem]">
              Ссылка не сработала
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">
              {error ?? "Не удалось подтвердить почту"}. Запросите новое письмо — старая ссылка
              могла устареть.
            </p>
          </>
        )}
      </div>

      {status === "done" && (
        <button
          type="button"
          onClick={handleContinue}
          className="btn-glass-blue mt-6 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
        >
          Продолжить сейчас
        </button>
      )}

      {status === "failed" && (
        <div className="mt-6 flex flex-col gap-3">
          <Link
            href="/signup/verify-email"
            className="btn-glass-blue inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
          >
            Запросить новое письмо
          </Link>
          <Link
            href="/login"
            className="inline-flex w-full items-center justify-center rounded-full border border-border px-6 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft"
          >
            Войти
          </Link>
        </div>
      )}
    </AuthPageChrome>
  );
}
