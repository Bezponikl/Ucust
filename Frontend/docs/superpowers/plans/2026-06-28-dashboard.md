# Дашборд (итерация 1: шелл + обзор) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Построить адаптивный шелл дашборда (десктоп-сайдбар ↔ мобильный bottom-nav) и главный обзорный экран, читающий «мозг бренда» из онбординга; остальные разделы — заглушки «Скоро».

**Architecture:** Роут-группа `app/dashboard/` с общим `DashboardShell` в layout. `DashboardProvider` читает профиль из sessionStorage (ключ онбординга) и собирает данные обзора через `getDashboardData()`. Обзор — композиция изолированных блоков; данные мок (гибрид, потом API).

**Tech Stack:** Next.js 16 (App Router, Turbopack), React 19, Tailwind v4 (токены тем), framer-motion, lucide-react. TypeScript. SVG-график без сторонних либ.

## Global Constraints

- **Next.js 16** — App Router; интерактивные компоненты `"use client"`; навигация через `next/navigation` (`usePathname`, `useRouter`), ссылки `next/link`.
- **Темы:** class-based dark, наследуется от корневого layout. Только токены: `bg-card`, `bg-surface-soft`, `bg-canvas`, `text-ink`, `text-ink-muted`, `border-border`, `text-brand`, `bg-brand`, `brand-tint`, палитра `brand-purple/brand-pink/brand-orange/success`. **Без тёмных плашек** в light.
- **Кнопки:** `.btn-glass`, `.btn-glass-blue`, `.btn-glass-dark` — не изобретать.
- **Мобайл-фёрст:** одна колонка на мобиле; стат-карты 2×2; bottom-nav фиксирован снизу, контент с нижним отступом; тач-цели ≥44px.
- **Шрифт:** Manrope (`font-display`/`font-body` глобально).
- **Скругления:** карточки `rounded-[20px]`/`rounded-[24px]`, кнопки/поля `rounded-xl`.
- **Анимации:** уважать `prefers-reduced-motion` mounted-паттерном (как `components/Channels.tsx`), без ветвления разметки до монтирования.
- **Данные:** мок сейчас, API потом — только тело `getDashboardData`. Профиль читать через существующий `loadOnboarding()` из `lib/onboarding/storage`.
- **Проект не под git:** «коммиты» = чекпойнты. **Проверка:** `npx tsc --noEmit` (0 ошибок) + `npx eslint <paths>` (0 ошибок) + dev-компиляция + визуальный Playwright (light+dark, ~1280 и ~390).
- **Язык:** русский; копи-тексты брать дословно из плана.

---

## Файловая структура

```
lib/dashboard/types.ts        — DashboardData + под-типы
lib/dashboard/mock.ts          — getDashboardData(profile): DashboardData

components/dashboard/nav.ts                 — NAV_ITEMS (DRY для sidebar/bottomnav)
components/dashboard/DashboardProvider.tsx   — контекст + данные из sessionStorage
components/dashboard/ProjectSwitcher.tsx
components/dashboard/DashboardTopBar.tsx
components/dashboard/DashboardSidebar.tsx
components/dashboard/DashboardBottomNav.tsx
components/dashboard/DashboardShell.tsx
components/dashboard/SectionStub.tsx
components/dashboard/overview/OverviewHeader.tsx
components/dashboard/overview/StatCards.tsx
components/dashboard/overview/ReachChart.tsx
components/dashboard/overview/AiTips.tsx
components/dashboard/overview/WeekPreview.tsx
components/dashboard/overview/ActivityFeed.tsx
components/dashboard/overview/Overview.tsx   — композиция блоков

app/dashboard/layout.tsx       — DashboardProvider + DashboardShell
app/dashboard/page.tsx         — <Overview/> (заменяет текущую заглушку)
app/dashboard/content/page.tsx — <SectionStub.../>
app/dashboard/promos/page.tsx
app/dashboard/reviews/page.tsx
app/dashboard/chatbot/page.tsx
app/dashboard/create/page.tsx
```

---

## Task 1: Слой данных — типы

**Files:** Create `lib/dashboard/types.ts`

**Interfaces:**
- Consumes: `ChannelId` из `@/lib/channels`.
- Produces: `AccentColor`, `StatIcon`, `Stat`, `ChartTab`, `AiTip`, `PostStatus`, `PlanDay`, `ActivityItem`, `DashboardData`.

- [ ] **Step 1: Создать типы**

```ts
// lib/dashboard/types.ts
import type { ChannelId } from "@/lib/channels";

export type AccentColor = "brand" | "purple" | "pink" | "orange" | "success";
export type StatIcon = "views" | "engagement" | "subscribers" | "reviews";

export interface Stat {
  id: string;
  label: string;
  value: string;
  hint: string;
  delta?: string;
  icon: StatIcon;
  color: AccentColor;
}

export type ChartTab = "reach" | "engagement" | "clicks";

export interface AiTip {
  id: string;
  title: string;
  text: string;
  color: AccentColor;
  href: string;
}

export type PostStatus = "published" | "scheduled" | "draft" | "none";

export interface PlanDay {
  weekday: string;
  day: number;
  status: PostStatus;
  channels: ChannelId[];
}

export interface ActivityItem {
  id: string;
  text: string;
  time: string;
  color: AccentColor;
}

export interface DashboardData {
  businessName: string;
  stats: Stat[];
  chart: Record<ChartTab, number[]>;
  tips: AiTip[];
  week: PlanDay[];
  activity: ActivityItem[];
}
```

- [ ] **Step 2: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 2: Слой данных — мок

**Files:** Create `lib/dashboard/mock.ts`

**Interfaces:**
- Consumes: типы Task 1, `BrandProfile` из `@/lib/onboarding/types`.
- Produces: `getDashboardData(profile: BrandProfile | null): DashboardData`.

- [ ] **Step 1: Создать мок**

```ts
// lib/dashboard/mock.ts
import type { BrandProfile } from "@/lib/onboarding/types";
import type { DashboardData } from "./types";

/**
 * Данные обзора дашборда. Мок: статы/график/рекомендации локальные, имя и часть
 * подсказок приправлены «мозгом бренда». ПОЗЖЕ заменяется на fetch к API — меняется
 * только тело этой функции.
 */
export function getDashboardData(profile: BrandProfile | null): DashboardData {
  const businessName = profile?.name?.trim() || "Ваш бизнес";
  const firstService = profile?.services?.[0]?.title ?? "новинке";
  const firstGoal = profile?.goals?.[0] ?? "Привлечь новых клиентов";

  return {
    businessName,
    stats: [
      { id: "views", label: "Просмотры", value: "12.5K", hint: "За последнюю неделю", delta: "+18%", icon: "views", color: "brand" },
      { id: "engagement", label: "Вовлечённость", value: "+24%", hint: "За последний месяц", icon: "engagement", color: "success" },
      { id: "subscribers", label: "Новые подписчики", value: "+127", hint: "За последнюю неделю", icon: "subscribers", color: "purple" },
      { id: "reviews", label: "Отзывы", value: "47", hint: "Требуют внимания", icon: "reviews", color: "orange" },
    ],
    chart: {
      reach: [20, 35, 28, 42, 55, 48, 62, 58, 70, 65, 78, 92],
      engagement: [10, 18, 16, 24, 30, 26, 34, 38, 33, 44, 40, 52],
      clicks: [5, 9, 7, 14, 12, 20, 18, 24, 22, 30, 28, 36],
    },
    tips: [
      {
        id: "post",
        title: `Создать пост о ${firstService.toLowerCase()}`,
        text: "Подписчики спрашивают про новинки — хороший повод для поста.",
        color: "pink",
        href: "/dashboard/create",
      },
      {
        id: "reviews",
        title: "Ответить на 3 новых отзыва",
        text: "Гости ждут вашего ответа — это повышает доверие.",
        color: "orange",
        href: "/dashboard/reviews",
      },
      {
        id: "promo",
        title: "Запустить акцию «Счастливые часы»",
        text: `Цель «${firstGoal.toLowerCase()}» — акция поможет её достичь.`,
        color: "brand",
        href: "/dashboard/promos",
      },
    ],
    week: [
      { weekday: "Пн", day: 1, status: "published", channels: ["vk", "telegram"] },
      { weekday: "Вт", day: 2, status: "published", channels: ["vk"] },
      { weekday: "Ср", day: 3, status: "scheduled", channels: ["telegram"] },
      { weekday: "Чт", day: 4, status: "scheduled", channels: ["vk", "telegram"] },
      { weekday: "Пт", day: 5, status: "draft", channels: [] },
      { weekday: "Сб", day: 6, status: "scheduled", channels: ["vk"] },
      { weekday: "Вс", day: 7, status: "none", channels: [] },
    ],
    activity: [
      { id: "a1", text: "Опубликован пост «Летняя акция»", time: "2 часа назад", color: "success" },
      { id: "a2", text: "Новый отзыв от Марии К.", time: "3 часа назад", color: "orange" },
      { id: "a3", text: "Запущена акция «День рождения»", time: "5 часов назад", color: "pink" },
    ],
  };
}
```

- [ ] **Step 2: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 3: Навигация — общий список пунктов

**Files:** Create `components/dashboard/nav.ts`

**Interfaces:**
- Produces: `NavItem` (`{ href: string; label: string; icon: LucideIcon }`), `NAV_ITEMS: NavItem[]`, `isNavActive(pathname: string, href: string): boolean`.

- [ ] **Step 1: Создать nav.ts**

```ts
// components/dashboard/nav.ts
import { LayoutDashboard, FileText, Gift, Star, MessageCircle, type LucideIcon } from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Дашборд", icon: LayoutDashboard },
  { href: "/dashboard/content", label: "Контент", icon: FileText },
  { href: "/dashboard/promos", label: "Акции", icon: Gift },
  { href: "/dashboard/reviews", label: "Отзывы", icon: Star },
  { href: "/dashboard/chatbot", label: "Чат-бот", icon: MessageCircle },
];

// /dashboard активен только при точном совпадении (он префикс всех остальных).
export function isNavActive(pathname: string, href: string): boolean {
  return href === "/dashboard" ? pathname === "/dashboard" : pathname.startsWith(href);
}
```

- [ ] **Step 2: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 4: DashboardProvider

**Files:** Create `components/dashboard/DashboardProvider.tsx`

**Interfaces:**
- Consumes: `getDashboardData` Task 2, `loadOnboarding` из `@/lib/onboarding/storage`, `DashboardData` Task 1.
- Produces: `DashboardProvider` (компонент), `useDashboard()` → `{ data: DashboardData | null; hydrated: boolean }`.

- [ ] **Step 1: Создать провайдер**

```tsx
// components/dashboard/DashboardProvider.tsx
"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { DashboardData } from "@/lib/dashboard/types";
import { getDashboardData } from "@/lib/dashboard/mock";
import { loadOnboarding } from "@/lib/onboarding/storage";

interface Ctx {
  data: DashboardData | null;
  hydrated: boolean;
}

const DashboardContext = createContext<Ctx | null>(null);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Профиль доступен только в sessionStorage (клиент) — собираем данные после монтирования.
  useEffect(() => {
    const saved = loadOnboarding();
    /* eslint-disable react-hooks/set-state-in-effect */
    setData(getDashboardData(saved?.profile ?? null));
    setHydrated(true);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  return <DashboardContext.Provider value={{ data, hydrated }}>{children}</DashboardContext.Provider>;
}

export function useDashboard(): Ctx {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error("useDashboard must be used within DashboardProvider");
  return ctx;
}
```

- [ ] **Step 2: Проверка** — `npx tsc --noEmit` → 0 ошибок.

---

## Task 5: ProjectSwitcher + DashboardTopBar

**Files:** Create `components/dashboard/ProjectSwitcher.tsx`, `components/dashboard/DashboardTopBar.tsx`
**Reference:** `components/onboarding/OnboardingTopBar.tsx` (паттерн лого/тема/аватар), `components/ThemeToggle.tsx` (default export, `className`)

**Interfaces:**
- Consumes: `useDashboard` Task 4 (для имени проекта), `ThemeToggle`.
- Produces: `ProjectSwitcher` (без пропсов), `DashboardTopBar` (без пропсов).

- [ ] **Step 1: ProjectSwitcher.tsx** — кнопка с именем текущего проекта (из `data.businessName`, дефолт «Ваш бизнес») + выпадающий список мок-проектов + «Добавить проект». Дропдаун по локальному `open`-стейту, закрывается по клику вне (слушатель на document). Декоративный: выбор проекта только подсвечивает.

```tsx
// components/dashboard/ProjectSwitcher.tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown, Plus, Check } from "lucide-react";
import { useDashboard } from "./DashboardProvider";

const MOCK_PROJECTS = ["Вердиктор", "Coffee Shop", "Fashion Store"];

export default function ProjectSwitcher() {
  const { data } = useDashboard();
  const current = data?.businessName ?? "Ваш бизнес";
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex max-w-[200px] items-center gap-2 rounded-xl border border-border bg-surface-soft px-3 py-1.5 text-left"
      >
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-brand-tint text-xs font-bold text-brand" aria-hidden="true">
          {current.slice(0, 1).toUpperCase()}
        </span>
        <span className="min-w-0 leading-tight">
          <span className="block truncate text-sm font-semibold text-ink">{current}</span>
          <span className="block text-xs text-ink-muted">Проект</span>
        </span>
        <ChevronDown size={16} className={`shrink-0 text-ink-muted transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true" />
      </button>

      {open && (
        <div className="absolute left-0 top-full z-50 mt-2 w-64 overflow-hidden rounded-2xl border border-border bg-card p-1.5 shadow-lift">
          <button type="button" onClick={() => setOpen(false)} className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left hover:bg-surface-soft">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-tint text-xs font-bold text-brand" aria-hidden="true">{current.slice(0, 1).toUpperCase()}</span>
            <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{current}</span>
            <Check size={16} className="text-brand" aria-hidden="true" />
          </button>
          {MOCK_PROJECTS.map((p) => (
            <button key={p} type="button" onClick={() => setOpen(false)} className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left hover:bg-surface-soft">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-surface-soft text-xs font-bold text-ink-muted" aria-hidden="true">{p.slice(0, 1)}</span>
              <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{p}</span>
            </button>
          ))}
          <div className="my-1 h-px bg-border" />
          <button type="button" onClick={() => setOpen(false)} className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-medium text-brand hover:bg-surface-soft">
            <Plus size={16} aria-hidden="true" /> Добавить проект
          </button>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: DashboardTopBar.tsx** — лого (свап по теме, как в OnboardingTopBar) + `ProjectSwitcher` + справа `ThemeToggle`, колокольчик с бейджем, аватар «АИ»+имя.

```tsx
// components/dashboard/DashboardTopBar.tsx
"use client";

import Image from "next/image";
import { Bell } from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";
import ProjectSwitcher from "./ProjectSwitcher";

export default function DashboardTopBar() {
  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-border bg-card px-4 sm:px-6">
      <div className="flex items-center gap-3 sm:gap-5">
        <Image src="/logo-wordmark.webp" alt="UCust" width={700} height={161} className="h-6 w-auto dark:hidden" />
        <Image src="/brand/logo-lighttext.webp" alt="UCust" width={700} height={161} className="hidden h-6 w-auto dark:block" />
        <ProjectSwitcher />
      </div>
      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle />
        <button type="button" aria-label="Уведомления" className="relative flex h-9 w-9 items-center justify-center rounded-full text-ink-muted transition-colors hover:bg-surface-soft hover:text-ink">
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

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` + `npx eslint components/dashboard` → 0 ошибок.

---

## Task 6: Sidebar + BottomNav

**Files:** Create `components/dashboard/DashboardSidebar.tsx`, `components/dashboard/DashboardBottomNav.tsx`

**Interfaces:**
- Consumes: `NAV_ITEMS`, `isNavActive` Task 3, `usePathname`.
- Produces: `DashboardSidebar` (без пропсов), `DashboardBottomNav` (без пропсов).

- [ ] **Step 1: DashboardSidebar.tsx** — вертикальный список `NAV_ITEMS`, активный — `bg-brand-tint text-brand`, остальные `text-ink-muted hover:bg-surface-soft hover:text-ink`. Только десктоп (`hidden lg:flex`).

```tsx
// components/dashboard/DashboardSidebar.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_ITEMS, isNavActive } from "./nav";

export default function DashboardSidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden w-60 shrink-0 border-r border-border p-4 lg:block">
      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = isNavActive(pathname, href);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={`flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                active ? "bg-brand-tint text-brand" : "text-ink-muted hover:bg-surface-soft hover:text-ink"
              }`}
            >
              <Icon size={18} aria-hidden="true" />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
```

- [ ] **Step 2: DashboardBottomNav.tsx** — фиксированная панель снизу, только мобайл (`lg:hidden`). Иконка над подписью, активный — `text-brand`. `fixed bottom-0`, `border-t`, `bg-card`, безопасный отступ.

```tsx
// components/dashboard/DashboardBottomNav.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_ITEMS, isNavActive } from "./nav";

export default function DashboardBottomNav() {
  const pathname = usePathname();
  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 flex border-t border-border bg-card pb-[env(safe-area-inset-bottom)] lg:hidden">
      {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
        const active = isNavActive(pathname, href);
        return (
          <Link
            key={href}
            href={href}
            aria-current={active ? "page" : undefined}
            className={`flex flex-1 flex-col items-center gap-1 py-2.5 text-[11px] font-medium transition ${
              active ? "text-brand" : "text-ink-muted"
            }`}
          >
            <Icon size={20} aria-hidden="true" />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
```

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` + `npx eslint components/dashboard` → 0 ошибок.

---

## Task 7: DashboardShell + layout

**Files:** Create `components/dashboard/DashboardShell.tsx`; Create `app/dashboard/layout.tsx`; **delete старую заглушку контента** в `app/dashboard/page.tsx` (заменяется в Task 9).

**Interfaces:**
- Consumes: `DashboardProvider`, `DashboardTopBar`, `DashboardSidebar`, `DashboardBottomNav`.
- Produces: `DashboardShell` (`{ children: ReactNode }`).

- [ ] **Step 1: DashboardShell.tsx**

```tsx
// components/dashboard/DashboardShell.tsx
import type { ReactNode } from "react";
import DashboardTopBar from "./DashboardTopBar";
import DashboardSidebar from "./DashboardSidebar";
import DashboardBottomNav from "./DashboardBottomNav";

export default function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-dvh bg-canvas">
      <DashboardTopBar />
      <div className="mx-auto flex w-full max-w-(--container-page)">
        <DashboardSidebar />
        {/* нижний отступ под bottom-nav на мобиле */}
        <main className="min-w-0 flex-1 px-4 py-6 pb-24 sm:px-6 lg:pb-10">{children}</main>
      </div>
      <DashboardBottomNav />
    </div>
  );
}
```

- [ ] **Step 2: app/dashboard/layout.tsx**

```tsx
// app/dashboard/layout.tsx
import type { ReactNode } from "react";
import { DashboardProvider } from "@/components/dashboard/DashboardProvider";
import DashboardShell from "@/components/dashboard/DashboardShell";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <DashboardProvider>
      <DashboardShell>{children}</DashboardShell>
    </DashboardProvider>
  );
}
```

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` → 0 ошибок. (Текущая `app/dashboard/page.tsx` пока остаётся прежней — отрисуется внутри шелла; полноценно проверим в Task 9.)

---

## Task 8: SectionStub + страницы-заглушки

**Files:** Create `components/dashboard/SectionStub.tsx`, `app/dashboard/content/page.tsx`, `app/dashboard/promos/page.tsx`, `app/dashboard/reviews/page.tsx`, `app/dashboard/chatbot/page.tsx`, `app/dashboard/create/page.tsx`

**Interfaces:**
- Produces: `SectionStub` (`{ title: string; icon: LucideIcon }`).

- [ ] **Step 1: SectionStub.tsx**

```tsx
// components/dashboard/SectionStub.tsx
import type { LucideIcon } from "lucide-react";

export default function SectionStub({ title, icon: Icon }: { title: string; icon: LucideIcon }) {
  return (
    <div className="grid min-h-[60vh] place-items-center text-center">
      <div>
        <span className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-tint text-brand">
          <Icon size={28} aria-hidden="true" />
        </span>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">{title}</h1>
        <p className="mx-auto mt-2 max-w-sm text-sm text-ink-muted">
          Раздел в разработке — появится в ближайшем обновлении.
        </p>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Пять страниц-заглушек** (каждая — серверный компонент, импортирует иконку из lucide):

```tsx
// app/dashboard/content/page.tsx
import { FileText } from "lucide-react";
import SectionStub from "@/components/dashboard/SectionStub";
export default function ContentPage() {
  return <SectionStub title="Контент" icon={FileText} />;
}
```

```tsx
// app/dashboard/promos/page.tsx
import { Gift } from "lucide-react";
import SectionStub from "@/components/dashboard/SectionStub";
export default function PromosPage() {
  return <SectionStub title="Акции" icon={Gift} />;
}
```

```tsx
// app/dashboard/reviews/page.tsx
import { Star } from "lucide-react";
import SectionStub from "@/components/dashboard/SectionStub";
export default function ReviewsPage() {
  return <SectionStub title="Отзывы" icon={Star} />;
}
```

```tsx
// app/dashboard/chatbot/page.tsx
import { MessageCircle } from "lucide-react";
import SectionStub from "@/components/dashboard/SectionStub";
export default function ChatbotPage() {
  return <SectionStub title="Чат-бот" icon={MessageCircle} />;
}
```

```tsx
// app/dashboard/create/page.tsx
import { Sparkles } from "lucide-react";
import SectionStub from "@/components/dashboard/SectionStub";
export default function CreatePage() {
  return <SectionStub title="Создать контент" icon={Sparkles} />;
}
```

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` + `npx eslint components/dashboard app/dashboard` → 0 ошибок.

---

## Task 9: Обзор — заголовок + стат-карты + страница

**Files:** Create `components/dashboard/overview/OverviewHeader.tsx`, `components/dashboard/overview/StatCards.tsx`, `components/dashboard/overview/Overview.tsx`; Modify `app/dashboard/page.tsx`

**Interfaces:**
- Consumes: `useDashboard` Task 4, `DashboardData`/`Stat`/`StatIcon`/`AccentColor` Task 1.
- Produces: `OverviewHeader` (`{ businessName: string }`), `StatCards` (`{ stats: Stat[] }`), `Overview` (без пропсов).

- [ ] **Step 1: OverviewHeader.tsx**

```tsx
// components/dashboard/overview/OverviewHeader.tsx
"use client";

import Link from "next/link";
import { Sparkles } from "lucide-react";

export default function OverviewHeader({ businessName }: { businessName: string }) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Добрый день!</h1>
        <p className="mt-1 text-sm text-ink-muted sm:text-base">
          Вот что происходит с бизнесом «{businessName}»
        </p>
      </div>
      <Link
        href="/dashboard/create"
        className="btn-glass-blue inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold"
      >
        <Sparkles size={16} aria-hidden="true" />
        Создать контент
      </Link>
    </div>
  );
}
```

- [ ] **Step 2: StatCards.tsx** — сетка 2×2 мобайл / 4 десктоп. Карта: иконка (по `stat.icon`) на мягком цветном фоне (по `stat.color`), значение, подпись, опц. дельта.

```tsx
// components/dashboard/overview/StatCards.tsx
import { Eye, TrendingUp, UserPlus, MessageSquare, type LucideIcon } from "lucide-react";
import type { AccentColor, Stat, StatIcon } from "@/lib/dashboard/types";

const ICONS: Record<StatIcon, LucideIcon> = {
  views: Eye,
  engagement: TrendingUp,
  subscribers: UserPlus,
  reviews: MessageSquare,
};

const BG: Record<AccentColor, string> = {
  brand: "bg-brand/12 text-brand",
  purple: "bg-brand-purple/15 text-brand-purple",
  pink: "bg-brand-pink/15 text-brand-pink",
  orange: "bg-brand-orange/15 text-brand-orange",
  success: "bg-success/15 text-success",
};

export default function StatCards({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
      {stats.map((s) => {
        const Icon = ICONS[s.icon];
        return (
          <div key={s.id} className="rounded-[20px] border border-border bg-card p-4 shadow-soft sm:p-5">
            <span className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl ${BG[s.color]}`}>
              <Icon size={18} aria-hidden="true" />
            </span>
            <p className="flex items-baseline gap-2">
              <span className="font-display text-2xl font-extrabold text-ink">{s.value}</span>
              {s.delta && <span className="text-xs font-semibold text-success">{s.delta}</span>}
            </p>
            <p className="mt-0.5 text-sm font-medium text-ink">{s.label}</p>
            <p className="text-xs text-ink-muted">{s.hint}</p>
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 3: Overview.tsx** (пока только header + статы; остальные блоки добавятся в Task 10–11). Скелетон до гидрации.

```tsx
// components/dashboard/overview/Overview.tsx
"use client";

import { useDashboard } from "../DashboardProvider";
import OverviewHeader from "./OverviewHeader";
import StatCards from "./StatCards";

export default function Overview() {
  const { data } = useDashboard();

  if (!data) {
    return <div className="h-40 animate-pulse rounded-[20px] bg-surface-soft" />;
  }

  return (
    <div className="flex flex-col gap-6 sm:gap-8">
      <OverviewHeader businessName={data.businessName} />
      <StatCards stats={data.stats} />
    </div>
  );
}
```

- [ ] **Step 4: app/dashboard/page.tsx** — заменить заглушку на обзор.

```tsx
// app/dashboard/page.tsx
import Overview from "@/components/dashboard/overview/Overview";

export default function DashboardPage() {
  return <Overview />;
}
```

- [ ] **Step 5: Проверка** — `npx tsc --noEmit` + `npx eslint` → 0 ошибок. Playwright: открыть `/dashboard`, скриншоты light+dark (десктоп). Убедиться: топ-бар с переключателем проекта, сайдбар, приветствие с именем бизнеса, 4 стат-карты.

---

## Task 10: Обзор — график охвата (SVG)

**Files:** Create `components/dashboard/overview/ReachChart.tsx`; Modify `components/dashboard/overview/Overview.tsx`

**Interfaces:**
- Consumes: `ChartTab`, `DashboardData["chart"]` Task 1.
- Produces: `ReachChart` (`{ chart: Record<ChartTab, number[]> }`).

- [ ] **Step 1: ReachChart.tsx** — карта с заголовком «Охват за последние 30 дней», табы Охват/Вовлечённость/Клики (локальный стейт), SVG-полилиния по выбранной серии (нормировка 0..max в viewBox 0 0 100 40), горизонтальные линии сетки. Без сторонних либ.

```tsx
// components/dashboard/overview/ReachChart.tsx
"use client";

import { useState } from "react";
import type { ChartTab } from "@/lib/dashboard/types";

const TABS: { id: ChartTab; label: string }[] = [
  { id: "reach", label: "Охват" },
  { id: "engagement", label: "Вовлечённость" },
  { id: "clicks", label: "Клики" },
];

export default function ReachChart({ chart }: { chart: Record<ChartTab, number[]> }) {
  const [tab, setTab] = useState<ChartTab>("reach");
  const series = chart[tab];
  const max = Math.max(...series, 1);
  const W = 100;
  const H = 40;
  const points = series
    .map((v, i) => {
      const x = (i / (series.length - 1)) * W;
      const y = H - (v / max) * (H - 4) - 2;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");

  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-base font-bold text-ink sm:text-lg">Охват за последние 30 дней</h2>
        <div role="tablist" className="flex gap-1 rounded-xl bg-surface-soft p-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={tab === t.id}
              onClick={() => setTab(t.id)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                tab === t.id ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" className="mt-5 h-40 w-full" role="img" aria-label={`График: ${TABS.find((t) => t.id === tab)?.label}`}>
        {[0.25, 0.5, 0.75].map((g) => (
          <line key={g} x1="0" x2={W} y1={H * g} y2={H * g} className="stroke-border" strokeWidth="0.3" />
        ))}
        <polyline points={points} fill="none" className="stroke-brand" strokeWidth="1.2" strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
      </svg>
    </div>
  );
}
```

- [ ] **Step 2: Подключить в Overview.tsx** — добавить `<ReachChart chart={data.chart} />` после `StatCards`.

```tsx
// фрагмент Overview.tsx — добавить импорт и блок
import ReachChart from "./ReachChart";
// ...внутри return, после <StatCards .../>:
      <ReachChart chart={data.chart} />
```

- [ ] **Step 3: Проверка** — `npx tsc --noEmit` + `npx eslint` → 0 ошибок. Playwright: переключение табов меняет линию.

---

## Task 11: Обзор — AI-рекомендации + неделя + активность

**Files:** Create `components/dashboard/overview/AiTips.tsx`, `components/dashboard/overview/WeekPreview.tsx`, `components/dashboard/overview/ActivityFeed.tsx`; Modify `components/dashboard/overview/Overview.tsx`

**Interfaces:**
- Consumes: `AiTip`, `PlanDay`, `PostStatus`, `ActivityItem`, `AccentColor` Task 1; `CHANNELS` из `@/lib/channels`.
- Produces: `AiTips` (`{ tips: AiTip[] }`), `WeekPreview` (`{ week: PlanDay[] }`), `ActivityFeed` (`{ items: ActivityItem[] }`).

- [ ] **Step 1: AiTips.tsx** — заголовок «Рекомендации AI», 3 карточки (адаптив: 1 кол мобайл, 3 десктоп). Цветная точка-приоритет (по `tip.color`), заголовок, текст, кнопка-ссылка «Перейти».

```tsx
// components/dashboard/overview/AiTips.tsx
import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import type { AccentColor, AiTip } from "@/lib/dashboard/types";

const DOT: Record<AccentColor, string> = {
  brand: "bg-brand",
  purple: "bg-brand-purple",
  pink: "bg-brand-pink",
  orange: "bg-brand-orange",
  success: "bg-success",
};

export default function AiTips({ tips }: { tips: AiTip[] }) {
  return (
    <div>
      <h2 className="mb-3 flex items-center gap-2 text-base font-bold text-ink sm:text-lg">
        <Sparkles size={18} className="text-brand" aria-hidden="true" />
        Рекомендации AI
      </h2>
      <div className="grid gap-3 lg:grid-cols-3">
        {tips.map((t) => (
          <div key={t.id} className="flex flex-col rounded-[20px] border border-border bg-card p-4 shadow-soft">
            <p className="flex items-start gap-2 text-sm font-semibold text-ink">
              <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${DOT[t.color]}`} aria-hidden="true" />
              {t.title}
            </p>
            <p className="mt-1.5 pl-4 text-xs leading-relaxed text-ink-muted">{t.text}</p>
            <Link href={t.href} className="btn-glass-blue mt-4 inline-flex items-center justify-center gap-1.5 rounded-xl px-4 py-2.5 text-xs font-semibold">
              Перейти <ArrowRight size={14} aria-hidden="true" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: WeekPreview.tsx** — заголовок «Контент-план» + ссылка «Все посты →» на `/dashboard/content`. Лента 7 дней (горизонтальный скролл на мобиле): день недели, число, статус-точка, иконки каналов из `CHANNELS`. Легенда статусов.

```tsx
// components/dashboard/overview/WeekPreview.tsx
import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { PlanDay, PostStatus } from "@/lib/dashboard/types";
import { CHANNELS } from "@/lib/channels";

const STATUS_DOT: Record<PostStatus, string> = {
  published: "bg-success",
  scheduled: "bg-brand",
  draft: "bg-ink-muted",
  none: "bg-transparent",
};

export default function WeekPreview({ week }: { week: PlanDay[] }) {
  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-bold text-ink sm:text-lg">Контент-план</h2>
        <Link href="/dashboard/content" className="inline-flex items-center gap-1 text-sm font-medium text-brand hover:text-brand-hover">
          Все посты <ArrowRight size={14} aria-hidden="true" />
        </Link>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {week.map((d) => (
          <div key={d.day} className="flex min-w-[84px] flex-1 flex-col items-center gap-2 rounded-2xl border border-border bg-surface-soft px-2 py-3">
            <span className="text-xs text-ink-muted">{d.weekday}</span>
            <span className="font-display text-lg font-bold text-ink">{d.day}</span>
            <span className={`h-2 w-2 rounded-full ${STATUS_DOT[d.status]}`} aria-hidden="true" />
            <span className="flex h-5 items-center gap-1">
              {d.channels.map((id) => {
                const ch = CHANNELS[id];
                return ch.icon && ch.iconType !== "wordmark" ? (
                  <Image key={id} src={ch.icon} alt={ch.label} width={16} height={16} className="h-4 w-4 object-contain" />
                ) : null;
              })}
            </span>
          </div>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
        <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-success" /> Опубликован</span>
        <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-brand" /> Запланирован</span>
        <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-ink-muted" /> Черновик</span>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: ActivityFeed.tsx** — заголовок «Недавняя активность», список событий с цветным маркером слева и временем справа.

```tsx
// components/dashboard/overview/ActivityFeed.tsx
import type { AccentColor, ActivityItem } from "@/lib/dashboard/types";

const BORDER: Record<AccentColor, string> = {
  brand: "border-l-brand",
  purple: "border-l-brand-purple",
  pink: "border-l-brand-pink",
  orange: "border-l-brand-orange",
  success: "border-l-success",
};

export default function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
      <h2 className="mb-4 text-base font-bold text-ink sm:text-lg">Недавняя активность</h2>
      <ul className="flex flex-col gap-2.5">
        {items.map((a) => (
          <li key={a.id} className={`flex items-center justify-between gap-3 rounded-xl border-l-2 bg-surface-soft px-4 py-3 ${BORDER[a.color]}`}>
            <span className="text-sm text-ink">{a.text}</span>
            <span className="shrink-0 text-xs text-ink-muted">{a.time}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

- [ ] **Step 4: Подключить в Overview.tsx** — финальная композиция блоков по порядку.

```tsx
// Overview.tsx — финальный return
import AiTips from "./AiTips";
import WeekPreview from "./WeekPreview";
import ActivityFeed from "./ActivityFeed";
// ...
  return (
    <div className="flex flex-col gap-6 sm:gap-8">
      <OverviewHeader businessName={data.businessName} />
      <StatCards stats={data.stats} />
      <ReachChart chart={data.chart} />
      <AiTips tips={data.tips} />
      <div className="grid gap-6 lg:grid-cols-2">
        <WeekPreview week={data.week} />
        <ActivityFeed items={data.activity} />
      </div>
    </div>
  );
```

- [ ] **Step 5: Проверка** — `npx tsc --noEmit` + `npx eslint` → 0 ошибок.

---

## Task 12: Финальная визуальная проверка

**Files:** —

- [ ] **Step 1:** Playwright десктоп (~1280), light и dark: `/dashboard` — все блоки (приветствие, статы, график, AI-рекомендации, неделя, активность); табы графика; переходы по сайдбару на заглушки `/dashboard/{content,promos,reviews,chatbot}` и обратно; дропдаун переключателя проекта.
- [ ] **Step 2:** Мобайл (~390): bottom-nav виден и фиксирован, контент не перекрыт; статы 2×2; график на всю ширину; неделя — горизонтальный скролл; переход по bottom-nav.
- [ ] **Step 3:** «Создать контент» и «Перейти» в AI-рекомендациях ведут на нужные заглушки; «Все посты →» → `/dashboard/content`.
- [ ] **Step 4:** Проверить отсутствие тёмных плашек в light, читаемость, контраст. `npx tsc --noEmit` + `npx eslint components/dashboard lib/dashboard app/dashboard` → 0 ошибок.

---

## Self-Review (для автора плана)

**Покрытие спеки:**
- Адаптивный шелл (топ-бар + сайдбар ↔ bottom-nav) → Task 5,6,7 ✓
- Переключатель проекта → Task 5 ✓
- 5 пунктов навигации + активность → Task 3,6 ✓
- Обзор: приветствие+CTA → Task 9; статы (Просмотры/Вовлечённость/Новые подписчики/Отзывы) → Task 2,9; график SVG с табами → Task 10; AI-рекомендации → Task 11; превью недели → Task 11; активность → Task 11 ✓
- Порядок блоков (аналитика → контент-план) → Task 11 Step 4 ✓
- Заглушки разделов + create → Task 8 ✓
- Слой данных из «мозга бренда» (sessionStorage) → Task 2,4 ✓
- Мобайл-фёрст (2×2 статы, bottom-nav, нижний отступ, скролл недели) → Task 6,7,9,11 ✓
- Темы/доступность/проверка → Global Constraints + Task 12 ✓

**Типы/сигнатуры консистентны:** `DashboardData`, `Stat`, `StatIcon`, `AccentColor`, `ChartTab`, `AiTip`, `PlanDay`, `PostStatus`, `ActivityItem`, `getDashboardData`, `useDashboard({data,hydrated})`, `NAV_ITEMS`/`isNavActive` — совпадают между задачами ✓

**Открытые мелочи для исполнителя:**
- Подтвердить экспорт/пути `ThemeToggle` и лого по факту чтения (Task 5) — ожидается `/logo-wordmark.webp` + `/brand/logo-lighttext.webp`, `ThemeToggle` default export.
- `app/dashboard/page.tsx` сейчас содержит старую заглушку «Дашборд скоро» — заменяется в Task 9 Step 4.
