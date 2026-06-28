"use client";

import Image from "next/image";
import ModalShell from "./ModalShell";

const SOCIAL_LOGINS = [
  { label: "VK", cta: "Продолжить с VK", icon: "/vk.png" },
  { label: "Telegram", cta: "Продолжить в Telegram", icon: "/telegram.png" },
  { label: "MAX", cta: "Продолжить через MAX", icon: "/max.png" },
];

export default function LoginModal({
  open,
  onClose,
  onSwitchToSignup,
}: {
  open: boolean;
  onClose: () => void;
  onSwitchToSignup: () => void;
}) {
  return (
    <ModalShell open={open} onClose={onClose} labelledBy="login-modal-title">
      <h2 id="login-modal-title" className="text-2xl font-bold text-ink sm:text-[28px]">
        С возвращением
      </h2>
      <p className="mt-2 text-sm leading-relaxed text-ink-muted">
        Войдите в аккаунт, чтобы продолжить.
      </p>

      <form className="mt-6 flex flex-col gap-4" onSubmit={(e) => e.preventDefault()}>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Email</span>
          <input
            type="email"
            required
            placeholder="you@example.com"
            className="rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card"
          />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Пароль</span>
          <input
            type="password"
            required
            placeholder="••••••••"
            className="rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card"
          />
        </label>

        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center gap-2 text-ink-muted">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-border accent-brand"
            />
            Запомнить меня
          </label>
          <a
            href="#"
            className="font-medium text-brand transition-colors hover:text-brand-hover"
          >
            Забыли пароль?
          </a>
        </div>

        <button
          type="submit"
          className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
        >
          Войти
        </button>
      </form>

      <div className="my-5 flex items-center gap-3 text-xs uppercase tracking-wide text-ink-muted">
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
        или
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
      </div>

      <div className="flex flex-col gap-2.5">
        {SOCIAL_LOGINS.map((social) => (
          <button
            key={social.label}
            type="button"
            className="flex w-full items-center gap-3 rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm font-medium text-ink transition-all hover:border-brand/40 hover:bg-card dark:hover:bg-white/5"
          >
            <Image
              src={social.icon}
              alt=""
              width={22}
              height={22}
              className="h-5 w-5 shrink-0 object-contain"
              aria-hidden="true"
            />
            <span className="flex-1 text-center">{social.cta}</span>
            <span className="w-5" aria-hidden="true" />
          </button>
        ))}
      </div>

      <p className="mt-6 text-center text-sm text-ink-muted">
        Нет аккаунта?{" "}
        <button
          type="button"
          onClick={onSwitchToSignup}
          className="font-medium text-brand transition-colors hover:text-brand-hover"
        >
          Зарегистрироваться
        </button>
      </p>
    </ModalShell>
  );
}
