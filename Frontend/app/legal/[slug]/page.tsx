import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { LEGAL_DOCS, LEGAL_LINKS, LEGAL_UPDATED, getLegalDoc } from "@/lib/legal";

export function generateStaticParams() {
  return LEGAL_DOCS.map((d) => ({ slug: d.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const doc = getLegalDoc(slug);
  return { title: doc ? `${doc.title} — UCust` : "Документ не найден — UCust" };
}

export default async function LegalPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const doc = getLegalDoc(slug);
  if (!doc) notFound();

  return (
    <div className="mx-auto max-w-3xl px-5 py-10 sm:px-6 sm:py-14">
      {/* Переключатель документов */}
      <nav className="mb-8 flex flex-wrap gap-2">
        {LEGAL_LINKS.map((link) => {
          const active = link.href === `/legal/${doc.slug}`;
          return (
            <Link
              key={link.href}
              href={link.href}
              aria-current={active ? "page" : undefined}
              className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition ${
                active ? "bg-brand text-white" : "bg-surface-soft text-ink-muted hover:text-ink"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>

      <h1 className="font-display text-2xl font-bold text-ink sm:text-3xl">{doc.title}</h1>
      <p className="mt-2 text-xs text-ink-muted">Редакция от {LEGAL_UPDATED}</p>

      <p className="mt-6 text-[0.9375rem] leading-relaxed text-ink-muted">{doc.intro}</p>

      <div className="mt-8 flex flex-col gap-7">
        {doc.sections.map((section) => (
          <section key={section.heading}>
            <h2 className="text-base font-bold text-ink sm:text-lg">{section.heading}</h2>
            <div className="mt-2 flex flex-col gap-2">
              {section.body.map((p, i) => (
                <p key={i} className="text-[0.9375rem] leading-relaxed text-ink-muted">{p}</p>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
