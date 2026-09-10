import Icon from "@/components/ui/Icon";
import Reveal from "@/components/Reveal";
import {
  INVESTOR_HERO,
  INVESTOR_PROBLEM,
  INVESTOR_SOLUTION,
  MARKET,
  METRICS,
  TECH,
  TEAM_TEXT,
  ROADMAP,
  INVESTOR_EMAIL,
} from "@/lib/investors";
import InvestorContactForm from "@/components/investors/InvestorContactForm";

export default function InvestorsPage() {
  return (
    <div className="mx-auto max-w-5xl px-5 py-12 sm:px-6 sm:py-16">
      {/* Hero */}
      <span className="kicker text-xs text-brand">{INVESTOR_HERO.kicker}</span>
      <Reveal>
        <h1 className="mt-3 font-display text-3xl font-bold leading-tight tracking-tight text-ink sm:text-4xl lg:text-5xl">
          {INVESTOR_HERO.title}
        </h1>
      </Reveal>
      <Reveal delay={0.05}>
        <p className="mt-4 max-w-2xl text-lg leading-relaxed text-ink-muted">
          {INVESTOR_HERO.subtitle}
        </p>
      </Reveal>
      <Reveal delay={0.1}>
        <div className="mt-8 flex flex-wrap gap-3">
          <a href="#contact" className="btn-glass-blue inline-flex items-center gap-2 rounded-xl px-6 py-3.5 text-sm font-semibold">
            Связаться <Icon name="arrow-right" size={16} aria-hidden="true" />
          </a>
          <a
            href="/UCast_prezentaciya.pptx"
            download
            className="btn-glass inline-flex items-center gap-2 rounded-xl px-6 py-3.5 text-sm font-semibold"
          >
            <Icon name="file-text" size={16} aria-hidden="true" /> Скачать презентацию
          </a>
        </div>
      </Reveal>

      {/* Проблема и решение */}
      <div className="mt-16 grid gap-6 md:grid-cols-2">
        <Reveal className="rounded-[24px] border border-border bg-card p-6 shadow-soft sm:p-7">
          <h2 className="text-xl font-bold text-ink sm:text-2xl">Проблема</h2>
          <p className="mt-3 text-[0.9375rem] leading-relaxed text-ink-muted">{INVESTOR_PROBLEM}</p>
        </Reveal>
        <Reveal delay={0.05} className="rounded-[24px] border border-brand/30 bg-brand-tint/40 p-6 shadow-soft sm:p-7">
          <h2 className="text-xl font-bold text-ink sm:text-2xl">Решение</h2>
          <p className="mt-3 text-[0.9375rem] leading-relaxed text-ink-muted">{INVESTOR_SOLUTION}</p>
        </Reveal>
      </div>

      {/* Рынок */}
      <section className="mt-16">
        <span className="kicker text-xs text-brand">Рынок</span>
        <h2 className="mt-2 text-2xl font-bold text-ink sm:text-3xl">Ёмкий и быстрорастущий</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {MARKET.map((m) => (
            <div key={m.label} className="rounded-2xl border border-border bg-card p-5 text-center shadow-soft">
              <div className="font-display text-gradient text-2xl font-extrabold sm:text-3xl">{m.value}</div>
              <div className="mt-1.5 text-sm text-ink-muted">{m.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Метрики / тяга */}
      <section className="mt-16">
        <span className="kicker text-xs text-brand">Показатели</span>
        <h2 className="mt-2 text-2xl font-bold text-ink sm:text-3xl">Не идея на бумаге</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {METRICS.map((m) => (
            <Reveal key={m.label} className="flex items-start gap-3 rounded-2xl border border-border bg-card p-5 shadow-soft transition-shadow duration-300 hover:shadow-lift">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-tint text-brand">
                <Icon name={m.icon} size={18} aria-hidden="true" />
              </span>
              <div>
                <div className="font-display text-xl font-extrabold text-ink">{m.value}</div>
                <div className="mt-0.5 text-sm leading-snug text-ink-muted">{m.label}</div>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* Технология-барьер */}
      <section className="mt-16">
        <span className="kicker text-xs text-brand">Технология</span>
        <h2 className="mt-2 text-2xl font-bold text-ink sm:text-3xl">Почему именно мы</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {TECH.map(({ title, text, icon }) => (
            <Reveal key={title} className="rounded-2xl border border-border bg-card p-6 shadow-soft">
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-tint text-brand">
                <Icon name={icon} size={20} aria-hidden="true" />
              </span>
              <h3 className="mt-4 text-base font-bold text-ink">{title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">{text}</p>
            </Reveal>
          ))}
        </div>
      </section>

      {/* Команда */}
      <section className="mt-16 rounded-[24px] border border-border bg-surface-soft p-6 sm:p-8">
        <h2 className="text-xl font-bold text-ink sm:text-2xl">Команда</h2>
        <p className="mt-3 max-w-3xl text-[0.9375rem] leading-relaxed text-ink-muted">{TEAM_TEXT}</p>
      </section>

      {/* Roadmap */}
      <section className="mt-16">
        <span className="kicker text-xs text-brand">Дорожная карта</span>
        <h2 className="mt-2 text-2xl font-bold text-ink sm:text-3xl">Куда идём</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {ROADMAP.map((r) => (
            <div key={r.period} className="rounded-2xl border border-border bg-card p-5 shadow-soft">
              <div className="inline-flex items-center gap-1.5 rounded-full bg-brand-tint px-2.5 py-1 text-xs font-semibold text-brand">
                <Icon name="calendar" size={12} aria-hidden="true" /> {r.period}
              </div>
              <p className="mt-2.5 text-sm leading-snug text-ink">{r.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Контакт */}
      <section id="contact" className="mt-16 scroll-mt-24 rounded-[28px] border border-border bg-card p-6 shadow-soft sm:p-8">
        <div className="grid gap-8 md:grid-cols-2 md:items-start">
          <div>
            <span className="kicker text-xs text-brand">Контакт</span>
            <h2 className="mt-2 text-2xl font-bold text-ink sm:text-3xl">Открыты к диалогу</h2>
            <p className="mt-3 text-[0.9375rem] leading-relaxed text-ink-muted">
              Ищем инвесторов и партнёров для масштабирования. Напишите — расскажем о продукте,
              экономике и планах подробнее.
            </p>
            <a
              href={`mailto:${INVESTOR_EMAIL}`}
              className="mt-5 inline-flex items-center gap-2 text-base font-semibold text-ink transition-colors hover:text-brand"
            >
              <Icon name="mail-check" size={18} aria-hidden="true" /> {INVESTOR_EMAIL}
            </a>
          </div>
          <InvestorContactForm />
        </div>
      </section>
    </div>
  );
}
