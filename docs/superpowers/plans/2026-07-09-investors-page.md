# Investors Page (`/investors`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Отдельная страница `/investors` — краткий инвест-питч + форма-заглушка (mailto) + скачивание презентации; точка входа из футера.

**Architecture:** Данные питча в `lib/investors.ts`; страница по паттерну `app/about` (layout с шапкой+`AboutBackLink`+`Footer`, декларативный `page.tsx`); форма — отдельный client-компонент с `mailto`-отправкой (без бэкенда/секретов).

**Tech Stack:** Next.js 16 (App Router), React 19, Tailwind v4 (токены, `.dark`), framer-motion (`Reveal`), Solar-иконки `./ui/Icon`.

## Global Constraints

- Контент из стартап-питча, **без региональной привязки** (не упоминать Ростовскую область / региональные агентства/форумы по названию).
- Русский копирайт — verbatim из этого плана.
- Форма — **только `mailto`**, без бэкенда, внешних сервисов, ключей и секретов. Реальный контакт `ucust@yandex.ru` виден рядом.
- Цвета — только токены (`text-ink`, `text-ink-muted`, `bg-card`, `border-border`, `text-brand`, `text-gradient`, `bg-brand-tint`), без сырых hex.
- Иконки — только существующие в `lib/icons/solar.ts`: `file-text`, `trending`, `bar-chart`, `shield`, `sparkles`, `sparkles-bold`, `check-bold`, `calendar`, `mail-check`, `arrow-right`, `arrow-left`.
- Не деплоить. **Не запускать `npm run build` при работающем dev-сервере** (портит `.next`). Верификация — `npx tsc --noEmit` + Playwright визуал на dev.
- Git есть (ветка `investors-page`): коммит после каждой задачи. `git -c user.name="UCust" -c user.email="dev@ucust.online" commit`.
- Верификация (из `C:\Claude\UCust`): тип-чек `npx tsc --noEmit`; визуал — dev на `http://localhost:3000/investors` + Playwright.

---

## Task 1: Данные питча — `lib/investors.ts`

**Files:**
- Create: `lib/investors.ts`

**Interfaces:**
- Produces: именованные экспорты `INVESTOR_HERO`, `INVESTOR_PROBLEM`, `INVESTOR_SOLUTION`, `MARKET`, `METRICS`, `TECH`, `TEAM_TEXT`, `ROADMAP`, `INVESTOR_EMAIL` — читаются `app/investors/page.tsx`. Типы: `Stat = { value: string; label: string }`, `RoadmapStep = { period: string; text: string }`.

- [ ] **Step 1: Создать модуль данных**

```ts
// Контент страницы для инвесторов. Тезисы — из стартап-питча, без региональной привязки.
import type { IconName } from "@/lib/icons/solar";

export const INVESTOR_EMAIL = "ucust@yandex.ru";

export const INVESTOR_HERO = {
  kicker: "Инвесторам",
  title: "Автономный ИИ-маркетолог для малого бизнеса",
  subtitle:
    "Облачный сервис, который полностью берёт на себя маркетинг и соцсети предпринимателя. От 1 500 ₽ в месяц — в 10–20 раз дешевле штатного специалиста.",
};

export const INVESTOR_PROBLEM =
  "Владелец небольшого бизнеса — сам себе директор, продавец и маркетолог. Штатный маркетолог стоит 40–80 тыс. ₽ в месяц, агентство — до 100 тыс. Для микробизнеса это неподъёмно: 61% предпринимателей ведут маркетинг сами, больше половины не знают, что публиковать, а у 60% посты не приводят клиентов.";

export const INVESTOR_SOLUTION =
  "Предприниматель за пару минут заполняет короткую анкету о бизнесе — и дальше платформа работает сама: анализирует бизнес, строит контент-план на месяц вперёд, по одной фразе генерирует готовый пост с текстом и картинкой и сама публикует его в нужных соцсетях в удачное время. Контент учитывает отрасль и сезонность.";

export const MARKET: { value: string; label: string }[] = [
  { value: "1 569 млрд ₽", label: "рынок интернет-рекламы в России (×6 за 5 лет)" },
  { value: "189 млрд ₽", label: "реально достижимый сегмент (SAM)" },
  { value: "62%", label: "организаций уже работают с ИИ-агентами" },
];

export const METRICS: { value: string; label: string; icon: IconName }[] = [
  { value: "2", label: "свидетельства Роспатента на ПО (2026)", icon: "shield" },
  { value: "89%", label: "в CustDev готовы доверить маркетинг ИИ", icon: "check-bold" },
  { value: "3 300 ₽", label: "средний доход с клиента в месяц", icon: "trending" },
  { value: "до 80%", label: "валовая маржа (норма от 70%)", icon: "bar-chart" },
  { value: "3,47", label: "LTV/CAC к 2028 (стандарт — 3:1)", icon: "sparkles" },
  { value: "~3,5 мес", label: "окупаемость привлечения клиента", icon: "calendar" },
];

export const TECH: { title: string; text: string; icon: IconName }[] = [
  {
    title: "6 ИИ-агентов — как маркетинговая команда",
    text: "Анализ, стратегия, создание контента, публикация и самоулучшение — полный цикл идёт автономно, без участия человека. На российском рынке такого решения пока нет.",
    icon: "sparkles-bold",
  },
  {
    title: "Отечественный стек и данные в России",
    text: "Работаем только на российских моделях и храним данные в РФ по 152-ФЗ — это ещё и технологическая независимость.",
    icon: "shield",
  },
];

export const TEAM_TEXT =
  "Продукт создаёт команда полного цикла: продуктовая, ML- и full-stack-разработка, проджект-менеджмент и научное сопровождение. За плечами — запуск ИИ-продуктов, стажировки в IT-компаниях и победы на хакатонах. Мы умеем доводить продукт от идеи до рынка.";

export const ROADMAP: { period: string; text: string }[] = [
  { period: "Q3", text: "Запуск MVP" },
  { period: "Конец года", text: "Первые пилотные клиенты" },
  { period: "2027", text: "Коммерческий запуск, выход в сеть «Мой бизнес»" },
  { period: "2028", text: "Масштабирование и операционная прибыль" },
];
```

- [ ] **Step 2: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок (проверяет валидность `IconName` значений).

- [ ] **Step 3: Commit**

```bash
git add lib/investors.ts
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(investors): pitch content module"
```

---

## Task 2: Каркас страницы + ассет презентации

**Files:**
- Create: `app/investors/layout.tsx`
- Create: `app/investors/page.tsx` (скелет: Hero + кнопки; секции добавит Task 3)
- Create (asset): `public/UCast_prezentaciya.pptx`

**Interfaces:**
- Consumes: `INVESTOR_HERO` из `lib/investors.ts`; `Footer`, `AboutBackLink`, `Icon`, `Reveal`.
- Produces: маршрут `/investors`; `page.tsx` экспортирует `default` компонент (Task 3 дополнит его секциями между Hero и закрывающим тегом).

- [ ] **Step 1: Скопировать презентацию в public**

```bash
cp "C:/Claude/Presentation Startup/UCast_Startup_v2.pptx" public/UCast_prezentaciya.pptx
ls -la public/UCast_prezentaciya.pptx
```
Expected: файл ~30 МБ на месте. (Утяжеляет репозиторий — временно, потом заменится на PDF.)

- [ ] **Step 2: Создать layout (по образцу `app/about/layout.tsx`)**

```tsx
import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import Image from "next/image";
import Footer from "@/components/Footer";
import AboutBackLink from "@/components/AboutBackLink";

export const metadata: Metadata = {
  title: "Инвесторам — UCust",
  description:
    "UCust — автономный ИИ-маркетолог для малого бизнеса. Рынок, метрики, технология и контакт для инвесторов и партнёров.",
};

export default function InvestorsLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-dvh flex-col bg-canvas">
      <header className="bg-canvas pt-3">
        <div className="mx-auto max-w-(--container-page) px-5 sm:px-6">
          <div className="flex h-14 items-center justify-between rounded-[24px] border border-white/10 bg-card/80 px-5 shadow-soft ring-1 ring-white/5 backdrop-blur-xl sm:px-6">
            <Link href="/" aria-label="UCust — на главную" className="inline-flex items-center">
              <Image src="/logo-wordmark.webp" alt="UCust" width={700} height={161} unoptimized className="h-6 w-auto sm:h-7 dark:hidden" />
              <Image src="/brand/logo-lighttext.webp" alt="UCust" width={700} height={161} unoptimized className="hidden h-6 w-auto sm:h-7 dark:block" />
            </Link>
            <AboutBackLink />
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
```

- [ ] **Step 3: Создать page.tsx (скелет с Hero и двумя кнопками)**

```tsx
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import Reveal from "@/components/Reveal";
import { INVESTOR_HERO } from "@/lib/investors";

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

      {/* Task 3 вставит секции здесь */}
      {/* Task 4 вставит блок #contact здесь */}
    </div>
  );
}
```

> Примечание для Task 3/4: секции и блок `#contact` добавляются **внутри** корневого `<div>`, после Hero-блока, перед закрывающим `</div>`.

- [ ] **Step 4: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 5: Визуальная проверка**

Dev-сервер работает. Playwright: открыть `http://localhost:3000/investors`, скриншот. Подтвердить: шапка с логотипом + «На главную», Hero-заголовок и подзаголовок, две кнопки. Кликнуть «Скачать презентацию» — проверить, что ссылка ведёт на `/UCast_prezentaciya.pptx` (проверить `href` через evaluate; фактическую загрузку 30 МБ не тянуть).

- [ ] **Step 6: Commit**

```bash
git add app/investors/layout.tsx app/investors/page.tsx public/UCast_prezentaciya.pptx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(investors): page shell, layout, deck asset"
```

---

## Task 3: Контент-секции страницы

**Files:**
- Modify: `app/investors/page.tsx` (добавить секции + расширить импорты)

**Interfaces:**
- Consumes: `INVESTOR_PROBLEM`, `INVESTOR_SOLUTION`, `MARKET`, `METRICS`, `TECH`, `TEAM_TEXT`, `ROADMAP` из `lib/investors.ts`.
- Produces: полностью свёрстанную страницу (кроме блока `#contact` из Task 4).

- [ ] **Step 1: Расширить импорты в `page.tsx`**

Заменить строку `import { INVESTOR_HERO } from "@/lib/investors";` на:

```tsx
import {
  INVESTOR_HERO,
  INVESTOR_PROBLEM,
  INVESTOR_SOLUTION,
  MARKET,
  METRICS,
  TECH,
  TEAM_TEXT,
  ROADMAP,
} from "@/lib/investors";
```

- [ ] **Step 2: Вставить секции**

Заменить комментарий `{/* Task 3 вставит секции здесь */}` на блок ниже (единый дизайн-язык: `mt-14/16`, заголовки `text-xl font-bold sm:text-2xl`, карточки `rounded-2xl border border-border bg-card`):

```tsx
      {/* Проблема и решение */}
      <div className="mt-16 grid gap-6 md:grid-cols-2">
        <Reveal className="rounded-[24px] border border-border bg-card p-6 shadow-soft sm:p-7">
          <h2 className="text-xl font-bold text-ink sm:text-2xl">Проблема</h2>
          <p className="mt-3 text-[15px] leading-relaxed text-ink-muted">{INVESTOR_PROBLEM}</p>
        </Reveal>
        <Reveal delay={0.05} className="rounded-[24px] border border-brand/30 bg-brand-tint/40 p-6 shadow-soft sm:p-7">
          <h2 className="text-xl font-bold text-ink sm:text-2xl">Решение</h2>
          <p className="mt-3 text-[15px] leading-relaxed text-ink-muted">{INVESTOR_SOLUTION}</p>
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
        <p className="mt-3 max-w-3xl text-[15px] leading-relaxed text-ink-muted">{TEAM_TEXT}</p>
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
```

- [ ] **Step 3: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 4: Визуальная проверка**

Playwright: `http://localhost:3000/investors`, скриншот full-page на 1440 и 375. Подтвердить: все секции читаемы, сетки метрик/рынка/roadmap ровные, тексты не растянуты, тёмная тема ок (переключить). Нет горизонтального скролла.

- [ ] **Step 5: Commit**

```bash
git add app/investors/page.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(investors): content sections (problem, market, metrics, tech, team, roadmap)"
```

---

## Task 4: Форма контакта (mailto) + блок `#contact`

**Files:**
- Create: `components/investors/InvestorContactForm.tsx`
- Modify: `app/investors/page.tsx` (импорт + блок `#contact`)

**Interfaces:**
- Consumes: `INVESTOR_EMAIL` из `lib/investors.ts`; `Icon`.
- Produces: `InvestorContactForm` (client, без пропсов) — рендерится в блоке `#contact`.

- [ ] **Step 1: Создать форму (client, mailto-отправка)**

`components/investors/InvestorContactForm.tsx`:

```tsx
"use client";

import { useState } from "react";
import Icon from "@/components/ui/Icon";
import { INVESTOR_EMAIL } from "@/lib/investors";

const inputCls =
  "rounded-2xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card";

const isEmail = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);

// Пока без бэкенда: собираем письмо и открываем почтовый клиент пользователя.
// Позже заменить тело функции на серверный POST — UI менять не нужно.
function submitLead(data: { name: string; email: string; message: string }) {
  const subject = encodeURIComponent("Инвестиции — UCust");
  const body = encodeURIComponent(
    `Имя: ${data.name}\nEmail: ${data.email}\n\n${data.message}`,
  );
  window.location.href = `mailto:${INVESTOR_EMAIL}?subject=${subject}&body=${body}`;
}

export default function InvestorContactForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [emailError, setEmailError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isEmail(email)) {
      setEmailError("Проверьте адрес почты");
      return;
    }
    setEmailError(null);
    submitLead({ name, email, message });
    setSent(true);
  };

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-medium text-ink">Имя</span>
        <input
          type="text"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Как к вам обращаться"
          className={inputCls}
        />
      </label>

      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-medium text-ink">Email</span>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onBlur={() => setEmailError(email && !isEmail(email) ? "Проверьте адрес почты" : null)}
          placeholder="you@example.com"
          aria-invalid={Boolean(emailError)}
          className={inputCls}
        />
        {emailError && (
          <span className="text-xs text-[color:var(--error,#e5484d)]" role="alert">
            {emailError}
          </span>
        )}
      </label>

      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-medium text-ink">Сообщение</span>
        <textarea
          required
          rows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Коротко о вашем интересе"
          className={`${inputCls} resize-y`}
        />
      </label>

      <button
        type="submit"
        className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold"
      >
        Отправить <Icon name="arrow-right" size={16} aria-hidden="true" />
      </button>

      <p className="text-xs leading-relaxed text-ink-muted" aria-live="polite">
        {sent
          ? "Откроется ваш почтовый клиент с готовым письмом. Если он не открылся — напишите нам напрямую."
          : "Кнопка откроет ваш почтовый клиент с заполненным письмом."}
      </p>
    </form>
  );
}
```

> Примечание: `--error` может отсутствовать в токенах — fallback `#e5484d` в `var(--error,#e5484d)` покрывает это.

- [ ] **Step 2: Добавить блок `#contact` в `page.tsx`**

В `app/investors/page.tsx` добавить импорт (рядом с другими):

```tsx
import InvestorContactForm from "@/components/investors/InvestorContactForm";
import { INVESTOR_EMAIL } from "@/lib/investors";
```

(Если `INVESTOR_EMAIL` уже импортирован — не дублировать; добавить его в существующий импорт из `@/lib/investors`.)

Заменить комментарий `{/* Task 4 вставит блок #contact здесь */}` на:

```tsx
      {/* Контакт */}
      <section id="contact" className="mt-16 scroll-mt-24 rounded-[28px] border border-border bg-card p-6 shadow-soft sm:p-8">
        <div className="grid gap-8 md:grid-cols-2 md:items-start">
          <div>
            <span className="kicker text-xs text-brand">Контакт</span>
            <h2 className="mt-2 text-2xl font-bold text-ink sm:text-3xl">Открыты к диалогу</h2>
            <p className="mt-3 text-[15px] leading-relaxed text-ink-muted">
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
```

- [ ] **Step 3: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 4: Визуальная + функциональная проверка**

Playwright: `http://localhost:3000/investors`, скролл к `#contact`. Подтвердить: форма и прямой email видны. Заполнить поля через `browser_evaluate`/type; ввести некорректный email → submit → видна ошибка «Проверьте адрес почты». Исправить → submit: проверить, что формируется `mailto:ucust@yandex.ru?subject=...&body=...` (перехватить через evaluate на `window.location.href` перед переходом, или проверить сборку строки). Кнопка «Связаться» в Hero скроллит к `#contact`.

- [ ] **Step 5: Commit**

```bash
git add components/investors/InvestorContactForm.tsx app/investors/page.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(investors): mailto contact form + contact block"
```

---

## Task 5: Точка входа — футер «Вопросы» → «Инвесторам»

**Files:**
- Modify: `components/Footer.tsx` (COLUMNS → «Компания»)

**Interfaces:**
- Consumes: ничего нового.
- Produces: ссылка `/investors` в футере.

- [ ] **Step 1: Заменить пункт в колонке «Компания»**

В `components/Footer.tsx`, в массиве `COLUMNS` → объект `title: "Компания"`, заменить:

```tsx
      { label: "Вопросы", href: "/#faq" },
```

на:

```tsx
      { label: "Инвесторам", href: "/investors" },
```

(Остальные пункты — «О нас», «Контакты» — не трогать. Навбар и секцию FAQ не трогать.)

- [ ] **Step 2: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 3: Визуальная проверка**

Playwright: `http://localhost:3000`, скролл к футеру. Подтвердить: в колонке «Компания» пункт «Инвесторам», клик ведёт на `/investors`. FAQ по-прежнему открывается из навбара («Вопросы»).

- [ ] **Step 4: Commit**

```bash
git add components/Footer.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(investors): footer entry point (Вопросы -> Инвесторам)"
```

---

## Финальная верификация (после всех задач)

- [ ] `npx tsc --noEmit` — чисто.
- [ ] Playwright обход `/investors` (светлая/тёмная, 1440 и 375): Hero, все секции, roadmap, форма, скачивание, прямой email; нет горизонтального скролла.
- [ ] Футер `/` → «Инвесторам» ведёт на `/investors`; FAQ работает из навбара.
- [ ] Форма: неверный email → ошибка; верный → корректный `mailto`.
- [ ] Не деплоить. Не запускать `npm run build` при активном dev-сервере.
