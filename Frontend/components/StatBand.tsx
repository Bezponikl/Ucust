import Reveal from "./Reveal";

// Честная «полоса в цифрах» — факты продукта, а не выдуманные счётчики клиентов.
const FACTS: { value: string; label: string }[] = [
  { value: "5", label: "соцсетей из одного окна" },
  { value: "5 мин", label: "до первого поста" },
  { value: "24/7", label: "автопостинг по расписанию" },
  { value: "0 ₽", label: "старт без карты" },
];

export default function StatBand() {
  return (
    <section className="mx-auto max-w-(--container-page) px-5 py-10 sm:px-6 sm:py-14">
      <Reveal>
        <div className="grid grid-cols-2 gap-6 rounded-[28px] border border-border bg-card px-6 py-8 shadow-soft sm:gap-8 lg:grid-cols-4 lg:px-10">
          {FACTS.map((f) => (
            <div key={f.label} className="text-center">
              <div className="font-display text-3xl font-extrabold text-brand sm:text-4xl">{f.value}</div>
              <div className="mt-1.5 text-sm text-ink-muted">{f.label}</div>
            </div>
          ))}
        </div>
      </Reveal>
    </section>
  );
}
