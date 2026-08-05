import Image from "next/image";
import Link from "next/link";
import { LEGAL_LINKS, LEGAL_COMPANY } from "@/lib/legal";
import { SOCIALS } from "@/lib/socials";

// Колонки под функциональную часть. Без «Возможности»/«Вопросы» — они уместны на лендинге.
const COLUMNS = [
  {
    title: "Компания",
    links: [
      { label: "О нас", href: "/about" },
      { label: "Контакты", href: "/contacts" },
      { label: "Тарифы", href: "/#pricing" },
    ],
  },
  {
    title: "Поддержка",
    links: [
      { label: "Написать в поддержку", href: "mailto:support@ucust.online" },
      { label: "Сообщить о проблеме", href: "mailto:support@ucust.online?subject=Проблема" },
    ],
  },
  {
    title: "Правовое",
    links: LEGAL_LINKS,
  },
];

// Компактный футер функциональной части — карточка внутри рабочей зоны, с закруглением.
export default function DashboardFooter() {
  return (
    <footer className="mt-6 rounded-[24px] border border-border bg-card px-5 py-7 sm:px-6">
      <div className="flex flex-col gap-10 md:flex-row md:items-start md:gap-16">
        <div className="md:w-64 md:shrink-0">
          <Image src="/logo-wordmark.webp" alt="UCust" width={700} height={161} unoptimized className="h-6 w-auto sm:h-7 dark:hidden" />
          <Image src="/brand/logo-lighttext.webp" alt="UCust" width={700} height={161} unoptimized className="hidden h-6 w-auto sm:h-7 dark:block" />
          <p className="mt-3 text-xs leading-relaxed text-ink-muted">ИИ-маркетолог для малого бизнеса.</p>
          <ul className="mt-4 flex items-center gap-2.5">
            {SOCIALS.map((social) => (
              <li key={social.label}>
                <a
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={social.label}
                  className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-xl bg-surface-soft shadow-soft transition-transform duration-200 hover:-translate-y-0.5"
                >
                  <Image src={social.icon} alt={social.label} width={22} height={22} className="h-5 w-5 object-contain" />
                </a>
              </li>
            ))}
          </ul>
        </div>

        <div className="grid flex-1 grid-cols-2 gap-x-8 gap-y-6 sm:grid-cols-3">
          {COLUMNS.map((column) => (
            <div key={column.title}>
              <h3 className="kicker text-xs text-ink-muted">{column.title}</h3>
              <ul className="mt-3 flex flex-col gap-2.5">
                {column.links.map((link) => (
                  <li key={link.label}>
                    <Link href={link.href} className="text-sm text-ink transition-colors hover:text-brand">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8 flex flex-col gap-2 border-t border-border pt-6">
        <p className="text-xs leading-relaxed text-ink-muted">
          * Instagram принадлежит компании Meta, признанной экстремистской организацией и запрещённой на территории РФ.
        </p>
        <p className="text-xs leading-relaxed text-ink-muted">
          © 2026 UCust. Правообладатель — {LEGAL_COMPANY}. Данные обрабатываются и хранятся на территории РФ.
        </p>
      </div>
    </footer>
  );
}
