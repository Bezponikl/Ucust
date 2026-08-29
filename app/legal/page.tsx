import type { Metadata } from "next";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import { LEGAL_COMPANY, LEGAL_LINKS, LEGAL_UPDATED } from "@/lib/legal";

export const metadata: Metadata = { title: "Правовые документы — UCust" };

export default function LegalIndexPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-10 sm:px-6 sm:py-14">
      <h1 className="font-display text-2xl font-bold text-ink sm:text-3xl">
        Правовые документы
      </h1>
      <p className="mt-2 text-sm text-ink-muted">
        Действующая редакция от {LEGAL_UPDATED} · правообладатель {LEGAL_COMPANY}
      </p>

      <div className="mt-8 flex flex-col gap-3">
        {LEGAL_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="group flex items-start gap-4 rounded-2xl border border-border bg-surface-soft px-5 py-4 transition-colors hover:border-brand/40 hover:bg-card"
          >
            <span
              aria-hidden="true"
              className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-tint text-brand"
            >
              <Icon name="file-text" size={17} />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-sm font-semibold text-ink">{link.title}</span>
              {/* Подпись важнее названия: по ней понятно, туда ли вы идёте */}
              <span className="mt-0.5 block text-xs leading-relaxed text-ink-muted">{link.desc}</span>
            </span>
            <Icon
              name="arrow-right"
              size={18}
              className="mt-1 shrink-0 text-ink-muted transition-colors group-hover:text-brand"
              aria-hidden="true"
            />
          </Link>
        ))}
      </div>
    </div>
  );
}
