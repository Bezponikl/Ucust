"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import { LEGAL_LINKS } from "@/lib/legal";
import { useDashboard } from "./DashboardProvider";
import { menuSurfaceClass, topbarButtonClass } from "@/lib/dashboard/surface";
import { dropClass, useDropDirection } from "@/lib/useDropDirection";
import { useSession } from "@/lib/session/SessionProvider";
import { startTour } from "@/lib/dashboard/tour";

export default function ProfileMenu() {
  const { surfaceStyle } = useDashboard();
  const { signOut, user } = useSession();

  // Профиль подгружается после старта сессии — до этого показываем нейтральное «Аккаунт».
  const displayName = user ? `${user.firstName} ${user.lastName}`.trim() || user.email : "Аккаунт";
  const displayEmail = user?.email ?? "";
  const initials =
    displayName
      .split(" ")
      .map((part) => part[0] ?? "")
      .slice(0, 2)
      .join("")
      .toUpperCase() || "U";
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const dir = useDropDirection(open, ref, 340);
  const router = useRouter();

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        data-tour="help"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label="Профиль"
        className={`${topbarButtonClass(surfaceStyle)} flex items-center gap-2 py-1 pl-1 pr-3`}
      >
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand text-sm font-semibold text-white">
          {initials}
        </span>
        <span className="hidden pr-1 text-sm font-medium text-ink sm:block">{displayName}</span>
      </button>

      {open && (
        <div className={`absolute right-0 z-50 w-64 overflow-hidden rounded-2xl border border-border p-1.5 shadow-lift ${dropClass(dir)} ${menuSurfaceClass(surfaceStyle)}`}>
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
            <Icon name="settings" size={16} aria-hidden="true" /> Управление аккаунтом
          </Link>
          <Link
            href="/dashboard/appearance"
            onClick={() => setOpen(false)}
            className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
          >
            <Icon name="image" size={16} aria-hidden="true" /> Оформление
          </Link>
          <Link
            href="/dashboard/subscription"
            onClick={() => setOpen(false)}
            className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
          >
            <Icon name="card" size={16} aria-hidden="true" /> Подписка
          </Link>
          <Link
            href="/dashboard/support"
            onClick={() => setOpen(false)}
            className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
          >
            <Icon name="help" size={16} aria-hidden="true" /> Поддержка
          </Link>
          {/* Раньше подсказки жили под отдельной кнопкой «?» в шапке. Кнопку убрали,
              чтобы не множить иконки в топбаре, — тур запускается отсюда. */}
          <button
            type="button"
            onClick={() => {
              setOpen(false);
              startTour();
            }}
            className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
          >
            <Icon name="sparkles" size={16} className="text-brand" aria-hidden="true" /> Как работает платформа
          </button>
          <div className="my-1 h-px bg-border" />

          {/* Правовые — один пункт: переключение между офертой, политикой и согласием
              живёт вкладками на самой странице, а не вторым уровнем в меню. */}
          <div>
            <Link
              href={`/dashboard${LEGAL_LINKS[0].href}`}
              onClick={() => setOpen(false)}
              className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
            >
              <Icon name="scale" size={16} aria-hidden="true" /> Правовые
            </Link>
            <div className="my-1 h-px bg-border" />
          </div>

          <button
            type="button"
            onClick={async () => {
              setOpen(false);
              // Сессию гасим и на сервере: без этого refresh-кука осталась бы жить.
              await signOut();
              router.push("/");
            }}
            className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
          >
            <Icon name="logout" size={16} aria-hidden="true" />
            Выйти
          </button>
        </div>
      )}
    </div>
  );
}
