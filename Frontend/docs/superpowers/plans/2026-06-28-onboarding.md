# Онбординг проекта — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Построить флоу онбординга ЮКаст: визард сбора данных → экран анализа → превью бренд-профиля (5 разделов) → заглушка дашборда, адаптированный под дизайн-систему сайта.

**Architecture:** Подход A — клиентский state-machine для визарда на `/onboarding`, ревью отдельным роутом `/onboarding/review`. Чистый слой данных `lib/onboarding/` (типы + `analyzeBusiness()`-заглушка с нишевыми пресетами), состояние в `OnboardingProvider` с персистом в sessionStorage. Гибрид: моки сейчас, подмена на API позже — только в теле `analyzeBusiness`.

**Tech Stack:** Next.js 16 (App Router, Turbopack), React 19, Tailwind v4 (токены тем), framer-motion, lucide-react. TypeScript.

## Global Constraints

- **Next.js 16** — это НЕ привычный Next; при сомнениях смотреть `node_modules/next/dist/docs/`. App Router, серверные компоненты по умолчанию; интерактивные — `"use client"`.
- **Темы:** class-based dark (`@custom-variant dark`), наследуется от корневого `app/layout.tsx`. Использовать только токены: `bg-card`, `bg-surface-soft`, `text-ink`, `text-ink-muted`, `border-border`, `text-brand`, `bg-brand`, `brand-tint`, палитра `brand-purple/brand-pink/brand-orange/success`. **Никаких тёмных блоков-«плашек»** — только токены палитры.
- **Кнопки:** существующие классы `.btn-glass` (нейтральная), `.btn-glass-blue` (синяя CTA), `.btn-glass-dark` (на синем фоне). Не изобретать новые.
- **Шрифт:** Manrope (`font-display`/`font-body` уже подключены глобально).
- **Скругления:** карточки `rounded-[24px]`/`rounded-[32px]`, поля/кнопки `rounded-xl`.
- **Анимации:** уважать `prefers-reduced-motion` через `mounted`-паттерн (как в `components/Channels.tsx`), НЕ ветвить разметку по `useReducedMotion` до монтирования (hydration mismatch).
- **Проект не под git:** «коммиты» = чекпойнты (проверка), без `git commit`.
- **Проверка задачи:** `npx tsc --noEmit` (0 ошибок) + `npm run lint` (0 ошибок) + при наличии UI — dev-сервер компилит без ошибок + визуальная проверка Playwright (light+dark).
- **Язык интерфейса:** русский. Тексты-копи брать дословно из этого плана.

---

## Файловая структура

```
lib/onboarding/types.ts          — типы WizardInput, BrandProfile + под-типы
lib/onboarding/presets.ts        — нишевые пресеты + pickPreset()
lib/onboarding/mock.ts           — analyzeBusiness(input): Promise<BrandProfile>
lib/onboarding/storage.ts        — load/save/clear sessionStorage

components/onboarding/OnboardingProvider.tsx   — контекст + персист + useOnboarding()
components/onboarding/OnboardingTopBar.tsx
components/onboarding/ProgressSteps.tsx
components/onboarding/Field.tsx                — label + input/textarea
components/onboarding/Chip.tsx                 — цветной чип
components/onboarding/WizardFlow.tsx           — оркестратор шагов + анализа
components/onboarding/steps/StepBusinessName.tsx
components/onboarding/steps/StepAbout.tsx
components/onboarding/steps/StepChannels.tsx
components/onboarding/AnalysisScreen.tsx
components/onboarding/review/ProfileSidebar.tsx
components/onboarding/review/ReviewFlow.tsx
components/onboarding/review/SectionAbout.tsx
components/onboarding/review/SectionMarket.tsx
components/onboarding/review/SectionSwot.tsx
components/onboarding/review/SectionServices.tsx
components/onboarding/review/SectionGoals.tsx

app/onboarding/layout.tsx        — OnboardingProvider + каркас
app/onboarding/page.tsx          — <WizardFlow/>
app/onboarding/review/page.tsx   — <ReviewFlow/>
app/verify-email/page.tsx
app/dashboard/page.tsx
components/SignupModal.tsx        — MODIFY: после сабмита router.push('/verify-email')
```

---

## Task 1: Слой данных — типы

**Files:**
- Create: `lib/onboarding/types.ts`

**Interfaces:**
- Produces: типы `AboutMode`, `SocialId`, `WizardInput`, `MarketInfo`, `SwotInfo`, `ServiceItem`, `BrandProfile`.

- [ ] **Step 1: Создать типы**

```ts
// lib/onboarding/types.ts
export type AboutMode = "link" | "manual";
export type SocialId = "instagram" | "vk" | "telegram" | "facebook";

export interface WizardInput {
  name: string;
  description: string;
  aboutMode: AboutMode;
  link: string;
  activity: string;
  difference: string;
  socials: SocialId[];
  files: string[];
}

export interface MarketInfo {
  competitors: string[];
  geography: string;
  segment: string;
  trends: string[];
}

export interface SwotInfo {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface ServiceItem {
  title: string;
  items: string;
}

export interface BrandProfile {
  name: string;
  field: string;
  positioning: string;
  market: MarketInfo;
  swot: SwotInfo;
  services: ServiceItem[];
  goals: string[];
  tone: string[];
}

export const EMPTY_INPUT: WizardInput = {
  name: "",
  description: "",
  aboutMode: "link",
  link: "",
  activity: "",
  difference: "",
  socials: [],
  files: [],
};
```

- [ ] **Step 2: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 2: Слой данных — нишевые пресеты

**Files:**
- Create: `lib/onboarding/presets.ts`

**Interfaces:**
- Consumes: типы из Task 1.
- Produces: `pickPreset(text: string): PresetProfile`, где `PresetProfile = Omit<BrandProfile, "name">`.

- [ ] **Step 1: Создать пресеты**

```ts
// lib/onboarding/presets.ts
import type { BrandProfile } from "./types";

export type PresetProfile = Omit<BrandProfile, "name">;

interface Preset {
  keywords: string[];
  profile: PresetProfile;
}

const coffee: PresetProfile = {
  field: "Кофейня — спешелти-кофе и свежая выпечка",
  positioning: "Уютная городская кофейня с авторскими напитками и зерном собственной обжарки",
  market: {
    competitors: ["Surf Coffee", "Cofix", "Skuratov Coffee"],
    geography: "Россия, Ростов-на-Дону",
    segment: "Жители района, офисные сотрудники, студенты, любители кофе",
    trends: [
      "Рост спроса на спешелти-кофе и альтернативные напитки",
      "Популярность кофе навынос и завтраков",
      "Гости выбирают атмосферные локальные кофейни",
    ],
  },
  swot: {
    strengths: ["Авторские напитки и своя обжарка", "Уютная атмосфера", "Удобная локация в центре"],
    weaknesses: ["Высокая конкуренция рядом", "Зависимость от потока в часы пик"],
    opportunities: ["Доставка и кофе навынос", "Завтраки и бизнес-ланчи", "Программа лояльности"],
    threats: ["Сетевые кофейни поблизости", "Рост цен на зерно"],
  },
  services: [
    { title: "Спешелти-кофе", items: "Эспрессо, капучино, раф, фильтр" },
    { title: "Свежая выпечка", items: "Круассаны, синнабоны, чизкейки" },
    { title: "Завтраки", items: "Сырники, гранола, тосты" },
  ],
  goals: [
    "Увеличить узнаваемость кофейни в районе",
    "Привлечь новых гостей и подписчиков",
    "Повысить средний чек через сезонное меню",
  ],
  tone: ["Дружелюбный", "Тёплый", "С заботой"],
};

const beauty: PresetProfile = {
  field: "Салон красоты — уход и эстетические услуги",
  positioning: "Современный салон красоты с индивидуальным подходом и премиальным сервисом",
  market: {
    competitors: ["Чёрный Жемчуг", "Persona", "Локальные мастера"],
    geography: "Россия, Москва",
    segment: "Женщины 20–45 лет, заботящиеся о внешности, жители района",
    trends: [
      "Спрос на натуральный уход и безопасные процедуры",
      "Рост записи через соцсети и мессенджеры",
      "Клиенты ценят атмосферу и персональный подход",
    ],
  },
  swot: {
    strengths: ["Опытные мастера", "Уютная атмосфера", "Качественные материалы"],
    weaknesses: ["Высокая конкуренция", "Зависимость от конкретных мастеров"],
    opportunities: ["Абонементы и программы лояльности", "Новые услуги и комплексы", "Партнёрства с брендами"],
    threats: ["Демпинг частных мастеров", "Рост цен на материалы"],
  },
  services: [
    { title: "Парикмахерские услуги", items: "Стрижки, окрашивание, укладки" },
    { title: "Ногтевой сервис", items: "Маникюр, педикюр, дизайн" },
    { title: "Уход за лицом", items: "Чистки, массаж, уходовые процедуры" },
  ],
  goals: [
    "Увеличить количество постоянных клиентов",
    "Привлечь новых клиентов через соцсети",
    "Повысить средний чек на комплексных услугах",
  ],
  tone: ["Дружелюбный", "Элегантный", "С заботой"],
};

const retail: PresetProfile = {
  field: "Розничный магазин — товары для покупателей",
  positioning: "Магазин с продуманным ассортиментом и удобным сервисом для покупателей",
  market: {
    competitors: ["Маркетплейсы", "Сетевые магазины", "Локальные точки"],
    geography: "Россия",
    segment: "Покупатели района и онлайн-аудитория, ценящие удобство и качество",
    trends: [
      "Рост онлайн-заказов и доставки",
      "Покупатели ищут локальные альтернативы маркетплейсам",
      "Важность отзывов и визуального контента",
    ],
  },
  swot: {
    strengths: ["Удобный ассортимент", "Личный сервис", "Гибкость к запросам"],
    weaknesses: ["Конкуренция с маркетплейсами", "Ограниченный охват"],
    opportunities: ["Онлайн-витрина и доставка", "Акции и распродажи", "Программа лояльности"],
    threats: ["Демпинг маркетплейсов", "Сезонность спроса"],
  },
  services: [
    { title: "Основной ассортимент", items: "Ключевые товары и новинки" },
    { title: "Доставка", items: "Самовывоз и доставка по городу" },
    { title: "Акции", items: "Сезонные скидки и спецпредложения" },
  ],
  goals: [
    "Увеличить продажи и средний чек",
    "Привлечь новых покупателей онлайн",
    "Повысить узнаваемость бренда",
  ],
  tone: ["Дружелюбный", "Понятный", "Полезный"],
};

const services: PresetProfile = {
  field: "Услуги — сервис для клиентов и бизнеса",
  positioning: "Надёжный сервис с экспертным подходом и понятным результатом для клиента",
  market: {
    competitors: ["Профильные агентства", "Фрилансеры", "Сетевые компании"],
    geography: "Россия",
    segment: "Малый и средний бизнес, частные клиенты, которым важны результат и надёжность",
    trends: [
      "Спрос на прозрачность и понятный результат",
      "Рост обращений через соцсети и рекомендации",
      "Клиенты выбирают экспертов с кейсами",
    ],
  },
  swot: {
    strengths: ["Экспертиза и опыт", "Индивидуальный подход", "Понятные кейсы"],
    weaknesses: ["Зависимость от ключевых специалистов", "Высокая конкуренция"],
    opportunities: ["Пакетные предложения", "Контент с экспертизой", "Партнёрства"],
    threats: ["Демпинг конкурентов", "Сезонность спроса"],
  },
  services: [
    { title: "Основная услуга", items: "Ключевое направление работы" },
    { title: "Консультации", items: "Разбор задачи и рекомендации" },
    { title: "Сопровождение", items: "Поддержка и доработки" },
  ],
  goals: [
    "Привлечь новых клиентов",
    "Повысить доверие через экспертный контент",
    "Увеличить повторные обращения",
  ],
  tone: ["Экспертный", "Понятный", "Надёжный"],
};

const fallback: PresetProfile = {
  field: "Бизнес — продукты и услуги для клиентов",
  positioning: "Бизнес с фокусом на качество и заботу о клиентах",
  market: {
    competitors: ["Прямые конкуренты", "Сетевые игроки", "Локальные альтернативы"],
    geography: "Россия",
    segment: "Целевая аудитория района и онлайн, ценящая качество и сервис",
    trends: [
      "Рост роли соцсетей в выборе бизнеса",
      "Спрос на регулярный и полезный контент",
      "Клиенты ценят локальные бренды",
    ],
  },
  swot: {
    strengths: ["Качество продукта", "Внимание к клиенту", "Гибкость"],
    weaknesses: ["Узнаваемость бренда", "Конкуренция"],
    opportunities: ["Развитие соцсетей", "Новые продукты", "Программа лояльности"],
    threats: ["Усиление конкурентов", "Изменение спроса"],
  },
  services: [
    { title: "Продукты", items: "Основное предложение" },
    { title: "Сервис", items: "Поддержка и доставка" },
    { title: "Спецпредложения", items: "Акции и новинки" },
  ],
  goals: [
    "Увеличить узнаваемость бренда",
    "Привлечь новых клиентов и подписчиков",
    "Повысить продажи через контент",
  ],
  tone: ["Дружелюбный", "Понятный", "С заботой"],
};

const PRESETS: Preset[] = [
  { keywords: ["кофе", "кофейн", "кафе", "бариста", "эспрессо", "капучино", "выпечк"], profile: coffee },
  { keywords: ["салон", "красот", "маникюр", "барбершоп", "парикмахер", "ногт", "космето"], profile: beauty },
  { keywords: ["магазин", "товар", "продаж", "шоурум", "ритейл", "ассортимент"], profile: retail },
  { keywords: ["услуг", "юрид", "консалт", "агентств", "ремонт", "сервис", "студи"], profile: services },
];

export function pickPreset(text: string): PresetProfile {
  const t = text.toLowerCase();
  for (const p of PRESETS) {
    if (p.keywords.some((k) => t.includes(k))) return p.profile;
  }
  return fallback;
}
```

- [ ] **Step 2: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 3: Слой данных — mock analyze + storage

**Files:**
- Create: `lib/onboarding/mock.ts`, `lib/onboarding/storage.ts`

**Interfaces:**
- Consumes: типы Task 1, `pickPreset` Task 2.
- Produces: `analyzeBusiness(input: WizardInput): Promise<BrandProfile>`; `loadOnboarding(): OnboardingState | null`, `saveOnboarding(state: OnboardingState): void`, `clearOnboarding(): void`, тип `OnboardingState`.

- [ ] **Step 1: mock.ts**

```ts
// lib/onboarding/mock.ts
import type { BrandProfile, WizardInput } from "./types";
import { pickPreset } from "./presets";

/**
 * Заглушка анализа бизнеса. Имитирует задержку и собирает профиль из нишевого
 * пресета, подставляя введённое название. ПОЗЖЕ заменяется на реальный fetch к API —
 * меняется только тело этой функции, сигнатура остаётся.
 */
export function analyzeBusiness(input: WizardInput): Promise<BrandProfile> {
  const text = [input.name, input.description, input.activity, input.difference, input.link].join(" ");
  const preset = pickPreset(text);
  const name = input.name.trim() || "Ваш бизнес";
  return new Promise((resolve) => {
    setTimeout(() => resolve({ name, ...preset }), 2500);
  });
}
```

- [ ] **Step 2: storage.ts**

```ts
// lib/onboarding/storage.ts
import type { BrandProfile, WizardInput } from "./types";

export interface OnboardingState {
  input: WizardInput;
  profile: BrandProfile | null;
}

const KEY = "ucust:onboarding";

export function loadOnboarding(): OnboardingState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as OnboardingState) : null;
  } catch {
    return null;
  }
}

export function saveOnboarding(state: OnboardingState): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* sessionStorage недоступен — игнорируем */
  }
}

export function clearOnboarding(): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.removeItem(KEY);
  } catch {
    /* ignore */
  }
}
```

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 4: OnboardingProvider (контекст + персист)

**Files:**
- Create: `components/onboarding/OnboardingProvider.tsx`

**Interfaces:**
- Consumes: типы Task 1, `analyzeBusiness` Task 3, storage Task 3.
- Produces: `OnboardingProvider` (компонент), `useOnboarding()` → `{ input, profile, updateInput, runAnalysis, resetAll }`.
  - `updateInput(patch: Partial<WizardInput>): void`
  - `runAnalysis(): Promise<void>` (вызывает analyzeBusiness, сохраняет profile)
  - `resetAll(): void`

- [ ] **Step 1: Создать провайдер**

```tsx
// components/onboarding/OnboardingProvider.tsx
"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import type { BrandProfile, WizardInput } from "@/lib/onboarding/types";
import { EMPTY_INPUT } from "@/lib/onboarding/types";
import { analyzeBusiness } from "@/lib/onboarding/mock";
import { clearOnboarding, loadOnboarding, saveOnboarding } from "@/lib/onboarding/storage";

interface Ctx {
  input: WizardInput;
  profile: BrandProfile | null;
  updateInput: (patch: Partial<WizardInput>) => void;
  runAnalysis: () => Promise<void>;
  resetAll: () => void;
}

const OnboardingContext = createContext<Ctx | null>(null);

export function OnboardingProvider({ children }: { children: ReactNode }) {
  const [input, setInput] = useState<WizardInput>(EMPTY_INPUT);
  const [profile, setProfile] = useState<BrandProfile | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Восстанавливаем состояние из sessionStorage после монтирования.
  useEffect(() => {
    const saved = loadOnboarding();
    if (saved) {
      setInput(saved.input);
      setProfile(saved.profile);
    }
    setHydrated(true);
  }, []);

  // Персистим при изменениях (только после гидрации, чтобы не затереть сохранённое).
  useEffect(() => {
    if (hydrated) saveOnboarding({ input, profile });
  }, [hydrated, input, profile]);

  const updateInput = useCallback((patch: Partial<WizardInput>) => {
    setInput((prev) => ({ ...prev, ...patch }));
  }, []);

  const runAnalysis = useCallback(async () => {
    const result = await analyzeBusiness(input);
    setProfile(result);
  }, [input]);

  const resetAll = useCallback(() => {
    setInput(EMPTY_INPUT);
    setProfile(null);
    clearOnboarding();
  }, []);

  return (
    <OnboardingContext.Provider value={{ input, profile, updateInput, runAnalysis, resetAll }}>
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding(): Ctx {
  const ctx = useContext(OnboardingContext);
  if (!ctx) throw new Error("useOnboarding must be used within OnboardingProvider");
  return ctx;
}
```

- [ ] **Step 2: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 5: Каркас онбординга — layout + топ-бар + прогресс

**Files:**
- Create: `app/onboarding/layout.tsx`, `components/onboarding/OnboardingTopBar.tsx`, `components/onboarding/ProgressSteps.tsx`
- Reference: `components/Navbar.tsx` (паттерн лого+тема), `components/ThemeToggle.tsx`

**Interfaces:**
- Consumes: `OnboardingProvider` Task 4, `ThemeToggle` (существует).
- Produces: `OnboardingTopBar` (компонент, без пропсов), `ProgressSteps` (`{ current: number; labels: string[] }`).

- [ ] **Step 1: layout.tsx** (оборачивает в провайдер и каркас)

```tsx
// app/onboarding/layout.tsx
import type { ReactNode } from "react";
import { OnboardingProvider } from "@/components/onboarding/OnboardingProvider";

export default function OnboardingLayout({ children }: { children: ReactNode }) {
  return (
    <OnboardingProvider>
      <div className="min-h-dvh bg-canvas">{children}</div>
    </OnboardingProvider>
  );
}
```

- [ ] **Step 2: OnboardingTopBar.tsx** — лого слева, переключатель проекта (декоративный), ThemeToggle, колокольчик, аватар. Используй `Image` для лого (см. `components/Navbar.tsx` какие файлы лого: `/logo-wordmark.webp` для light, `public/brand/logo-lighttext.webp` для dark — свап как в Navbar). Иконки `Bell`, `ChevronDown` из lucide. Аватар — кружок с инициалами «АИ» на `bg-brand text-white`. Имя «Анна Иванова». Высота бара `h-16`, `border-b border-border`, `bg-card`.

```tsx
// components/onboarding/OnboardingTopBar.tsx
"use client";

import Image from "next/image";
import { Bell, ChevronDown } from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";

export default function OnboardingTopBar() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-4 sm:px-6">
      <div className="flex items-center gap-3 sm:gap-5">
        <Image src="/logo-wordmark.webp" alt="UCust" width={96} height={24} className="h-6 w-auto dark:hidden" />
        <Image src="/brand/logo-lighttext.webp" alt="UCust" width={96} height={24} className="hidden h-6 w-auto dark:block" />
        <button type="button" className="hidden items-center gap-2 rounded-xl border border-border bg-surface-soft px-3 py-1.5 text-left sm:flex">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-tint text-sm">☕</span>
          <span className="leading-tight">
            <span className="block text-sm font-semibold text-ink">Кофейня «Зерно»</span>
            <span className="block text-xs text-ink-muted">Кофейня</span>
          </span>
          <ChevronDown size={16} className="text-ink-muted" aria-hidden="true" />
        </button>
      </div>
      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle />
        <button type="button" aria-label="Уведомления" className="relative flex h-9 w-9 items-center justify-center rounded-full text-ink-muted hover:bg-surface-soft hover:text-ink">
          <Bell size={18} aria-hidden="true" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-brand" />
        </button>
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand text-sm font-semibold text-white">АИ</span>
          <span className="hidden text-sm font-medium text-ink sm:block">Анна Иванова</span>
        </div>
      </div>
    </header>
  );
}
```

> Примечание для исполнителя: подтвердить точные пути лого в `components/ThemeToggle.tsx`/`components/Navbar.tsx` и `components/ThemeToggle` экспорт (default). Если `ThemeToggle` — named export, поправить импорт.

- [ ] **Step 3: ProgressSteps.tsx**

```tsx
// components/onboarding/ProgressSteps.tsx
export default function ProgressSteps({ current, labels }: { current: number; labels: string[] }) {
  return (
    <div aria-label="Прогресс онбординга" className="mx-auto flex max-w-xl gap-2">
      {labels.map((label, i) => (
        <div key={label} className="flex-1">
          <div
            className={`h-1.5 rounded-full transition-colors ${i <= current ? "bg-brand" : "bg-border"}`}
            aria-current={i === current ? "step" : undefined}
          />
          <span className={`mt-2 hidden text-xs sm:block ${i <= current ? "text-ink" : "text-ink-muted"}`}>{label}</span>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 4: Проверка** — `npx tsc --noEmit` + `npm run lint` → 0 ошибок. (Визуально проверится в Task 9.)

---

## Task 6: Мелкие примитивы — Field, Chip

**Files:**
- Create: `components/onboarding/Field.tsx`, `components/onboarding/Chip.tsx`

**Interfaces:**
- Produces:
  - `Field` (`{ label: string; hint?: string; children: ReactNode }`) — обёртка label+контрол.
  - `TextInput` (`React.InputHTMLAttributes<HTMLInputElement>`) и `TextArea` (`React.TextareaHTMLAttributes<HTMLTextAreaElement>`) — стилизованные поля.
  - `Chip` (`{ children: ReactNode; color?: "brand" | "purple" | "pink" | "orange" | "success"; onRemove?: () => void }`).

- [ ] **Step 1: Field.tsx**

```tsx
// components/onboarding/Field.tsx
import type { InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from "react";

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-semibold text-ink">{label}</span>
      {children}
      {hint && <span className="mt-1.5 block text-xs text-ink-muted">{hint}</span>}
    </label>
  );
}

const base =
  "w-full rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink placeholder:text-ink-muted/70 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand-tint";

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`${base} ${props.className ?? ""}`} />;
}

export function TextArea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={`${base} min-h-28 resize-none ${props.className ?? ""}`} />;
}
```

- [ ] **Step 2: Chip.tsx**

```tsx
// components/onboarding/Chip.tsx
import { X } from "lucide-react";
import type { ReactNode } from "react";

const COLORS = {
  brand: "bg-brand/12 text-brand",
  purple: "bg-brand-purple/15 text-brand-purple",
  pink: "bg-brand-pink/15 text-brand-pink",
  orange: "bg-brand-orange/15 text-brand-orange",
  success: "bg-success/15 text-success",
} as const;

export default function Chip({
  children,
  color = "brand",
  onRemove,
}: {
  children: ReactNode;
  color?: keyof typeof COLORS;
  onRemove?: () => void;
}) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${COLORS[color]}`}>
      {children}
      {onRemove && (
        <button type="button" onClick={onRemove} aria-label="Удалить" className="opacity-70 hover:opacity-100">
          <X size={12} aria-hidden="true" />
        </button>
      )}
    </span>
  );
}
```

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 7: Шаги визарда 1 и 2

**Files:**
- Create: `components/onboarding/steps/StepBusinessName.tsx`, `components/onboarding/steps/StepAbout.tsx`

**Interfaces:**
- Consumes: `useOnboarding` Task 4, `Field/TextInput/TextArea` Task 6.
- Produces: `StepBusinessName` (без пропсов), `StepAbout` (без пропсов) — читают/пишут input через контекст.

- [ ] **Step 1: StepBusinessName.tsx** — заголовок «Как называется ваш бизнес?», подзаголовок «Укажите название и краткое описание — это поможет системе лучше понять ваш бизнес». Поля: Название (`input.name`, плейсхолдер «Например: Кофейня Аромат»), «Чем занимается ваш бизнес? (необязательно)» (`input.description`, textarea, плейсхолдер «Кратко опишите, что вы делаете и для кого»).

```tsx
// components/onboarding/steps/StepBusinessName.tsx
"use client";

import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { Field, TextArea, TextInput } from "@/components/onboarding/Field";

export default function StepBusinessName() {
  const { input, updateInput } = useOnboarding();
  return (
    <div className="flex flex-col gap-5">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Как называется ваш бизнес?</h1>
        <p className="mt-2 text-sm text-ink-muted sm:text-base">
          Укажите название и краткое описание — это поможет системе лучше понять ваш бизнес
        </p>
      </header>
      <Field label="Название">
        <TextInput
          value={input.name}
          onChange={(e) => updateInput({ name: e.target.value })}
          placeholder="Например: Кофейня Аромат"
        />
      </Field>
      <Field label="Чем занимается ваш бизнес? (необязательно)">
        <TextArea
          value={input.description}
          onChange={(e) => updateInput({ description: e.target.value })}
          placeholder="Кратко опишите, что вы делаете и для кого"
        />
      </Field>
    </div>
  );
}
```

- [ ] **Step 2: StepAbout.tsx** — заголовок «Расскажите о бизнесе», подзаголовок «Проще всего — дать ссылку на сайт или соцсеть, система сама всё найдёт». Segmented control из двух кнопок: «По ссылке» (icon `Link2`) / «Вручную» (icon `FileText`), активная — `bg-brand text-white`, неактивная — `bg-surface-soft text-ink`. По `input.aboutMode`. Контент:
  - `link`: Field «Ссылка на сайт или соцсеть» → TextInput (`input.link`), hint «Можно указать ссылку на сайт, группу ВКонтакте, страницу в Instagram или Telegram-канал».
  - `manual`: Field «Чем занимается бизнес» → TextInput (`input.activity`, плейсхолдер «Например: кофейня, салон красоты, юридические услуги») + Field «Что отличает вас от конкурентов? (необязательно)» → TextArea (`input.difference`, плейсхолдер «В чём ваша уникальность?»).

```tsx
// components/onboarding/steps/StepAbout.tsx
"use client";

import { FileText, Link2 } from "lucide-react";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { Field, TextArea, TextInput } from "@/components/onboarding/Field";
import type { AboutMode } from "@/lib/onboarding/types";

export default function StepAbout() {
  const { input, updateInput } = useOnboarding();
  const tab = (mode: AboutMode, label: string, Icon: typeof Link2) => (
    <button
      type="button"
      role="tab"
      aria-selected={input.aboutMode === mode}
      onClick={() => updateInput({ aboutMode: mode })}
      className={`flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
        input.aboutMode === mode ? "bg-brand text-white" : "bg-surface-soft text-ink hover:text-brand"
      }`}
    >
      <Icon size={16} aria-hidden="true" />
      {label}
    </button>
  );

  return (
    <div className="flex flex-col gap-5">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Расскажите о бизнесе</h1>
        <p className="mt-2 text-sm text-ink-muted sm:text-base">
          Проще всего — дать ссылку на сайт или соцсеть, система сама всё найдёт
        </p>
      </header>
      <div role="tablist" className="flex gap-2">
        {tab("link", "По ссылке", Link2)}
        {tab("manual", "Вручную", FileText)}
      </div>
      {input.aboutMode === "link" ? (
        <Field
          label="Ссылка на сайт или соцсеть"
          hint="Можно указать ссылку на сайт, группу ВКонтакте, страницу в Instagram или Telegram-канал"
        >
          <TextInput
            value={input.link}
            onChange={(e) => updateInput({ link: e.target.value })}
            placeholder="https://example.com или ссылка на VK/Instagram"
          />
        </Field>
      ) : (
        <div className="flex flex-col gap-5">
          <Field label="Чем занимается бизнес">
            <TextInput
              value={input.activity}
              onChange={(e) => updateInput({ activity: e.target.value })}
              placeholder="Например: кофейня, салон красоты, юридические услуги"
            />
          </Field>
          <Field label="Что отличает вас от конкурентов? (необязательно)">
            <TextArea
              value={input.difference}
              onChange={(e) => updateInput({ difference: e.target.value })}
              placeholder="В чём ваша уникальность?"
            />
          </Field>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 8: Шаг визарда 3 — соцсети + загрузка

**Files:**
- Create: `components/onboarding/steps/StepChannels.tsx`

**Interfaces:**
- Consumes: `useOnboarding` Task 4.
- Produces: `StepChannels` (без пропсов).

- [ ] **Step 1: StepChannels.tsx** — заголовок «Подключите соцсети», подзаголовок «Выберите, куда будем публиковать контент. Можно пропустить и настроить позже.». Сетка 2×2 карточек-кнопок для соцсетей. Каждая: иконка-квадрат с буквой на бренд-цвете, название, подпись «Нажмите для подключения» / при подключении — «Подключено» + `Check`. Тоггл добавляет/убирает id из `input.socials`, `aria-pressed`. Соцсети: Instagram (`brand-pink`), ВКонтакте (`#0077ff`), Telegram (`#28a8e9`), Facebook (`#1877f2`). Ниже — drag-drop зона «Загрузите дополнительные файлы о бизнесе (необязательно)»: пунктирная рамка `border-2 border-dashed border-border`, иконка `Upload`, «Прайс, презентация, каталог», «PDF, DOC, XLSX (макс. 10 файлов)». Клик/`<input type="file" hidden multiple>` добавляет имена файлов в `input.files` (имитация, без отправки); показать список имён с возможностью удалить.

```tsx
// components/onboarding/steps/StepChannels.tsx
"use client";

import { useRef } from "react";
import { Check, Upload, X } from "lucide-react";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import type { SocialId } from "@/lib/onboarding/types";

const SOCIALS: { id: SocialId; label: string; letter: string; color: string }[] = [
  { id: "instagram", label: "Instagram", letter: "Ig", color: "var(--brand-pink)" },
  { id: "vk", label: "ВКонтакте", letter: "VK", color: "#0077ff" },
  { id: "telegram", label: "Telegram", letter: "Tg", color: "#28a8e9" },
  { id: "facebook", label: "Facebook", letter: "f", color: "#1877f2" },
];

export default function StepChannels() {
  const { input, updateInput } = useOnboarding();
  const fileRef = useRef<HTMLInputElement>(null);

  const toggle = (id: SocialId) => {
    const connected = input.socials.includes(id);
    updateInput({ socials: connected ? input.socials.filter((s) => s !== id) : [...input.socials, id] });
  };

  const addFiles = (list: FileList | null) => {
    if (!list) return;
    const names = Array.from(list).map((f) => f.name);
    updateInput({ files: [...input.files, ...names].slice(0, 10) });
  };

  return (
    <div className="flex flex-col gap-5">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Подключите соцсети</h1>
        <p className="mt-2 text-sm text-ink-muted sm:text-base">
          Выберите, куда будем публиковать контент. Можно пропустить и настроить позже.
        </p>
      </header>

      <div className="grid gap-3 sm:grid-cols-2">
        {SOCIALS.map((s) => {
          const connected = input.socials.includes(s.id);
          return (
            <button
              key={s.id}
              type="button"
              aria-pressed={connected}
              onClick={() => toggle(s.id)}
              className={`flex items-center gap-3 rounded-2xl border bg-card px-4 py-3.5 text-left transition ${
                connected ? "border-brand ring-1 ring-brand" : "border-border hover:border-brand/50"
              }`}
            >
              <span
                className="flex h-10 w-10 items-center justify-center rounded-xl text-sm font-bold text-white"
                style={{ backgroundColor: s.color }}
                aria-hidden="true"
              >
                {s.letter}
              </span>
              <span className="leading-tight">
                <span className="block text-sm font-semibold text-ink">{s.label}</span>
                <span className={`block text-xs ${connected ? "text-brand" : "text-ink-muted"}`}>
                  {connected ? "Подключено" : "Нажмите для подключения"}
                </span>
              </span>
              {connected && <Check size={18} className="ml-auto text-brand" aria-hidden="true" />}
            </button>
          );
        })}
      </div>

      <div>
        <p className="mb-2 text-sm text-ink-muted">Загрузите дополнительные файлы о бизнесе (необязательно)</p>
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          className="flex w-full flex-col items-center gap-1.5 rounded-2xl border-2 border-dashed border-border bg-surface-soft px-6 py-8 text-center transition hover:border-brand/50"
        >
          <Upload size={24} className="text-brand" aria-hidden="true" />
          <span className="text-sm font-medium text-ink">Прайс, презентация, каталог</span>
          <span className="text-xs text-ink-muted">PDF, DOC, XLSX (макс. 10 файлов)</span>
        </button>
        <input
          ref={fileRef}
          type="file"
          multiple
          hidden
          onChange={(e) => addFiles(e.target.files)}
        />
        {input.files.length > 0 && (
          <ul className="mt-3 flex flex-col gap-1.5">
            {input.files.map((name, i) => (
              <li key={`${name}-${i}`} className="flex items-center justify-between rounded-lg bg-surface-soft px-3 py-2 text-sm text-ink">
                <span className="truncate">{name}</span>
                <button
                  type="button"
                  aria-label="Удалить файл"
                  onClick={() => updateInput({ files: input.files.filter((_, j) => j !== i) })}
                  className="text-ink-muted hover:text-ink"
                >
                  <X size={16} aria-hidden="true" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 9: AnalysisScreen + WizardFlow + страница `/onboarding`

**Files:**
- Create: `components/onboarding/AnalysisScreen.tsx`, `components/onboarding/WizardFlow.tsx`, `app/onboarding/page.tsx`
- Reference: `components/Channels.tsx` (mounted-паттерн), `public/app/icon.png`/знак UCust

**Interfaces:**
- Consumes: всё из Task 4–8, `OnboardingTopBar`, `ProgressSteps`, `useOnboarding`, `useRouter` (next/navigation).
- Produces: `AnalysisScreen` (`{ onDone: () => void }`), `WizardFlow` (без пропсов).

- [ ] **Step 1: AnalysisScreen.tsx** — по центру: анимированная иконка-звезда (lucide `Sparkles` или знак UCust на `text-brand`), «Анализируем ваш бизнес», «Это займёт несколько секунд…», прогресс-бар (имитация заполнения). Через ~2.5с вызывает `onDone`. Анимацию пульсации делать с учётом reduced-motion.

```tsx
// components/onboarding/AnalysisScreen.tsx
"use client";

import { useEffect } from "react";
import { Sparkles } from "lucide-react";
import { motion } from "framer-motion";

export default function AnalysisScreen({ onDone }: { onDone: () => void }) {
  useEffect(() => {
    const t = setTimeout(onDone, 2600);
    return () => clearTimeout(t);
  }, [onDone]);

  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <motion.span
        className="mb-5 text-brand"
        animate={{ scale: [1, 1.15, 1], opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
      >
        <Sparkles size={44} aria-hidden="true" />
      </motion.span>
      <h1 className="text-2xl font-bold text-ink sm:text-3xl">Анализируем ваш бизнес</h1>
      <p className="mt-2 text-sm text-ink-muted">Это займёт несколько секунд…</p>
      <div className="mt-6 h-1.5 w-64 overflow-hidden rounded-full bg-border">
        <motion.div
          className="h-full rounded-full bg-brand"
          initial={{ width: "5%" }}
          animate={{ width: "100%" }}
          transition={{ duration: 2.5, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: WizardFlow.tsx** — state-machine. Состояние `step: 0|1|2` + `analyzing: boolean`. Шаги: `[StepBusinessName, StepAbout, StepChannels]`, прогресс-лейблы `["Название", "О бизнесе", "Соцсети", "Анализ"]`. На шаге 2 кнопка «Далее» → «Начать анализ»: ставит `analyzing=true`, вызывает `runAnalysis()`. `AnalysisScreen.onDone` → `router.push("/onboarding/review")`. «Далее» на шаге 0 заблокирована при пустом `input.name`. Кнопки внизу: «Назад» (`.btn-glass`, скрыта на шаге 0) / «Далее»/«Начать анализ» (`.btn-glass-blue`).

```tsx
// components/onboarding/WizardFlow.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingTopBar from "./OnboardingTopBar";
import ProgressSteps from "./ProgressSteps";
import StepBusinessName from "./steps/StepBusinessName";
import StepAbout from "./steps/StepAbout";
import StepChannels from "./steps/StepChannels";
import AnalysisScreen from "./AnalysisScreen";
import { useOnboarding } from "./OnboardingProvider";

const LABELS = ["Название", "О бизнесе", "Соцсети", "Анализ"];

export default function WizardFlow() {
  const router = useRouter();
  const { input, runAnalysis } = useOnboarding();
  const [step, setStep] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);

  const startAnalysis = () => {
    setAnalyzing(true);
    void runAnalysis();
  };

  const nextDisabled = step === 0 && input.name.trim().length === 0;

  return (
    <div className="flex min-h-dvh flex-col">
      <OnboardingTopBar />
      <main className="mx-auto w-full max-w-2xl flex-1 px-5 py-10 sm:px-6 sm:py-14">
        <ProgressSteps current={analyzing ? 3 : step} labels={LABELS} />
        <div className="mt-12">
          {analyzing ? (
            <AnalysisScreen onDone={() => router.push("/onboarding/review")} />
          ) : (
            <>
              {step === 0 && <StepBusinessName />}
              {step === 1 && <StepAbout />}
              {step === 2 && <StepChannels />}
              <div className="mt-10 flex gap-3">
                {step > 0 && (
                  <button
                    type="button"
                    onClick={() => setStep((s) => s - 1)}
                    className="btn-glass inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
                  >
                    Назад
                  </button>
                )}
                {step < 2 ? (
                  <button
                    type="button"
                    disabled={nextDisabled}
                    onClick={() => setStep((s) => s + 1)}
                    className="btn-glass-blue inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Далее
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={startAnalysis}
                    className="btn-glass-blue inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
                  >
                    Начать анализ
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 3: app/onboarding/page.tsx**

```tsx
// app/onboarding/page.tsx
import WizardFlow from "@/components/onboarding/WizardFlow";

export default function OnboardingPage() {
  return <WizardFlow />;
}
```

- [ ] **Step 4: Проверка** — `npx tsc --noEmit` + `npm run lint` → 0 ошибок. Запустить dev (`npm run dev` если не запущен), Playwright: открыть `http://localhost:3000/onboarding`, пройти шаги 1→2→3→анализ, скриншоты light+dark. Убедиться: прогресс заполняется, «Далее» заблокирована без названия, анализ ведёт на /review (будет 404 до Task 11 — это ок на этом шаге, проверить переход).

---

## Task 10: Ревью — sidebar + разделы

**Files:**
- Create: `components/onboarding/review/ProfileSidebar.tsx`, `SectionAbout.tsx`, `SectionMarket.tsx`, `SectionSwot.tsx`, `SectionServices.tsx`, `SectionGoals.tsx`

**Interfaces:**
- Consumes: `useOnboarding` (для `profile`), `Field/TextInput/TextArea`, `Chip`.
- Produces: `ProfileSidebar` (`{ current: number; onSelect: (i: number) => void }`), пять Section-компонентов (`{ profile: BrandProfile }`; SectionAbout также принимает `onEdit?` — но для демо правки локальны/в контекст по желанию; минимально — read-only поля, редактируемость опциональна).

> Для демо разделы могут быть read-only визуально-точными. Если редактирование `О проекте` тривиально — прокинуть через `updateProfileField` (добавить в провайдер `setProfile`-патч), иначе оставить значения из профиля.

- [ ] **Step 1: ProfileSidebar.tsx** — список из 5 пунктов: «1. О проекте», «2. Рынок», «3. SWOT анализ», «4. Услуги», «5. Цели». Сверху ссылка «← На главную» (`Link href="/"`), заголовок «Проект». Активный пункт — `bg-brand text-white rounded-xl`, остальные — `text-ink-muted hover:text-ink`. На десктопе колонка `w-64 border-r border-border`, на мобильном — горизонтальный скролл-таб.

```tsx
// components/onboarding/review/ProfileSidebar.tsx
"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

const ITEMS = ["1. О проекте", "2. Рынок", "3. SWOT анализ", "4. Услуги", "5. Цели"];

export default function ProfileSidebar({ current, onSelect }: { current: number; onSelect: (i: number) => void }) {
  return (
    <aside className="shrink-0 border-border lg:w-64 lg:border-r">
      <Link href="/" className="mb-4 hidden items-center gap-2 px-4 pt-6 text-sm text-ink-muted hover:text-ink lg:flex">
        <ArrowLeft size={16} aria-hidden="true" /> На главную
      </Link>
      <p className="mb-2 hidden px-4 text-xs font-semibold uppercase tracking-wide text-ink-muted lg:block">Проект</p>
      <nav className="flex gap-2 overflow-x-auto px-2 pb-2 lg:flex-col lg:overflow-visible lg:pb-0">
        {ITEMS.map((item, i) => (
          <button
            key={item}
            type="button"
            onClick={() => onSelect(i)}
            aria-current={i === current ? "page" : undefined}
            className={`whitespace-nowrap rounded-xl px-4 py-2.5 text-left text-sm font-medium transition ${
              i === current ? "bg-brand text-white" : "text-ink-muted hover:bg-surface-soft hover:text-ink"
            }`}
          >
            {item}
          </button>
        ))}
      </nav>
    </aside>
  );
}
```

- [ ] **Step 2: SectionAbout.tsx** — заголовок «О проекте», подзаголовок «Проверьте информацию. Если что-то неправильно — отредактируйте.». Карточка-превью лого (квадрат `aspect square`, `bg-brand-tint`, инициалы/название бизнеса крупно). Поля Название (`profile.name`), Сфера деятельности (`profile.field`), Позиционирование (`profile.positioning`) — через `Field`+`TextInput/TextArea`, значения из профиля (read-only или editable).

```tsx
// components/onboarding/review/SectionAbout.tsx
"use client";

import type { BrandProfile } from "@/lib/onboarding/types";
import { Field, TextArea, TextInput } from "@/components/onboarding/Field";

export default function SectionAbout({ profile }: { profile: BrandProfile }) {
  return (
    <div className="flex flex-col gap-5">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">О проекте</h1>
        <p className="mt-2 text-sm text-ink-muted">Проверьте информацию. Если что-то неправильно — отредактируйте.</p>
      </header>
      <div className="flex aspect-[2/1] max-w-sm items-center justify-center rounded-2xl bg-brand-tint">
        <span className="font-display text-2xl font-extrabold text-brand">{profile.name}</span>
      </div>
      <Field label="Название">
        <TextInput defaultValue={profile.name} />
      </Field>
      <Field label="Сфера деятельности">
        <TextInput defaultValue={profile.field} />
      </Field>
      <Field label="Позиционирование">
        <TextArea defaultValue={profile.positioning} />
      </Field>
    </div>
  );
}
```

- [ ] **Step 3: SectionMarket.tsx** — заголовок «Рынок», подзаголовок «Основная информация о вашем рынке». Карточка «Конкуренты» (чипы `purple`). Две карточки рядом: «География» (`profile.market.geography`), «Сегмент» (`profile.market.segment`). Карточка «Тренды рынка» — чипы `success` из `profile.market.trends`. Карточки — `rounded-2xl border border-border bg-card p-5`.

```tsx
// components/onboarding/review/SectionMarket.tsx
import type { BrandProfile } from "@/lib/onboarding/types";
import Chip from "@/components/onboarding/Chip";

export default function SectionMarket({ profile }: { profile: BrandProfile }) {
  const m = profile.market;
  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Рынок</h1>
        <p className="mt-2 text-sm text-ink-muted">Основная информация о вашем рынке</p>
      </header>
      <div className="rounded-2xl border border-border bg-card p-5">
        <p className="mb-3 text-sm font-semibold text-ink-muted">Конкуренты</p>
        <div className="flex flex-wrap gap-2">
          {m.competitors.map((c) => (
            <Chip key={c} color="purple">{c}</Chip>
          ))}
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-border bg-card p-5">
          <p className="mb-1 text-sm font-semibold text-ink-muted">География</p>
          <p className="text-sm text-ink">{m.geography}</p>
        </div>
        <div className="rounded-2xl border border-border bg-card p-5">
          <p className="mb-1 text-sm font-semibold text-ink-muted">Сегмент</p>
          <p className="text-sm text-ink">{m.segment}</p>
        </div>
      </div>
      <div className="rounded-2xl border border-border bg-card p-5">
        <p className="mb-3 text-sm font-semibold text-ink-muted">Тренды рынка</p>
        <div className="flex flex-wrap gap-2">
          {m.trends.map((t) => (
            <Chip key={t} color="success">{t}</Chip>
          ))}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: SectionSwot.tsx** — заголовок «SWOT анализ», подзаголовок «Сильные и слабые стороны вашего бизнеса». Сетка 2×2 карточек: «Сильные стороны» (маркер `success`), «Слабые стороны» (`pink`), «Возможности» (`brand`), «Угрозы» (`orange`). В каждой — цветная точка + заголовок + список пунктов с «·».

```tsx
// components/onboarding/review/SectionSwot.tsx
import type { BrandProfile } from "@/lib/onboarding/types";

const DOT = {
  success: "bg-success",
  pink: "bg-brand-pink",
  brand: "bg-brand",
  orange: "bg-brand-orange",
} as const;

function Quadrant({ title, items, color }: { title: string; items: string[]; color: keyof typeof DOT }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <p className="mb-3 flex items-center gap-2 font-bold text-ink">
        <span className={`h-2.5 w-2.5 rounded-full ${DOT[color]}`} aria-hidden="true" />
        {title}
      </p>
      <ul className="flex flex-col gap-1.5">
        {items.map((it) => (
          <li key={it} className="text-sm text-ink-muted">· {it}</li>
        ))}
      </ul>
    </div>
  );
}

export default function SectionSwot({ profile }: { profile: BrandProfile }) {
  const s = profile.swot;
  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">SWOT анализ</h1>
        <p className="mt-2 text-sm text-ink-muted">Сильные и слабые стороны вашего бизнеса</p>
      </header>
      <div className="grid gap-4 sm:grid-cols-2">
        <Quadrant title="Сильные стороны" items={s.strengths} color="success" />
        <Quadrant title="Слабые стороны" items={s.weaknesses} color="pink" />
        <Quadrant title="Возможности" items={s.opportunities} color="brand" />
        <Quadrant title="Угрозы" items={s.threats} color="orange" />
      </div>
    </div>
  );
}
```

- [ ] **Step 5: SectionServices.tsx** — заголовок «Услуги и товары», подзаголовок «Что вы предлагаете клиентам». Список карточек: иконка-квадрат с градиентом (`bg-gradient-to-br from-brand to-brand-purple` и варианты), заголовок (`title`), подпись (`items`).

```tsx
// components/onboarding/review/SectionServices.tsx
import { Sparkles } from "lucide-react";
import type { BrandProfile } from "@/lib/onboarding/types";

const GRADIENTS = [
  "from-success to-brand",
  "from-brand to-brand-purple",
  "from-brand-purple to-brand-pink",
];

export default function SectionServices({ profile }: { profile: BrandProfile }) {
  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Услуги и товары</h1>
        <p className="mt-2 text-sm text-ink-muted">Что вы предлагаете клиентам</p>
      </header>
      <div className="flex flex-col gap-3">
        {profile.services.map((s, i) => (
          <div key={s.title} className="flex items-center gap-4 rounded-2xl border border-border bg-card p-4">
            <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${GRADIENTS[i % GRADIENTS.length]} text-white`}>
              <Sparkles size={20} aria-hidden="true" />
            </span>
            <span className="leading-tight">
              <span className="block font-semibold text-ink">{s.title}</span>
              <span className="block text-sm text-ink-muted">{s.items}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 6: SectionGoals.tsx** — заголовок «Цели», подзаголовок «Чего хотим достичь с помощью контента». Список целей (`profile.goals`) — строки-карточки с цветной точкой палитры (циклично brand/purple/pink/orange). Карточка «Стиль общения с клиентами» — чипы из `profile.tone` (циклично цвета).

```tsx
// components/onboarding/review/SectionGoals.tsx
import type { BrandProfile } from "@/lib/onboarding/types";
import Chip from "@/components/onboarding/Chip";

const DOTS = ["bg-brand-orange", "bg-brand-purple", "bg-brand-pink", "bg-brand"];
const TONE_COLORS = ["orange", "purple", "pink", "brand"] as const;

export default function SectionGoals({ profile }: { profile: BrandProfile }) {
  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Цели</h1>
        <p className="mt-2 text-sm text-ink-muted">Чего хотим достичь с помощью контента</p>
      </header>
      <div className="flex flex-col gap-3">
        {profile.goals.map((g, i) => (
          <div key={g} className="flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3.5">
            <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${DOTS[i % DOTS.length]}`} aria-hidden="true" />
            <span className="text-sm text-ink">{g}</span>
          </div>
        ))}
      </div>
      <div className="rounded-2xl border border-border bg-card p-5">
        <p className="mb-3 text-sm font-semibold text-ink-muted">Стиль общения с клиентами</p>
        <div className="flex flex-wrap gap-2">
          {profile.tone.map((t, i) => (
            <Chip key={t} color={TONE_COLORS[i % TONE_COLORS.length]}>{t}</Chip>
          ))}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 7: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 11: ReviewFlow + страница `/onboarding/review`

**Files:**
- Create: `components/onboarding/review/ReviewFlow.tsx`, `app/onboarding/review/page.tsx`

**Interfaces:**
- Consumes: `useOnboarding`, `OnboardingTopBar`, `ProfileSidebar`, 5 Section-компонентов, `useRouter`.
- Produces: `ReviewFlow` (без пропсов).

- [ ] **Step 1: ReviewFlow.tsx** — если `profile === null` → `useEffect` redirect на `/onboarding` (и вернуть `null`). Иначе: `OnboardingTopBar`, ниже двухколоночный grid: `ProfileSidebar` + активный раздел по `section`-стейту. Под разделом — кнопки «Назад» (на разделе 0 скрыта)/«Далее»; на разделе 4 — «Готово — перейти в дашборд» (`router.push("/dashboard")`).

```tsx
// components/onboarding/review/ReviewFlow.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingTopBar from "../OnboardingTopBar";
import { useOnboarding } from "../OnboardingProvider";
import ProfileSidebar from "./ProfileSidebar";
import SectionAbout from "./SectionAbout";
import SectionMarket from "./SectionMarket";
import SectionSwot from "./SectionSwot";
import SectionServices from "./SectionServices";
import SectionGoals from "./SectionGoals";

export default function ReviewFlow() {
  const router = useRouter();
  const { profile } = useOnboarding();
  const [section, setSection] = useState(0);

  useEffect(() => {
    if (profile === null) router.replace("/onboarding");
  }, [profile, router]);

  if (!profile) return null;

  const sections = [
    <SectionAbout key="about" profile={profile} />,
    <SectionMarket key="market" profile={profile} />,
    <SectionSwot key="swot" profile={profile} />,
    <SectionServices key="services" profile={profile} />,
    <SectionGoals key="goals" profile={profile} />,
  ];

  return (
    <div className="flex min-h-dvh flex-col">
      <OnboardingTopBar />
      <div className="mx-auto flex w-full max-w-(--container-page) flex-1 flex-col gap-6 px-4 py-6 sm:px-6 lg:flex-row lg:gap-10">
        <ProfileSidebar current={section} onSelect={setSection} />
        <main className="min-w-0 flex-1 pb-10 lg:pt-6">
          {sections[section]}
          <div className="mt-10 flex gap-3">
            {section > 0 && (
              <button
                type="button"
                onClick={() => setSection((s) => s - 1)}
                className="btn-glass inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
              >
                Назад
              </button>
            )}
            {section < 4 ? (
              <button
                type="button"
                onClick={() => setSection((s) => s + 1)}
                className="btn-glass-blue inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
              >
                Далее
              </button>
            ) : (
              <button
                type="button"
                onClick={() => router.push("/dashboard")}
                className="btn-glass-blue inline-flex flex-1 items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
              >
                Готово — перейти в дашборд
              </button>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: app/onboarding/review/page.tsx**

```tsx
// app/onboarding/review/page.tsx
import ReviewFlow from "@/components/onboarding/review/ReviewFlow";

export default function ReviewPage() {
  return <ReviewFlow />;
}
```

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` + `npm run lint` → 0 ошибок. Playwright: пройти визард до конца, дождаться /review, кликнуть по всем 5 разделам, скриншоты light+dark + мобильная ширина (375px) для sidebar-табов.

---

## Task 12: `/verify-email` и `/dashboard`

**Files:**
- Create: `app/verify-email/page.tsx`, `app/dashboard/page.tsx`

**Interfaces:**
- Consumes: `next/navigation` (`useRouter`, `useSearchParams`), `next/link`.

- [ ] **Step 1: app/verify-email/page.tsx** — клиентский компонент: карточка по центру экрана (`min-h-dvh grid place-items-center bg-canvas`), иконка `MailCheck` в кружке `bg-brand-tint text-brand`, заголовок «Подтвердите почту», текст «Мы отправили письмо на {email}» (email из `useSearchParams().get("email")` или «вашу почту»), кнопка «Я подтвердил почту» (`.btn-glass-blue`) → `router.push("/onboarding")`, ниже текст-кнопка «Отправить повторно» (имитация: дизейбл на 30с с обратным отсчётом). Обернуть в `Suspense` (требование Next для `useSearchParams`).

```tsx
// app/verify-email/page.tsx
"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { MailCheck } from "lucide-react";

function VerifyEmailInner() {
  const router = useRouter();
  const email = useSearchParams().get("email");
  const [sent, setSent] = useState(false);

  return (
    <main className="grid min-h-dvh place-items-center bg-canvas px-5">
      <div className="w-full max-w-md rounded-[28px] border border-border bg-card p-8 text-center shadow-soft">
        <span className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-brand-tint text-brand">
          <MailCheck size={30} aria-hidden="true" />
        </span>
        <h1 className="text-2xl font-bold text-ink">Подтвердите почту</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Мы отправили письмо на {email ? <span className="font-medium text-ink">{email}</span> : "вашу почту"}.
          Перейдите по ссылке из письма, чтобы продолжить.
        </p>
        <button
          type="button"
          onClick={() => router.push("/onboarding")}
          className="btn-glass-blue mt-6 inline-flex w-full items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
        >
          Я подтвердил почту
        </button>
        <button
          type="button"
          disabled={sent}
          onClick={() => setSent(true)}
          className="mt-4 text-sm text-ink-muted hover:text-brand disabled:opacity-50"
        >
          {sent ? "Письмо отправлено" : "Отправить повторно"}
        </button>
      </div>
    </main>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={null}>
      <VerifyEmailInner />
    </Suspense>
  );
}
```

- [ ] **Step 2: app/dashboard/page.tsx** — заглушка: лого/иконка, «Дашборд скоро», текст «Мы готовим рабочее пространство. Совсем скоро здесь появится ваш контент-план и аналитика.», кнопка «На главную» (`Link href="/"`).

```tsx
// app/dashboard/page.tsx
import Link from "next/link";
import { LayoutDashboard } from "lucide-react";

export default function DashboardPage() {
  return (
    <main className="grid min-h-dvh place-items-center bg-canvas px-5 text-center">
      <div>
        <span className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-tint text-brand">
          <LayoutDashboard size={30} aria-hidden="true" />
        </span>
        <h1 className="text-3xl font-bold text-ink">Дашборд скоро</h1>
        <p className="mx-auto mt-3 max-w-md text-sm text-ink-muted sm:text-base">
          Мы готовим рабочее пространство. Совсем скоро здесь появится ваш контент-план и аналитика.
        </p>
        <Link
          href="/"
          className="btn-glass mt-7 inline-flex items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
        >
          На главную
        </Link>
      </div>
    </main>
  );
}
```

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` + `npm run lint` → 0 ошибок. Playwright: открыть `/verify-email?email=test@mail.ru` (кнопка ведёт на /onboarding), `/dashboard` (скриншоты light+dark).

---

## Task 13: Вход из регистрации (SignupModal → /verify-email)

**Files:**
- Modify: `components/SignupModal.tsx`

**Interfaces:**
- Consumes: `useRouter` (next/navigation).

- [ ] **Step 1:** Прочитать `components/SignupModal.tsx`, найти обработчик сабмита формы (или кнопку отправки). Импортировать `useRouter` из `next/navigation`. В обработчике сабмита: закрыть модалку (существующий `onClose`/контекст) и `router.push("/verify-email?email=" + encodeURIComponent(email))`, где `email` — значение поля email формы. Если формы как таковой нет (кнопки-заглушки) — повесить на основную CTA-кнопку «Зарегистрироваться» переход на `/verify-email` (без email, или с введённым, если поле есть). Сохранить существующий UX модалки.

> Точную правку определить по факту чтения файла. Минимальное вмешательство: только редирект после «успешной» регистрации, остальное не трогать.

- [ ] **Step 2: Проверка** — `npx tsc --noEmit` + `npm run lint` → 0 ошибок. Playwright: открыть главную, открыть модалку регистрации, засабмитить → редирект на `/verify-email`.

---

## Task 14: Финальная визуальная проверка

**Files:** —

- [ ] **Step 1:** Полный сквозной прогон через Playwright (light и dark):
  главная → открыть регистрацию → сабмит → `/verify-email` → «Я подтвердил» → визард (3 шага, проверить заполнение полей, табы шага 2, тогглы соцсетей, загрузку файла-имитации) → «Начать анализ» → экран анализа → `/onboarding/review` → пройти все 5 разделов → «Готово» → `/dashboard`.
- [ ] **Step 2:** Проверить мобильную ширину (375px): топ-бар, прогресс, sidebar-табы ревью, сетки SWOT/услуг в один столбец.
- [ ] **Step 3:** Проверить отсутствие тёмных «плашек» в light-теме (всё на `bg-card`/`surface-soft`), контраст текста, читаемость чипов.
- [ ] **Step 4:** `npx tsc --noEmit` + `npm run lint` → 0 ошибок. Зафиксировать результат (скриншоты ключевых экранов).

---

## Self-Review (для автора плана)

**Покрытие спеки:**
- verify-email → Task 12 ✓; onboarding layout/provider → Task 4,5 ✓; визард 3 шага → Task 7,8 ✓; анализ → Task 9 ✓; ревью 5 разделов → Task 10,11 ✓; dashboard → Task 12 ✓; слой данных (типы/пресеты/mock/storage) → Task 1–3 ✓; вход из регистрации → Task 13 ✓; темы/доступность/проверка → Global Constraints + Task 14 ✓.
- Нишевые пресеты (coffee/beauty/retail/services/default) → Task 2 ✓.

**Типы/сигнатуры консистентны:** `WizardInput`, `BrandProfile`, `analyzeBusiness`, `useOnboarding({input,profile,updateInput,runAnalysis,resetAll})`, `pickPreset`, storage — совпадают между задачами ✓.

**Открытые мелочи для исполнителя (не блокеры):**
- Подтвердить экспорт/пути `ThemeToggle` и файлов лого в Task 5 по факту чтения `Navbar.tsx`.
- Редактируемость полей в `SectionAbout` — опциональна (read-only допустимо для демо).
- Точную правку `SignupModal` определить по факту чтения файла (Task 13).
```
