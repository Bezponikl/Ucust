import { notFound } from "next/navigation";
import PageWindow from "@/components/dashboard/PageWindow";
import PromoEditView from "@/components/dashboard/promos/PromoEditView";
import { PROMOS } from "@/lib/dashboard/promos";

export function generateStaticParams() {
  return PROMOS.map((p) => ({ id: p.id }));
}

export default async function PromoPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const promo = PROMOS.find((p) => p.id === id);
  if (!promo) notFound();

  return (
    <PageWindow>
      <PromoEditView promo={promo} />
    </PageWindow>
  );
}
