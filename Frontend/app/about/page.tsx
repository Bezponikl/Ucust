import type { Metadata } from "next";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";
import GradientScrollText from "@/components/GradientScrollText";
import Reveal from "@/components/Reveal";
import { LEGAL_COMPANY } from "@/lib/legal";

export const metadata: Metadata = {
  title: "О нас — UCust",
  description: "UCust — ИИ-маркетолог для малого бизнеса: помогаем предпринимателям вести контент в соцсетях без агентств и штатных маркетологов.",
};

const STATS = [
  { value: "6+", label: "каналов публикации" },
  { value: "3 мин", label: "на пост вместо часа" },
  { value: "РФ", label: "хранение данных" },
];

const VALUES: { icon: IconName; title: string; text: string }[] = [
  { icon: "sparkles", title: "Технологичность", text: "Генеративный ИИ, обученный на голосе вашего бренда, — тексты и медиа под конкретный бизнес, а не шаблоны." },
  { icon: "heart", title: "Забота о малом бизнесе", text: "Делаем маркетинг доступным там, где нет бюджета на агентство и штатного специалиста." },
  { icon: "shield", title: "Доверие и прозрачность", text: "Данные обрабатываются и хранятся в России, а вы всегда контролируете, что публикуется." },
];

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-12 sm:px-6 sm:py-16">
      <span className="kicker text-xs text-brand">О нас</span>
      <GradientScrollText
        as="h1"
        eager
        lines={["Маркетинг,", "который работает сам"]}
        className="mt-3 font-display text-3xl font-bold leading-tight tracking-tight sm:text-4xl lg:text-5xl"
      />
      <Reveal delay={0.05}>
        <p className="mt-4 text-lg leading-relaxed text-ink-muted">
          UCust — это ИИ-маркетолог для малого бизнеса. Мы помогаем кофейням, магазинам, салонам и локальным
          брендам вести соцсети и мессенджеры системно: планировать контент, генерировать посты и публиковать
          их в нужных каналах — без агентств и штатных специалистов.
        </p>
      </Reveal>

      <div className="mt-10 grid grid-cols-3 gap-3 sm:gap-4">
        {STATS.map((s) => (
          <div key={s.label} className="rounded-2xl border border-border bg-card p-4 text-center shadow-soft sm:p-5">
            <div className="font-display text-gradient text-2xl font-bold sm:text-3xl">{s.value}</div>
            <div className="mt-1 text-xs text-ink-muted sm:text-sm">{s.label}</div>
          </div>
        ))}
      </div>

      <section className="mt-12">
        <h2 className="text-xl font-bold text-ink sm:text-2xl">Наша миссия</h2>
        <p className="mt-3 text-[0.9375rem] leading-relaxed text-ink-muted">
          Мы верим, что качественный маркетинг не должен быть привилегией крупных компаний. Небольшой бизнес —
          основа живых городов, и ему нужен инструмент, который берёт рутину на себя: подсказывает, о чём писать,
          создаёт контент в голосе бренда и следит за регулярностью публикаций. Так предприниматель может
          заниматься своим делом, а не лентой.
        </p>
      </section>

      <section className="mt-12">
        <h2 className="text-xl font-bold text-ink sm:text-2xl">Что нам важно</h2>
        <div className="mt-5 flex flex-col gap-4">
          {VALUES.map(({ icon, title, text }, i) => (
            <Reveal
              key={title}
              delay={0.05 * i}
              className="flex gap-4 rounded-2xl border border-border bg-card p-5 shadow-soft transition-shadow duration-300 hover:shadow-lift"
            >
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-tint text-brand">
                <Icon name={icon} size={20} aria-hidden="true" />
              </span>
              <div>
                <h3 className="text-base font-bold text-ink">{title}</h3>
                <p className="mt-1 text-sm leading-relaxed text-ink-muted">{text}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="mt-12 rounded-[24px] border border-border bg-surface-soft p-6 sm:p-8">
        <h2 className="text-xl font-bold text-ink sm:text-2xl">Кто мы</h2>
        <p className="mt-3 text-[0.9375rem] leading-relaxed text-ink-muted">
          Сервис UCust развивает команда {LEGAL_COMPANY}. Мы объединяем разработку, дизайн и экспертизу в
          маркетинге, чтобы предприниматель получал результат, а не набор функций.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/#pricing" className="btn-glass-blue inline-flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold">
            Смотреть тарифы <Icon name="arrow-right" size={16} aria-hidden="true" />
          </Link>
          <Link href="/contacts" className="btn-glass inline-flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold">
            Связаться с нами
          </Link>
        </div>
      </section>
    </div>
  );
}
