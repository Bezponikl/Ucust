"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import FormError from "@/components/auth/FormError";
import SocialAuth from "@/components/auth/SocialAuth";
import Checkbox from "@/components/ui/Checkbox";
import PasswordInput from "@/components/ui/PasswordInput";
import { toMessage } from "@/lib/api/errors";
import { linkSocial } from "@/lib/api/auth";
import { oauthErrorMessage, parseLinkSocialHint, type LinkSocialHint } from "@/lib/api/oauth";
import { useSession } from "@/lib/session/SessionProvider";

const inputClass =
  "rounded-full border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card";

const PROVIDER_NAMES: Record<string, string> = {
  YANDEX: "Яндекс",
  VK: "ВКонтакте",
};

export default function LoginPage() {
  const router = useRouter();
  const { signIn, reload } = useSession();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [linkHint, setLinkHint] = useState<LinkSocialHint | null>(null);
  const [linkPending, setLinkPending] = useState(false);
  const [linkError, setLinkError] = useState<string | null>(null);

  // Вход через соцсеть возвращает сюда с кодом ошибки, если что-то не сложилось.
  // Отдельный случай — почта из соцсети совпала с почтой парольного аккаунта:
  // тогда в адресе приходят данные провайдера, и мы показываем форму привязки.
  useEffect(() => {
    const hint = parseLinkSocialHint(window.location.search);
    if (hint) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLinkHint(hint);
      window.history.replaceState(null, "", "/login");
      return;
    }

    const code = new URLSearchParams(window.location.search).get("error");
    const message = oauthErrorMessage(code);
    if (!message) return;
    setError(message);
    window.history.replaceState(null, "", "/login");
  }, []);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const data = new FormData(e.currentTarget);
    const rememberMe = data.get("rememberMe") != null;
    setPending(true);
    setError(null);
    try {
      await signIn(String(data.get("email") ?? ""), String(data.get("password") ?? ""), rememberMe);
      router.push("/dashboard");
    } catch (err) {
      setError(toMessage(err));
      setPending(false);
    }
  };

  const handleLinkSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!linkHint) return;

    const data = new FormData(e.currentTarget);
    const password = String(data.get("password") ?? "");
    setLinkPending(true);
    setLinkError(null);
    try {
      await linkSocial({
        email: linkHint.email,
        password,
        provider: linkHint.provider,
        providerUserId: linkHint.providerUserId,
      });
      await reload();
      router.push("/dashboard");
    } catch (err) {
      setLinkError(toMessage(err));
      setLinkPending(false);
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

      {linkHint ? (
        <LinkSocialForm
          linkHint={linkHint}
          pending={linkPending}
          error={linkError}
          onCancel={() => setLinkHint(null)}
          onSubmit={handleLinkSubmit}
        />
      ) : (
        <form className="mt-7 flex flex-col gap-4" onSubmit={handleSubmit}>
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-ink">Email</span>
            <input
              name="email"
              type="email"
              required
              autoComplete="email"
              placeholder="you@example.com"
              className={inputClass}
            />
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
            {pending ? "Входим…" : "Войти"}
          </button>

          <Link
            href="/signup"
            className="inline-flex w-full items-center justify-center rounded-full border border-border px-6 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft"
          >
            Зарегистрироваться
          </Link>
        </form>
      )}

      <SocialAuth />
    </AuthPageChrome>
  );
}

function LinkSocialForm({
  linkHint,
  pending,
  error,
  onCancel,
  onSubmit,
}: {
  linkHint: LinkSocialHint;
  pending: boolean;
  error: string | null;
  onCancel: () => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="mt-7 flex flex-col gap-4">
      <div className="rounded-2xl border border-border bg-surface-soft p-4 text-sm leading-relaxed">
        <p className="font-semibold text-ink">На этой почте уже существует аккаунт.</p>
        <p className="mt-1 text-ink-muted">
          Чтобы продолжить вход и привязать {PROVIDER_NAMES[linkHint.provider] ?? linkHint.provider} к
          текущему аккаунту на {linkHint.email}, введите пароль от аккаунта.
        </p>
      </div>

      <form className="flex flex-col gap-4" onSubmit={onSubmit}>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Email</span>
          <input
            readOnly
            value={linkHint.email}
            className="rounded-full border border-border bg-surface-soft px-4 py-3 text-sm text-ink-muted outline-none"
          />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Пароль</span>
          <PasswordInput name="password" required autoComplete="current-password" placeholder="••••••••" />
        </label>

        <FormError>{error}</FormError>

        <button
          type="submit"
          disabled={pending}
          className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
        >
          {pending ? "Привязываем…" : "Подтвердить и войти"}
        </button>

        <button
          type="button"
          onClick={onCancel}
          disabled={pending}
          className="inline-flex w-full items-center justify-center rounded-full border border-border px-6 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-surface-soft disabled:cursor-not-allowed disabled:opacity-60"
        >
          Отмена
        </button>
      </form>
    </div>
  );
}
