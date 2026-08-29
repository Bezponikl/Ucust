"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import FormError from "@/components/auth/FormError";
import Checkbox from "@/components/ui/Checkbox";
import PasswordInput from "@/components/ui/PasswordInput";
import { register } from "@/lib/api/auth";
import { toMessage } from "@/lib/api/errors";

const inputClass =
  "rounded-full border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card";

export default function SignupPage() {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    const email = String(data.get("email") ?? "");
    try {
      sessionStorage.setItem("uc_signup_email", email);
    } catch {}

    setPending(true);
    setError(null);
    try {
      await register({
        firstName: String(data.get("firstName") ?? ""),
        lastName: String(data.get("lastName") ?? ""),
        email,
        password: String(data.get("password") ?? ""),
        confirmPassword: String(data.get("confirmPassword") ?? ""),
      });
      router.push("/signup/verify-email");
    } catch (err) {
      setError(toMessage(err));
      setPending(false);
    }
  };

  return (
    <AuthPageChrome>
      <div className="text-center">
        <h1 className="text-2xl font-bold text-ink sm:text-[1.75rem]">Создать аккаунт</h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">
          Первые посты будут готовы через 5 минут — без привязки карты.
        </p>
      </div>

      <form className="mt-7 flex flex-col gap-4" onSubmit={handleSubmit}>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-ink">Имя</span>
            <input
              name="firstName"
              type="text"
              required
              autoComplete="given-name"
              placeholder="Иван"
              className={inputClass}
            />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-ink">Фамилия</span>
            <input
              name="lastName"
              type="text"
              required
              autoComplete="family-name"
              placeholder="Иванов"
              className={inputClass}
            />
          </label>
        </div>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">
            Отчество{" "}
            <span className="font-normal text-ink-muted">(не обязательно)</span>
          </span>
          <input type="text" placeholder="Иванович" className={inputClass} />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Email</span>
          <input
            name="email"
            type="email"
            required
            placeholder="you@example.com"
            className={inputClass}
          />
        </label>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-ink">Пароль</span>
            <PasswordInput name="password" required autoComplete="new-password" placeholder="••••••••" />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-ink">Повторите пароль</span>
            <PasswordInput
              name="confirmPassword"
              required
              autoComplete="new-password"
              placeholder="••••••••"
            />
          </label>
        </div>

        <label className="flex items-start gap-2.5 py-1 text-sm leading-relaxed text-ink-muted">
          <Checkbox required className="mt-0.5" />
          <span>
            Я принимаю{" "}
            <Link
              href="/legal"
              className="font-medium text-brand transition-colors hover:text-brand-hover"
            >
              условия использования
            </Link>
          </span>
        </label>

        <FormError>{error}</FormError>

        <button
          type="submit"
          disabled={pending}
          className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
        >
          {pending ? "Создаём аккаунт…" : "Зарегистрироваться"}
        </button>

        <Link
          href="/login"
          className="inline-flex w-full items-center justify-center rounded-full border border-border px-6 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft"
        >
          Войти
        </Link>
      </form>
    </AuthPageChrome>
  );
}
