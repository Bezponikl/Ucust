"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { useAuthModal } from "./AuthModalProvider";

const NAV_LINKS = [
  { href: "#features", label: "Возможности" },
  { href: "#how-it-works", label: "Как работает" },
  { href: "#channels", label: "Каналы" },
  { href: "#pricing", label: "Тарифы" },
  { href: "#faq", label: "FAQ" },
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
      className={`sticky top-0 z-50 border-b bg-card/95 backdrop-blur-sm transition-shadow duration-300 ${
        scrolled ? "border-border shadow-[0_1px_0_0_rgba(10,26,60,0.04)]" : "border-transparent"
      }`}
    >
      <nav
        aria-label="Главная навигация"
        className="mx-auto flex max-w-(--container-page) items-center justify-between px-5 py-3.5 sm:px-6"
      >
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <Image
            src="/logo.jpg"
            alt="UCust"
            width={120}
            height={40}
            priority
            className="h-8 w-auto sm:h-9"
          />
          <span className="sr-only">UCust</span>
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
          <button
            type="button"
            onClick={openLogin}
            className="rounded-full px-4 py-2 text-sm font-medium text-ink transition-colors hover:bg-surface-soft"
          >
            Войти
          </button>
          <button
            type="button"
            onClick={openSignup}
            className="rounded-full bg-brand-tint px-4 py-2 text-sm font-medium text-brand transition-colors hover:bg-brand hover:text-white"
          >
            Зарегистрироваться
          </button>
        </div>

        <button
          type="button"
          aria-label={open ? "Закрыть меню" : "Открыть меню"}
          aria-expanded={open}
          aria-controls="mobile-menu"
          onClick={() => setOpen((v) => !v)}
          className="flex h-10 w-10 items-center justify-center rounded-full text-ink transition-colors hover:bg-surface-soft lg:hidden"
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
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
              className="rounded-full px-4 py-3 text-center text-sm font-medium text-ink transition-colors hover:bg-surface-soft"
            >
              Войти
            </button>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                openSignup();
              }}
              className="rounded-full bg-brand px-4 py-3 text-center text-sm font-medium text-white shadow-soft transition-colors hover:bg-brand-hover"
            >
              Зарегистрироваться
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
