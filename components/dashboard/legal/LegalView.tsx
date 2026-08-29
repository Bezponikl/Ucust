import Link from "next/link";
import Icon from "@/components/ui/Icon";
import LegalBody from "@/components/legal/LegalBody";
import { SettingsCard } from "@/components/dashboard/settings/primitives";
import { LEGAL_LINKS, LEGAL_UPDATED, type LegalDoc } from "@/lib/legal";

export default function LegalView({ doc }: { doc: LegalDoc }) {
  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Правовое</h1>
        <p className="mt-0.5 text-sm text-ink-muted">Договоры, политики и согласия UCust</p>
      </div>

      {/* Документов шесть — переключатель переносится по строкам, а не сжимается */}
      <div role="tablist" aria-label="Правовые документы" className="flex flex-wrap gap-1 self-start rounded-xl bg-surface-soft p-1">
        {LEGAL_LINKS.map((l) => {
          const active = l.slug === doc.slug;
          return (
            <Link
              key={l.slug}
              href={`/dashboard${l.href}`}
              role="tab"
              aria-selected={active}
              title={l.title}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                active ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
              }`}
            >
              {l.label}
            </Link>
          );
        })}
      </div>

      <SettingsCard title={doc.title} desc={`Редакция от ${LEGAL_UPDATED} · ${doc.desc}`}>
        <div className="flex flex-col gap-5">
          {/* Оглавление свёрнуто: документы длинные, но читают их обычно точечно */}
          {doc.toc.length > 0 && (
            <details className="rounded-2xl border border-border bg-surface-soft/60 px-4 py-3">
              <summary className="cursor-pointer text-sm font-semibold text-ink">
                Разделы документа ({doc.toc.length})
              </summary>
              <ul className="mt-2 grid gap-1.5 sm:grid-cols-2">
                {doc.toc.map((s) => (
                  <li key={s.id}>
                    <a href={`#${s.id}`} className="text-sm text-ink-muted transition hover:text-brand">
                      {s.text}
                    </a>
                  </li>
                ))}
              </ul>
            </details>
          )}

          <LegalBody blocks={doc.blocks} />

          <Link
            href={`/legal/${doc.slug}`}
            target="_blank"
            className="inline-flex w-fit items-center gap-1.5 border-t border-border pt-4 text-xs font-medium text-ink-muted transition hover:text-brand"
          >
            <Icon name="external" size={14} aria-hidden="true" />
            Открыть публичную версию документа
          </Link>
        </div>
      </SettingsCard>
    </div>
  );
}
