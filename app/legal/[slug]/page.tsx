import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Icon from "@/components/ui/Icon";
import LegalBody from "@/components/legal/LegalBody";
import { LEGAL_DOCS, LEGAL_UPDATED } from "@/lib/legal.content";
import { LEGAL_LINKS } from "@/lib/legal";

export function generateStaticParams() {
  return LEGAL_DOCS.map((d) => ({ slug: d.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const doc = LEGAL_DOCS.find((d) => d.slug === slug);
  return {
    title: doc ? `${doc.title} — UCust` : "Документ не найден — UCust",
    description: doc?.desc,
  };
}

export default async function LegalPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const doc = LEGAL_DOCS.find((d) => d.slug === slug);
  if (!doc) notFound();

  return (
    <div className="mx-auto max-w-(--container-page) px-5 py-8 sm:px-6 sm:py-12">
      <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:gap-10">
        {/* Боковая колонка: сначала все документы, затем разделы открытого */}
        <aside className="lg:sticky lg:top-8 lg:w-64 lg:shrink-0">
          <nav aria-label="Правовые документы">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-ink-muted">Документы</p>
            {/* На узких экранах список едет вбок, а не занимает пол-экрана */}
            <ul className="-mx-5 flex gap-2 overflow-x-auto px-5 pb-1 lg:mx-0 lg:flex-col lg:gap-1 lg:overflow-visible lg:px-0">
              {LEGAL_LINKS.map((link) => {
                const active = link.slug === doc.slug;
                return (
                  <li key={link.slug} className="shrink-0 lg:shrink">
                    <Link
                      href={link.href}
                      aria-current={active ? "page" : undefined}
                      className={`block whitespace-nowrap rounded-xl px-3.5 py-2 text-sm font-medium transition lg:whitespace-normal ${
                        active
                          ? "bg-brand text-white shadow-soft"
                          : "bg-surface-soft text-ink-muted hover:text-ink lg:bg-transparent lg:hover:bg-surface-soft"
                      }`}
                    >
                      {link.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {doc.toc.length > 0 && (
            <nav aria-label="Разделы документа" className="mt-6 hidden lg:block">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-ink-muted">В документе</p>
              <ul className="flex flex-col gap-1 border-l border-border pl-3">
                {doc.toc.map((s) => (
                  <li key={s.id}>
                    <a
                      href={`#${s.id}`}
                      className="block py-0.5 text-xs leading-snug text-ink-muted transition hover:text-brand"
                    >
                      {s.text}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          )}
        </aside>

        <article className="min-w-0 flex-1">
          <h1 className="font-display text-2xl font-bold text-ink sm:text-3xl">{doc.title}</h1>
          <p className="mt-2 text-xs text-ink-muted">Редакция от {LEGAL_UPDATED}</p>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{doc.desc}</p>

          {/* Оглавление на мобиле — свёрнутым списком, чтобы не отодвигать текст */}
          {doc.toc.length > 0 && (
            <details className="mt-5 rounded-2xl border border-border bg-surface-soft/60 px-4 py-3 lg:hidden">
              <summary className="cursor-pointer text-sm font-semibold text-ink">
                Разделы документа ({doc.toc.length})
              </summary>
              <ul className="mt-2 flex flex-col gap-1.5">
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

          <div className="mt-7">
            <LegalBody blocks={doc.blocks} />
          </div>

          <p className="mt-10 flex items-center gap-2 border-t border-border pt-5 text-xs text-ink-muted">
            <Icon name="mail" size={14} aria-hidden="true" />
            Вопросы по документам — на адрес поддержки, указанный в тексте документа.
          </p>
        </article>
      </div>
    </div>
  );
}
