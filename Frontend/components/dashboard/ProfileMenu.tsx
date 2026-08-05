"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import { LEGAL_LINKS } from "@/lib/legal";
import { useDashboard } from "./DashboardProvider";
import { menuSurfaceClass, topbarButtonClass } from "@/lib/dashboard/surface";

export default function ProfileMenu() {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);
  const [legalOpen, setLegalOpen] = useState(false);
  const [dark, setDark] = useState(false);
  const [mounted, setMounted] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  useEffect(() => {
    if (!open) {
      setLegalOpen(false); // при закрытии меню возвращаем «Правовое» в свёрнутое состояние
      return;
    }
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  // Смена темы — тот же механизм, что и в ThemeToggle (класс .dark + localStorage).
  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {}
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label="Профиль"
        className={`${topbarButtonClass(surfaceStyle)} flex items-center gap-2 py-1 pl-1 pr-3`}
      >
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand text-sm font-semibold text-white">
          АИ
        </span>
        <span className="hidden pr-1 text-sm font-medium text-ink sm:block">Анна Иванова</span>
      </button>

      {open && (
        <div className={`absolute right-0 top-full z-50 mt-2 w-56 overflow-hidden rounded-2xl border border-border p-1.5 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}>
          <div className="px-3 py-2">
            <p className="text-sm font-semibold text-ink">Анна Иванова</p>
            <p className="truncate text-xs text-ink-muted">anna@example.com</p>
          </div>
          <div className="my-1 h-px bg-border" />

          {/* Смена темы живёт в профиле — на мобиле в шапке её нет (на десктопе есть отдельная кнопка) */}
          <button
            type="button"
            onClick={toggleTheme}
            className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft sm:hidden"
          >
            {mounted && dark ? <Icon name="sun" size={16} aria-hidden="true" /> : <Icon name="moon" size={16} aria-hidden="true" />}
            {mounted && dark ? "Светлая тема" : "Тёмная тема"}
          </button>

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
          <div className="my-1 h-px bg-border" />

          {/* Правовое — в дашборде нет футера (только на лендинге), поэтому доступно всегда.
              Свёрнуто по умолчанию, раскрывается по нажатию. */}
          <div>
            <button
              type="button"
              onClick={() => setLegalOpen((v) => !v)}
              aria-expanded={legalOpen}
              className="flex w-full items-center justify-between gap-2 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
            >
              <span className="flex items-center gap-2.5">
                <Icon name="scale" size={16} aria-hidden="true" /> Правовое
              </span>
              <Icon name="chevron-down" size={15} className={`text-ink-muted transition-transform ${legalOpen ? "rotate-180" : ""}`} aria-hidden="true" />
            </button>
            {legalOpen && (
              <div className="uc-pop-in">
                {LEGAL_LINKS.map((l) => (
                  <Link
                    key={l.href}
                    href={`/dashboard${l.href}`}
                    onClick={() => setOpen(false)}
                    className="block rounded-xl py-2 pl-10 pr-3 text-sm text-ink-muted transition-colors hover:bg-surface-soft hover:text-ink"
                  >
                    {l.label}
                  </Link>
                ))}
              </div>
            )}
            <div className="my-1 h-px bg-border" />
          </div>

          <button
            type="button"
            onClick={() => {
              setOpen(false);
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
