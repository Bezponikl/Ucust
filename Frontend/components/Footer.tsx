import Image from "next/image";

const SOCIALS = [
  { label: "VK", href: "https://vk.com", icon: "/vk.png" },
  { label: "Telegram", href: "https://t.me", icon: "/telegram.png" },
  { label: "MAX", href: "https://max.ru", icon: "/max.png" },
];

const COLUMNS = [
  {
    title: "Продукт",
    links: [
      { label: "Возможности", href: "#features" },
      { label: "Тарифы", href: "#pricing" },
      { label: "Демо", href: "#product-showcase" },
    ],
  },
  {
    title: "Поддержка",
    links: [
      { label: "Вопросы", href: "#faq" },
      { label: "Контакты", href: "/contacts" },
    ],
  },
  {
    title: "Правовое",
    links: [
      { label: "Публичная оферта", href: "/legal/offer" },
      { label: "Политика конфиденциальности", href: "/legal/privacy" },
      { label: "Согласие на обработку ПДн", href: "/legal/pdn-consent" },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-border bg-card">
      <div className="mx-auto max-w-(--container-page) px-5 py-12 sm:px-6 sm:py-16">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          <div className="col-span-2 sm:col-span-1">
            <Image
              src="/logo-wordmark.webp"
              alt="UCust"
              width={700}
              height={161}
              className="h-6 w-auto sm:h-7 dark:hidden"
            />
            <Image
              src="/brand/logo-lighttext.webp"
              alt="UCust"
              width={700}
              height={161}
              className="hidden h-6 w-auto sm:h-7 dark:block"
            />
            <ul className="mt-5 flex items-center gap-3">
              {SOCIALS.map((social) => (
                <li key={social.label}>
                  <a
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={social.label}
                    className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-xl bg-surface-soft shadow-soft transition-transform duration-200 hover:-translate-y-0.5"
                  >
                    <Image
                      src={social.icon}
                      alt={social.label}
                      width={24}
                      height={24}
                      className="h-6 w-6 object-contain"
                    />
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {COLUMNS.map((column) => (
            <div key={column.title}>
              <h3 className="kicker text-xs text-ink-muted">
                {column.title}
              </h3>
              <ul className="mt-4 flex flex-col gap-3">
                {column.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-ink transition-colors hover:text-brand"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <p className="mt-12 text-xs leading-relaxed text-ink-muted">
          © 2026 UCust. Правообладатель — ООО «ЕТА СОФТ ГРУПП». Данные
          обрабатываются и хранятся на территории РФ.
        </p>
      </div>
    </footer>
  );
}
