"use client";

import Link from "next/link";
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
        <div className="flex flex-col gap-6">
          <p className="text-sm leading-relaxed text-ink-muted">{doc.intro}</p>

          {doc.sections.map((section) => (
            <section key={section.heading}>
              <h2 className="text-sm font-bold text-ink">{section.heading}</h2>
              <div className="mt-2 flex flex-col gap-2">
                {section.body.map((p, i) => (
                  <p key={i} className="text-sm leading-relaxed text-ink-muted">{p}</p>
                ))}
              </div>
            </section>
          ))}
        </div>
      </SettingsCard>
    </div>
  );
}
