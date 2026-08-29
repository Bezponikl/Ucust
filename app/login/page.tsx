"use client";

import { useEffect, useState, type FormEvent } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import FormError from "@/components/auth/FormError";
import Checkbox from "@/components/ui/Checkbox";
import PasswordInput from "@/components/ui/PasswordInput";
import { toMessage } from "@/lib/api/errors";
import { linkSocial } from "@/lib/api/auth";
import {
  authorizeUrl,
  oauthErrorMessage,
  parseLinkSocialHint,
  type LinkSocialHint,
} from "@/lib/api/oauth";
import { useSession } from "@/lib/session/SessionProvider";

const inputClass =
  "rounded-full border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card";

export default function LoginPage() {
  const router = useRouter();
  const { signIn, reload } = useSession();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  /** Не null — Яндекс вернул нас сюда, чтобы привязать соцсеть к парольному аккаунту. */
  const [linkHint, setLinkHint] = useState<LinkSocialHint | null>(null);

  // Вход через соцсеть возвращает сюда с кодом ошибки, если что-то не сложилось.
  useEffect(() => {
    const search = window.location.search;
    const hint = parseLinkSocialHint(search);
    const code = new URLSearchParams(search).get("error");
    const message = oauthErrorMessage(code);
    if (!message) return;

    /* eslint-disable react-hooks/set-state-in-effect */
    if (hint) setLinkHint(hint);
    setError(message);
    /* eslint-enable react-hooks/set-state-in-effect */
    window.history.replaceState(null, "", "/login");
  }, []);

  const startYandex = () => {
    // Полноценный переход, а не fetch: дальше идёт цепочка редиректов Яндекса.
    window.location.href = authorizeUrl("yandex");
  };

  const startVk = () => {
    window.location.href = authorizeUrl("vk");
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const data = new FormData(e.currentTarget);
    const password = String(data.get("password") ?? "");
    // Галочка «запомнить меня» доезжает до бэка: от неё зависит срок жизни refresh-куки
    const rememberMe = data.get("rememberMe") === "on";
    setPending(true);
    setError(null);
    try {
      if (linkHint) {
        // Пароль подтверждает, что аккаунт наш, — и заодно привязывает соцсеть,
        // чтобы в следующий раз вход через Яндекс проходил без этого шага.
        await linkSocial({ ...linkHint, password });
        await reload();
      } else {
        await signIn(String(data.get("email") ?? ""), password, rememberMe);
      }
      router.push("/dashboard");
    } catch (err) {
      setError(toMessage(err));
      setPending(false);
    }
  };

  return (
    <AuthPageChrome>
      <div className="text-center">
        <h1 className="text-2xl font-bold text-ink sm:text-[1.75rem]">С возвращением</h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">
          Войдите в аккаунт, чтобы продолжить.
        </p>
      </div>

      <form className="mt-7 flex flex-col gap-4" onSubmit={handleSubmit}>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Email</span>
          <input
            key={linkHint?.email ?? "new"}
            name="email"
            type="email"
            required
            autoComplete="email"
            placeholder="you@example.com"
            defaultValue={linkHint?.email}
            readOnly={Boolean(linkHint)}
            aria-describedby={linkHint ? "link-social-hint" : undefined}
            className={`${inputClass} ${linkHint ? "cursor-not-allowed opacity-70" : ""}`}
          />
          {linkHint && (
            <span id="link-social-hint" className="text-xs text-ink-muted">
              Аккаунт с этой почтой уже есть. Введите пароль — Яндекс привяжется к нему.
            </span>
          )}
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Пароль</span>
          <PasswordInput name="password" required autoComplete="current-password" placeholder="••••••••" />
        </label>

        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center gap-2 text-ink-muted">
            <Checkbox name="rememberMe" />
            Запомнить меня
          </label>
          <button
            type="button"
            onClick={() => router.push("/forgot-password")}
            className="font-medium text-brand transition-colors hover:text-brand-hover"
          >
            Забыли пароль?
          </button>
        </div>

        <FormError>{error}</FormError>

        <button
          type="submit"
          disabled={pending}
          className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
        >
          {pending ? "Входим…" : linkHint ? "Войти и привязать Яндекс" : "Войти"}
        </button>

        <Link
          href="/signup"
          className="inline-flex w-full items-center justify-center rounded-full border border-border px-6 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft"
        >
          Зарегистрироваться
        </Link>
      </form>

      <div className="my-6 flex items-center gap-3 text-xs text-ink-muted">
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
        или войдите с помощью
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
      </div>

      <div className="flex items-center justify-center gap-4">
        <button
          type="button"
          onClick={startYandex}
          aria-label="Войти через Яндекс"
          className="flex h-16 w-16 items-center justify-center rounded-full bg-surface-soft transition-all hover:bg-card dark:hover:bg-white/5"
        >
          <Image
            src="/yandex.svg"
            alt=""
            width={32}
            height={32}
            className="h-8 w-8 shrink-0"
            aria-hidden="true"
          />
        </button>

        <button
          type="button"
          onClick={startVk}
          aria-label="Войти через VK"
          className="flex h-16 w-16 items-center justify-center rounded-full bg-surface-soft transition-all hover:bg-card dark:hover:bg-white/5"
        >
          <Image
            src="/vk.svg"
            alt=""
            width={32}
            height={32}
            className="h-8 w-8 shrink-0"
            aria-hidden="true"
          />
        </button>
      </div>
    </AuthPageChrome>
  );
}
