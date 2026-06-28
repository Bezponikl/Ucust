"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { MailCheck } from "lucide-react";

function VerifyEmailInner() {
  const router = useRouter();
  const email = useSearchParams().get("email");
  const [sent, setSent] = useState(false);

  return (
    <main className="grid min-h-dvh place-items-center bg-canvas px-5">
      <div className="w-full max-w-md rounded-[28px] border border-border bg-card p-8 text-center shadow-soft">
        <span className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-brand-tint text-brand">
          <MailCheck size={30} aria-hidden="true" />
        </span>
        <h1 className="text-2xl font-bold text-ink">Подтвердите почту</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Мы отправили письмо на{" "}
          {email ? <span className="font-medium text-ink">{email}</span> : "вашу почту"}. Перейдите по
          ссылке из письма, чтобы продолжить.
        </p>
        <button
          type="button"
          onClick={() => router.push("/onboarding")}
          className="btn-glass-blue mt-6 inline-flex w-full items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
        >
          Я подтвердил почту
        </button>
        <button
          type="button"
          disabled={sent}
          onClick={() => setSent(true)}
          className="mt-4 text-sm text-ink-muted hover:text-brand disabled:opacity-50"
        >
          {sent ? "Письмо отправлено" : "Отправить повторно"}
        </button>
      </div>
    </main>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={null}>
      <VerifyEmailInner />
    </Suspense>
  );
}
