import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { LEGAL_DOCS, getLegalDoc } from "@/lib/legal";
import PageWindow from "@/components/dashboard/PageWindow";
import LegalView from "@/components/dashboard/legal/LegalView";

export function generateStaticParams() {
  return LEGAL_DOCS.map((d) => ({ slug: d.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const doc = getLegalDoc(slug);
  return { title: doc ? `${doc.title} — UCust` : "Документ не найден — UCust" };
}

export default async function DashboardLegalPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const doc = getLegalDoc(slug);
  if (!doc) notFound();

  return (
    <PageWindow>
      <LegalView doc={doc} />
    </PageWindow>
  );
}
