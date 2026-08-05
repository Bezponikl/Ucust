"use client";

import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";

const inputClass =
  "rounded-full border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card";

export default function ForgotPasswordPage() {
  const router = useRouter();

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const email = new FormData(e.currentTarget).get("email");
    try {
      if (typeof email === "string") sessionStorage.setItem("uc_reset_email", email);
    } catch {}
    router.push("/forgot-password/check-email");
  };

  return (
    <AuthPageChrome>
      <div className="text-center">
        <h1 className="text-2xl font-bold text-ink sm:text-[1.75rem]">Восстановление пароля</h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">
          Укажите email — пришлём ссылку для сброса пароля.
        </p>
      </div>

      <form className="mt-7 flex flex-col gap-4" onSubmit={handleSubmit}>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Email</span>
          <input
            name="email"
            type="email"
            required
            autoFocus
            placeholder="you@example.com"
            className={inputClass}
          />
        </label>

        <button
          type="submit"
          className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
        >
          Отправить ссылку
        </button>

        <Link
          href="/login"
          className="inline-flex w-full items-center justify-center rounded-full border border-border px-6 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft"
        >
          ← Вернуться ко входу
        </Link>
      </form>
    </AuthPageChrome>
  );
}
