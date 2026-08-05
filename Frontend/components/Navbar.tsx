"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import Icon from "./ui/Icon";
import { useAuthModal } from "./AuthModalProvider";
import ThemeToggle from "./ThemeToggle";

const NAV_LINKS = [
  { href: "#how-it-works", label: "Как работает", id: "how-it-works" },
  { href: "#features", label: "Возможности", id: "features" },
  { href: "#channels", label: "Каналы", id: "channels" },
  { href: "#product-showcase", label: "Продукт", id: "product-showcase" },
  { href: "#pricing", label: "Тарифы", id: "pricing" },
  { href: "#faq", label: "Вопросы", id: "faq" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState<string>("");
  const { openLogin, openSignup } = useAuthModal();

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  // Сжатие пилюли + тень после прокрутки
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Scroll-spy: подсвечиваем активную секцию
  useEffect(() => {
    const sections = NAV_LINKS.map((l) => document.getElementById(l.id)).filter(
      (el): el is HTMLElement => Boolean(el)
    );
    if (!sections.length) return;
    const obs = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) setActive(e.target.id);
        }
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach((s) => obs.observe(s));
    return () => obs.disconnect();
  }, []);

  return (
    <header className="fixed inset-x-0 top-0 z-50">
      {/* Прозрачная floating-шапка: закреплена только стеклянная пилюля,
          по бокам просвечивает фон hero (бесшовно). */}
      <div className="mx-auto max-w-(--container-page) px-5 pt-3 sm:px-6">
        <nav
          aria-label="Главная навигация"
          className={`flex items-center justify-between rounded-[24px] border border-white/10 bg-card/80 px-5 py-2.5 ring-1 ring-white/5 backdrop-blur-xl transition-shadow duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] sm:px-6 ${
            scrolled ? "shadow-lift" : "shadow-soft"
          }`}
        >
          <Link href="/" aria-label="UCust — на главную" className="flex shrink-0 items-center">
            <Image src="/logo-wordmark.webp" alt="UCust" width={700} height={161} unoptimized priority className="h-6 w-auto sm:h-7 dark:hidden" />
            <Image src="/brand/logo-lighttext.webp" alt="UCust" width={700} height={161} unoptimized priority className="hidden h-6 w-auto sm:h-7 dark:block" />
          </Link>

          <ul className="hidden items-center gap-5 lg:flex xl:gap-6">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className={`text-sm transition-colors ${
                    active === link.id ? "font-semibold text-brand" : "text-ink-muted hover:text-ink"
                  }`}
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
              className="px-3 py-2 text-sm font-medium text-ink-muted transition-colors hover:text-ink"
            >
              Войти
            </button>
            <button type="button" onClick={openSignup} className="btn-glass-blue px-4 py-2 text-sm font-semibold">
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
              <Icon name={open ? "close" : "menu"} size={22} />
            </button>
          </div>
        </nav>

        {open && (
          <div
            id="mobile-menu"
            className="mt-2 rounded-[24px] border border-white/10 bg-card/90 p-3 shadow-lift ring-1 ring-white/5 backdrop-blur-xl lg:hidden"
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
                className="px-4 py-3 text-center text-sm font-medium text-ink-muted transition-colors hover:text-ink"
              >
                Войти
              </button>
              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  openSignup();
                }}
                className="btn-glass-blue px-4 py-3 text-center text-sm font-semibold"
              >
                Зарегистрироваться
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
