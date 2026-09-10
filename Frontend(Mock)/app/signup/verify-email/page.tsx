"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import FormError from "@/components/auth/FormError";
import Icon from "@/components/ui/Icon";
import { resendConfirmation } from "@/lib/api/auth";
import { toMessage } from "@/lib/api/errors";
import { toast } from "@/lib/toast";

export default function VerifyEmailPage() {
  const [email, setEmail] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      setEmail(sessionStorage.getItem("uc_signup_email") ?? "");
    } catch {}
  }, []);

  const handleResend = async () => {
    if (!email) {
      setError("Не удалось определить адрес — вернитесь и введите его заново");
      return;
    }
    setPending(true);
    setError(null);
    try {
      await resendConfirmation(email);
      toast("Письмо отправлено ещё раз");
    } catch (err) {
      setError(toMessage(err));
    } finally {
      setPending(false);
    }
  };

  return (
    <AuthPageChrome>
      <div className="flex flex-col items-center text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-blue text-brand">
          <Icon name="mail" size={24} aria-hidden="true" />
        </div>

        <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[1.75rem]">Проверьте почту</h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">
          Мы отправили ссылку для подтверждения{email ? ` на ${email}` : ""}. Перейдите по ней,
          чтобы активировать аккаунт — письмо может идти пару минут.
        </p>
      </div>

      <div className="mt-6 flex flex-col gap-3">
        <FormError>{error}</FormError>

        <button
          type="button"
          onClick={handleResend}
          disabled={pending}
          className="btn-glass-blue inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
        >
          {pending ? "Отправляем…" : "Отправить письмо ещё раз"}
        </button>

        <Link
          href="/login"
          className="inline-flex w-full items-center justify-center rounded-full border border-border px-6 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft"
        >
          Я подтвердил — войти
        </Link>
      </div>

      <Link
        href="/signup"
        className="mt-3 block text-center text-sm text-ink-muted transition-colors hover:text-ink"
      >
        ← Изменить email
      </Link>
    </AuthPageChrome>
  );
}
