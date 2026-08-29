"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import FormError from "@/components/auth/FormError";
import Icon from "@/components/ui/Icon";
import PasswordInput from "@/components/ui/PasswordInput";
import { toast } from "@/lib/toast";
import { resetPassword } from "@/lib/api/auth";
import { toMessage } from "@/lib/api/errors";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [done, setDone] = useState(false);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Токен приходит в ссылке из письма. Читаем из location, а не через
    // useSearchParams: тот потребовал бы Suspense и убрал страницу из статики.
    setToken(new URLSearchParams(window.location.search).get("token"));
  }, []);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (password.length < 8) {
      toast("Пароль — минимум 8 символов");
      return;
    }
    if (password !== confirm) {
      toast("Пароли не совпадают");
      return;
    }

    if (!token) {
      setError("Ссылка недействительна — запросите новую на странице восстановления");
      return;
    }

    setPending(true);
    setError(null);
    try {
      await resetPassword(token, password, confirm);
      try {
        sessionStorage.removeItem("uc_reset_email");
      } catch {}
      setDone(true);
    } catch (err) {
      setError(toMessage(err));
      setPending(false);
    }
  };

  if (done) {
    return (
      <AuthPageChrome>
        <div className="flex flex-col items-center text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-success/15 text-success">
            <Icon name="check-bold" size={24} aria-hidden="true" />
          </div>
          <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[1.75rem]">Пароль обновлён</h1>
          <p className="mt-2 text-sm leading-relaxed text-ink-muted">
            Готово! Войдите в аккаунт с новым паролем.
          </p>
        </div>

        <button
          type="button"
          onClick={() => router.push("/login")}
          className="btn-glass-blue mt-6 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
        >
          Войти
        </button>
      </AuthPageChrome>
    );
  }

  return (
    <AuthPageChrome>
      <div className="flex flex-col items-center text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-blue text-brand">
          <Icon name="shield" size={24} aria-hidden="true" />
        </div>
        <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[1.75rem]">Новый пароль</h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">
          Придумайте новый пароль — не короче 8 символов.
        </p>
      </div>

      <form className="mt-7 flex flex-col gap-4" onSubmit={handleSubmit}>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Новый пароль</span>
          <PasswordInput
            required
            autoFocus
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Повторите пароль</span>
          <PasswordInput
            required
            placeholder="••••••••"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />
        </label>

        <FormError>{error}</FormError>

        <button
          type="submit"
          disabled={pending}
          className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
        >
          {pending ? "Сохраняем…" : "Сохранить пароль"}
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
