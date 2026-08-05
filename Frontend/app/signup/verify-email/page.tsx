"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import Icon from "@/components/ui/Icon";

const AUTO_REDIRECT_SECONDS = 3;

export default function VerifyEmailPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(AUTO_REDIRECT_SECONDS);
  const redirected = useRef(false);

  useEffect(() => {
    try {
      setEmail(sessionStorage.getItem("uc_signup_email") ?? "");
    } catch {}
  }, []);

  const goToConfirm = () => {
    if (redirected.current) return;
    redirected.current = true;
    router.push("/signup/confirm");
  };

  useEffect(() => {
    if (secondsLeft <= 0) {
      goToConfirm();
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
          <Icon name="mail" size={24} aria-hidden="true" />
        </div>

        <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[1.75rem]">Проверьте почту</h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">
          Мы отправили ссылку для подтверждения{email ? ` на ${email}` : ""}. Откроем её
          автоматически через {secondsLeft} с.
        </p>
      </div>

      <button
        type="button"
        onClick={goToConfirm}
        className="btn-glass-blue mt-6 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
      >
        Открыть письмо сейчас
      </button>

      <Link
        href="/signup"
        className="mt-3 block text-center text-sm text-ink-muted transition-colors hover:text-ink"
      >
        ← Изменить email
      </Link>
    </AuthPageChrome>
  );
}
