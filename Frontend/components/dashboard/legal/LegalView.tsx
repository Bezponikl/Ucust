"use client";

import Link from "next/link";
import LegalBody from "@/components/legal/LegalBody";
import { SettingsCard } from "@/components/dashboard/settings/primitives";
import { LEGAL_LINKS, LEGAL_UPDATED, type LegalDoc } from "@/lib/legal";

export default function LegalView({ doc }: { doc: LegalDoc }) {
  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Правовое</h1>
        <p className="mt-0.5 text-sm text-ink-muted">Договоры и политики UCust</p>
      </div>

      <div role="tablist" className="flex flex-wrap gap-1 self-start rounded-xl bg-surface-soft p-1">
        {LEGAL_LINKS.map((l) => {
          const active = l.href === `/legal/${doc.slug}`;
          return (
            <Link
              key={l.href}
              href={`/dashboard${l.href}`}
              role="tab"
              aria-selected={active}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                active ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
              }`}
            >
              {l.label}
            </Link>
          );
        })}
      </div>

      <SettingsCard title={doc.title} desc={`Редакция от ${LEGAL_UPDATED}`}>
        <LegalBody blocks={doc.blocks} />
      </SettingsCard>
    </div>
  );
}
