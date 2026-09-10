"use client";

import { useState } from "react";
import ModalShell from "@/components/ModalShell";
import Icon from "@/components/ui/Icon";
import {
  changeEmailConfirm,
  changeEmailSetNewEmail,
  changeEmailVerifyPassword,
} from "@/lib/api/auth";
import { toMessage } from "@/lib/api/errors";

/**
 * Смена почты идёт тремя шагами бэка: пароль подтверждает владельца, затем
 * на новый адрес уходит код, и он же закрывает смену. Токен связывает шаги —
 * бэк отдаёт его либо ответом на первый шаг, либо письмом, поэтому предусмотрены
 * оба случая.
 */
type Step = "password" | "email" | "code" | "done";

const inputCls =
  "w-full rounded-full border border-border bg-surface-soft/70 px-4 py-2.5 text-sm text-ink outline-none transition focus:border-brand focus:ring-1 focus:ring-brand/25";

const STEP_TITLE: Record<Step, string> = {
  password: "Подтвердите пароль",
  email: "Новый адрес почты",
  code: "Код из письма",
  done: "Почта изменена",
};

export default function ChangeEmailModal({
  open,
  currentEmail,
  onClose,
  onChanged,
}: {
  open: boolean;
  currentEmail: string;
  onClose: () => void;
  /** Смена прошла — профиль пора перечитать. */
  onChanged: () => void;
}) {
  const [step, setStep] = useState<Step>("password");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  /** true — токен пришёл ответом сервера, поле для него показывать не нужно. */
  const [tokenFromServer, setTokenFromServer] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [code, setCode] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reset = () => {
    setStep("password");
    setPassword("");
    setToken("");
    setTokenFromServer(false);
    setNewEmail("");
    setCode("");
    setError(null);
    setPending(false);
  };

  const close = () => {
    reset();
    onClose();
  };

  const run = async (action: () => Promise<void>) => {
    setPending(true);
    setError(null);
    try {
      await action();
    } catch (err) {
      setError(toMessage(err));
    } finally {
      setPending(false);
    }
  };

  const submitPassword = () =>
    run(async () => {
      const issued = await changeEmailVerifyPassword(password);
      if (issued) {
        setToken(issued);
        setTokenFromServer(true);
      }
      setStep("email");
    });

  const submitEmail = () =>
    run(async () => {
      await changeEmailSetNewEmail({ token, newEmail });
      setStep("code");
    });

  const submitCode = () =>
    run(async () => {
      await changeEmailConfirm({ token, code });
      setStep("done");
      onChanged();
    });

  const stepNumber = step === "password" ? 1 : step === "email" ? 2 : 3;

  return (
    <ModalShell open={open} onClose={close} labelledBy="change-email-title">
      <div className="flex flex-col">
        <span className="text-xs font-semibold uppercase tracking-wide text-ink-muted">
          {step === "done" ? "Готово" : `Шаг ${stepNumber} из 3`}
        </span>
        <h2 id="change-email-title" className="mt-1 text-lg font-bold text-ink">
          {STEP_TITLE[step]}
        </h2>

        {step === "password" && (
          <>
            <p className="mt-1.5 text-sm text-ink-muted">
              Сейчас почта — {currentEmail || "не указана"}. Введите пароль, чтобы продолжить.
            </p>
            <label className="mt-4 block">
              <span className="mb-1.5 block text-sm font-semibold text-ink">Пароль</span>
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={inputCls}
              />
            </label>
          </>
        )}

        {step === "email" && (
          <>
            <p className="mt-1.5 text-sm text-ink-muted">
              Отправим на новый адрес код подтверждения.
            </p>
            <label className="mt-4 block">
              <span className="mb-1.5 block text-sm font-semibold text-ink">Новая почта</span>
              <input
                type="email"
                autoComplete="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="you@example.com"
                className={inputCls}
              />
            </label>
            {!tokenFromServer && (
              <label className="mt-3 block">
                <span className="mb-1.5 block text-sm font-semibold text-ink">
                  Токен из письма
                </span>
                <input
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="Вставьте токен из письма на текущую почту"
                  className={inputCls}
                />
              </label>
            )}
          </>
        )}

        {step === "code" && (
          <>
            <p className="mt-1.5 text-sm text-ink-muted">
              Код отправлен на {newEmail}. Введите его — и почта сменится.
            </p>
            <label className="mt-4 block">
              <span className="mb-1.5 block text-sm font-semibold text-ink">Код</span>
              <input
                inputMode="numeric"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className={inputCls}
              />
            </label>
          </>
        )}

        {step === "done" && (
          <div className="mt-4 flex items-center gap-3 rounded-2xl border border-border bg-surface-soft px-4 py-3">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-success/15 text-success">
              <Icon name="check" size={18} aria-hidden="true" />
            </span>
            <p className="text-sm text-ink">
              Новый адрес — {newEmail}. Входить теперь нужно с ним.
            </p>
          </div>
        )}

        {error && (
          <p role="alert" className="mt-3 text-sm text-red-500">
            {error}
          </p>
        )}

        <div className="mt-6 flex gap-3">
          {step === "done" ? (
            <button
              type="button"
              onClick={close}
              className="btn-glass-blue inline-flex flex-1 items-center justify-center px-5 py-3 text-sm font-semibold"
            >
              Готово
            </button>
          ) : (
            <>
              <button
                type="button"
                onClick={close}
                className="inline-flex flex-1 items-center justify-center rounded-full border border-border px-5 py-3 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft"
              >
                Отмена
              </button>
              <button
                type="button"
                disabled={
                  pending ||
                  (step === "password" && !password) ||
                  (step === "email" && (!newEmail || !token)) ||
                  (step === "code" && !code)
                }
                onClick={
                  step === "password" ? submitPassword : step === "email" ? submitEmail : submitCode
                }
                className="btn-glass-blue inline-flex flex-1 items-center justify-center px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
              >
                {pending ? "Отправляем…" : step === "code" ? "Подтвердить" : "Далее"}
              </button>
            </>
          )}
        </div>
      </div>
    </ModalShell>
  );
}
