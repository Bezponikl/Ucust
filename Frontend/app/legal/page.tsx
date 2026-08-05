import type { Metadata } from "next";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import { LEGAL_LINKS, LEGAL_UPDATED } from "@/lib/legal";

export const metadata: Metadata = { title: "Правовые документы — UCust" };

export default function LegalIndexPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-10 sm:px-6 sm:py-14">
      <h1 className="font-display text-2xl font-bold text-ink sm:text-3xl">
        Правовые документы
      </h1>
      <p className="mt-2 text-xs text-ink-muted">Редакция от {LEGAL_UPDATED}</p>

      <div className="mt-8 flex flex-col gap-3">
        {LEGAL_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="flex items-center justify-between rounded-2xl border border-border bg-surface-soft px-5 py-4 text-sm font-medium text-ink transition-colors hover:border-brand/40 hover:bg-card"
          >
            {link.label}
            <Icon name="arrow-right" size={18} className="text-ink-muted" aria-hidden="true" />
          </Link>
        ))}
      </div>
    </div>
  );
}
