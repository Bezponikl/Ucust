import Image from "next/image";
import { LEGAL_LINKS, LEGAL_COMPANY } from "@/lib/legal";
import { SOCIALS } from "@/lib/socials";

const COLUMNS = [
  {
    title: "Продукт",
    links: [
      { label: "Возможности", href: "/#features" },
      { label: "Тарифы", href: "/#pricing" },
      { label: "Демо", href: "/#product-showcase" },
    ],
  },
  {
    title: "Компания",
    links: [
      { label: "О нас", href: "/about" },
      { label: "Инвесторам", href: "/investors" },
      { label: "Контакты", href: "/contacts" },
    ],
  },
  {
    title: "Правовое",
    links: LEGAL_LINKS,
  },
];

export default function Footer() {
  return (
    <div className="w-full sm:mx-auto sm:max-w-(--container-page) sm:px-6 sm:pb-6">
      {/* Мобайл — футер на всю ширину; sm+ — закруглённая карточка (как в вебе) */}
      <footer className="border-t border-border bg-card px-5 py-7 sm:rounded-[24px] sm:border sm:px-6">
        <div className="flex flex-col gap-10 md:flex-row md:items-start md:gap-16">
          <div className="md:w-64 md:shrink-0">
            <Image src="/logo-wordmark.webp" alt="UCust" width={700} height={161} unoptimized className="h-6 w-auto sm:h-7 dark:hidden" />
            <Image src="/brand/logo-lighttext.webp" alt="UCust" width={700} height={161} unoptimized className="hidden h-6 w-auto sm:h-7 dark:block" />
            <p className="mt-3 text-xs leading-relaxed text-ink-muted">ИИ-маркетолог для малого бизнеса.</p>
            <a
              href="mailto:ucust@yandex.ru"
              className="mt-3 inline-block text-sm font-medium text-ink transition-colors hover:text-brand"
            >
              ucust@yandex.ru
            </a>
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
              <div
                key={column.title}
                className={column.title === "Правовое" ? "col-span-2 sm:col-span-1" : undefined}
              >
                <h3 className="kicker text-xs text-ink-muted">{column.title}</h3>
                <ul className="mt-3 flex flex-col gap-2.5">
                  {column.links.map((link) => (
                    <li key={link.label}>
                      <a
                        href={link.href}
                        className="whitespace-nowrap text-sm text-ink transition-colors hover:text-brand"
                      >
                        {link.label}
                      </a>
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
    </div>
  );
}
