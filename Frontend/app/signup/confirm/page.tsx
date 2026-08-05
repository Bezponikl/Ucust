"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import Icon from "@/components/ui/Icon";
import { clearWorkspace } from "@/lib/onboarding/storage";

const AUTO_REDIRECT_SECONDS = 3;

export default function ConfirmEmailPage() {
  const router = useRouter();
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
    if (secondsLeft <= 0) {
      handleContinue();
      return;
    }
    const timeout = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [secondsLeft]);

  return (
    <AuthPageChrome>
      <div className="flex flex-col items-center text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-blue text-brand">
          <Icon name="mail-check" size={24} aria-hidden="true" />
        </div>

        <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[1.75rem]">Почта подтверждена</h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">
          Регистрация завершена. Открываем кабинет через {secondsLeft} с — профиль проекта
          создадите оттуда, за пару минут.
        </p>
      </div>

      <button
        type="button"
        onClick={handleContinue}
        className="btn-glass-blue mt-6 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
      >
        Продолжить сейчас
      </button>
    </AuthPageChrome>
  );
}
