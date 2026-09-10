import ComingSoon from "@/components/dashboard/ComingSoon";
import PageWindow from "@/components/dashboard/PageWindow";

export default function PromosPage() {
  return (
    <PageWindow>
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-xl font-bold text-ink sm:text-2xl">Акции</h1>
          <p className="mt-0.5 text-sm text-ink-muted">Акции и скидки для клиентов</p>
        </div>

        <ComingSoon
          icon="gift"
          title="Акции скоро появятся"
          text="Здесь можно будет создавать акции и скидки и следить за их результатами — пока без выдуманных данных."
        />
      </div>
    </PageWindow>
  );
}