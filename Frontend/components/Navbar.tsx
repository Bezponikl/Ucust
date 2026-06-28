"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { useAuthModal } from "./AuthModalProvider";
import ThemeToggle from "./ThemeToggle";

const NAV_LINKS = [
  { href: "#features", label: "Возможности" },
  { href: "#how-it-works", label: "Как работает" },
  { href: "#channels", label: "Каналы" },
  { href: "#pricing", label: "Тарифы" },
  { href: "#faq", label: "Вопросы" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { openLogin, openSignup } = useAuthModal();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled
          ? "border-b border-white/50 bg-white/65 shadow-[0_4px_30px_rgba(31,36,51,0.06)] backdrop-blur-xl dark:border-white/10 dark:bg-canvas/70"
          : "border-b border-transparent bg-transparent"
      }`}
    >
      <nav
        aria-label="Главная навигация"
        className="mx-auto flex max-w-(--container-page) items-center justify-between px-5 py-3.5 sm:px-6"
      >
        <Link href="/" aria-label="UCust — на главную" className="flex shrink-0 items-center">
          <Image
            src="/logo-wordmark.webp"
            alt="UCust"
            width={700}
            height={161}
            priority
            className="h-6 w-auto sm:h-7 dark:hidden"
          />
          <Image
            src="/brand/logo-lighttext.webp"
            alt="UCust"
            width={700}
            height={161}
            priority
            className="hidden h-6 w-auto sm:h-7 dark:block"
          />
        </Link>

        <ul className="hidden items-center gap-8 lg:flex">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm text-ink-muted transition-colors hover:text-ink"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden items-center gap-2 lg:flex">
          <ThemeToggle className="mr-1" />
          <button
            type="button"
            onClick={openLogin}
            className="btn-glass rounded-full px-4 py-2 text-sm font-medium"
          >
            Войти
          </button>
          <button
            type="button"
            onClick={openSignup}
            className="btn-glass-fill rounded-full px-4 py-2 text-sm font-semibold"
          >
            Зарегистрироваться
          </button>
        </div>

        <div className="flex items-center gap-1.5 lg:hidden">
          <ThemeToggle />
          <button
            type="button"
            aria-label={open ? "Закрыть меню" : "Открыть меню"}
            aria-expanded={open}
            aria-controls="mobile-menu"
            onClick={() => setOpen((v) => !v)}
            className="flex h-10 w-10 items-center justify-center rounded-full text-ink transition-colors hover:bg-surface-soft"
          >
            {open ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </nav>

      {open && (
        <div
          id="mobile-menu"
          className="border-t border-border bg-card px-5 pb-6 pt-2 lg:hidden"
        >
          <ul className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block rounded-xl px-3 py-3 text-base text-ink transition-colors hover:bg-surface-soft"
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
          <div className="mt-3 flex flex-col gap-2">
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                openLogin();
              }}
              className="btn-glass rounded-full px-4 py-3 text-center text-sm font-medium"
            >
              Войти
            </button>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                openSignup();
              }}
              className="btn-glass-fill rounded-full px-4 py-3 text-center text-sm font-semibold"
            >
              Зарегистрироваться
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
