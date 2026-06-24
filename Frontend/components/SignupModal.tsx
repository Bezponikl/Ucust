"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import ModalShell from "./ModalShell";

type Step = "form" | "code";

export default function SignupModal({
  open,
  onClose,
  onSwitchToLogin,
}: {
  open: boolean;
  onClose: () => void;
  onSwitchToLogin: () => void;
}) {
  const [step, setStep] = useState<Step>("form");
  const [code, setCode] = useState<string[]>(Array(6).fill(""));
  const codeRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (!open) {
      const timeout = setTimeout(() => {
        setStep("form");
        setCode(Array(6).fill(""));
      }, 300);
      return () => clearTimeout(timeout);
    }
  }, [open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setStep("code");
  };

  const handleCodeChange = (index: number, value: string) => {
    const digit = value.replace(/\D/g, "").slice(-1);
    setCode((prev) => {
      const next = [...prev];
      next[index] = digit;
      return next;
    });
    if (digit && index < 5) {
      codeRefs.current[index + 1]?.focus();
    }
  };

  const handleCodeKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !code[index] && index > 0) {
      codeRefs.current[index - 1]?.focus();
    }
  };

  return (
    <ModalShell open={open} onClose={onClose} labelledBy="signup-modal-title">
      {step === "form" ? (
        <>
          <h2 id="signup-modal-title" className="text-2xl font-bold text-ink sm:text-3xl">
            Создать аккаунт
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-ink-muted">
            Первые посты будут готовы через 5 минут — без привязки карты.
          </p>

          <form className="mt-6 flex flex-col gap-4" onSubmit={handleSubmit}>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-1.5">
                <span className="text-sm font-medium text-ink">Имя</span>
                <input
                  type="text"
                  required
                  placeholder="Иван"
                  className="rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand"
                />
              </label>

              <label className="flex flex-col gap-1.5">
                <span className="text-sm font-medium text-ink">Фамилия</span>
                <input
                  type="text"
                  required
                  placeholder="Иванов"
                  className="rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand"
                />
              </label>
            </div>

            <label className="flex flex-col gap-1.5">
              <span className="text-sm font-medium text-ink">
                Отчество <span className="font-normal text-ink-muted">(не обязательно)</span>
              </span>
              <input
                type="text"
                placeholder="Иванович"
                className="rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand"
              />
            </label>

            <label className="flex flex-col gap-1.5">
              <span className="text-sm font-medium text-ink">Email</span>
              <input
                type="email"
                required
                placeholder="you@example.com"
                className="rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand"
              />
            </label>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-1.5">
                <span className="text-sm font-medium text-ink">Пароль</span>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand"
                />
              </label>

              <label className="flex flex-col gap-1.5">
                <span className="text-sm font-medium text-ink">Повторите пароль</span>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand"
                />
              </label>
            </div>

            <label className="flex items-start gap-2.5 text-sm text-ink-muted">
              <input
                type="checkbox"
                required
                className="mt-0.5 h-4 w-4 shrink-0 rounded border-border accent-brand"
              />
              <span>
                Я принимаю условия{" "}
                <Link href="/legal/offer" className="font-medium text-brand transition-colors hover:text-brand-hover">
                  Публичной оферты
                </Link>
                ,{" "}
                <Link href="/legal/privacy" className="font-medium text-brand transition-colors hover:text-brand-hover">
                  Политики конфиденциальности
                </Link>{" "}
                и{" "}
                <Link href="/legal/pdn-consent" className="font-medium text-brand transition-colors hover:text-brand-hover">
                  Согласия на обработку ПДн
                </Link>
              </span>
            </label>

            <button
              type="submit"
              className="mt-1 inline-flex items-center justify-center rounded-xl bg-brand px-6 py-3.5 text-sm font-medium text-white shadow-soft transition-all hover:-translate-y-0.5 hover:bg-brand-hover"
            >
              Зарегистрироваться
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-ink-muted">
            Уже есть аккаунт?{" "}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="font-medium text-brand transition-colors hover:text-brand-hover"
            >
              Войти
            </button>
          </p>
        </>
      ) : (
        <>
          <h2 id="signup-modal-title" className="text-2xl font-bold text-ink sm:text-3xl">
            Подтвердите email
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-ink-muted">
            Мы отправили шестизначный код на вашу почту. Введите его, чтобы
            завершить регистрацию.
          </p>

          <form
            className="mt-6 flex flex-col gap-5"
            onSubmit={(e) => e.preventDefault()}
          >
            <div className="flex items-center justify-between gap-2 sm:gap-3">
              {code.map((digit, i) => (
                <input
                  key={i}
                  ref={(el) => {
                    codeRefs.current[i] = el;
                  }}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleCodeChange(i, e.target.value)}
                  onKeyDown={(e) => handleCodeKeyDown(i, e)}
                  className="h-12 w-full max-w-12 rounded-xl border border-border bg-surface-soft text-center text-lg font-bold text-ink outline-none transition-colors focus:border-brand"
                />
              ))}
            </div>

            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-xl bg-brand px-6 py-3.5 text-sm font-medium text-white shadow-soft transition-all hover:-translate-y-0.5 hover:bg-brand-hover"
            >
              Подтвердить
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-ink-muted">
            Не пришёл код?{" "}
            <button
              type="button"
              className="font-medium text-brand transition-colors hover:text-brand-hover"
            >
              Отправить ещё раз
            </button>
          </p>

          <button
            type="button"
            onClick={() => setStep("form")}
            className="mt-2 w-full text-center text-sm text-ink-muted transition-colors hover:text-ink"
          >
            ← Изменить email
          </button>
        </>
      )}
    </ModalShell>
  );
}
