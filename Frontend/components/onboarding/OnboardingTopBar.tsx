"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import { useSession } from "@/lib/session/SessionProvider";
import { dropClass, useDropDirection } from "@/lib/useDropDirection";

export default function OnboardingTopBar() {
  const { user, signOut } = useSession();
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const dir = useDropDirection(open, ref, 300);

  // Ревью — отдельный роут поверх визарда; с него удобно вернуться к вводу данных.
  const onReview = pathname === "/onboarding/review";

  // Инициалы и имя берём из сессии, а не из демо-данных.
  const displayName = user ? `${user.firstName} ${user.lastName}`.trim() || user.email : "Аккаунт";
  const displayEmail = user?.email ?? "";
  const initials =
    displayName
      .split(" ")
      .map((part) => part[0] ?? "")
      .slice(0, 2)
      .join("")
      .toUpperCase() || "U";

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-3 border-b border-border/60 bg-card/70 px-4 backdrop-blur-xl sm:px-6">
      <div className="flex min-w-0 items-center gap-3 sm:gap-5">
        <Link href={onReview ? "/onboarding" : "/"} aria-label="UCust" className="shrink-0">
          <Image
            src="/logo-wordmark.webp"
            alt="UCust"
            width={700}
            height={161}
            unoptimized
            className="h-7 w-auto dark:hidden"
          />
          <Image
            src="/brand/logo-lighttext.webp"
            alt="UCust"
            width={700}
            height={161}
            unoptimized
            className="hidden h-7 w-auto dark:block"
          />
        </Link>

        {onReview && (
          <Link
            href="/onboarding"
            className="inline-flex items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-sm font-medium text-ink-muted transition hover:bg-surface-soft hover:text-ink"
          >
            <Icon name="arrow-left" size={16} aria-hidden="true" />
            Онбординг
          </Link>
        )}
      </div>

      <div ref={ref} className="relative shrink-0">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-label="Профиль"
          className="flex items-center gap-2 rounded-xl py-1 pl-1 pr-2 transition hover:bg-surface-soft sm:pr-3"
        >
          <span className="relative flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand text-sm font-semibold text-white">
            {user?.fullAvatarUrl ? (
              <Image src={user.fullAvatarUrl} alt="" fill unoptimized className="object-cover" />
            ) : (
              initials
            )}
          </span>
          <span className="hidden pr-1 text-sm font-medium text-ink sm:block">{displayName}</span>
          <Icon
            name="chevron-down"
            size={14}
            className={`text-ink-muted transition-transform ${open ? "rotate-180" : ""}`}
            aria-hidden="true"
          />
        </button>

        {open && (
          <div
            className={`absolute right-0 z-50 w-64 overflow-hidden rounded-2xl border border-border bg-card/95 p-1.5 shadow-lift backdrop-blur-xl ${dropClass(dir)}`}
          >
            <div className="px-3 py-2">
              <p className="text-sm font-semibold text-ink">{displayName}</p>
              <p className="truncate text-xs text-ink-muted">{displayEmail}</p>
            </div>
            <div className="my-1 h-px bg-border" />

            <Link
              href="/dashboard/account"
              onClick={() => setOpen(false)}
              className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
            >
              <Icon name="settings" size={16} aria-hidden="true" /> Профиль
            </Link>
            <Link
              href="/dashboard"
              onClick={() => setOpen(false)}
              className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
            >
              <Icon name="dashboard" size={16} aria-hidden="true" /> Дашборд
            </Link>
            <div className="my-1 h-px bg-border" />

            <button
              type="button"
              onClick={async () => {
                setOpen(false);
                // Сессию гасим и на сервере: refresh-кука не должна пережить выход.
                await signOut();
                router.push("/");
              }}
              className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
            >
              <Icon name="logout" size={16} aria-hidden="true" /> Выйти
            </button>
          </div>
        )}
      </div>
    </header>
  );
}