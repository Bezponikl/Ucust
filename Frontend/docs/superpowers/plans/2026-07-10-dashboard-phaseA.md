# Dashboard Polish — Фаза A (аудит-фиксы) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Закрыть аудит-пункты 10.1–10.9 по дашборду: единый StatCard, цвет-кодирование срочности, читаемость данных, UX-мелочи.

**Architecture:** Один переиспользуемый `StatCard` заменяет три реализации; правки точечные в существующих экранах и мок-данных. Дизайн-язык и токены — текущие.

**Tech Stack:** Next.js 16, React 19, Tailwind v4 (токены), Solar-иконки `../ui/Icon`.

## Global Constraints

- Русская копия verbatim; цвета — только токены, без сырых hex. Янтарный = `brand-orange` (токена `--warning` в проекте нет).
- Не ломать функциональность; следовать текущим паттернам.
- Нет юнит-тестов → верификация: `npx tsc --noEmit` + Playwright визуал на dev (демо-вход → `/dashboard`). **Не** запускать `npm run build` при активном dev-сервере.
- Git есть (ветка `dashboard-polish`): коммит после каждой задачи. `git -c user.name="UCust" -c user.email="dev@ucust.online" commit`.
- Демо-вход: `/` → «Войти» (seedDemoProject) → `/dashboard`. Разделы: `/dashboard`, `/dashboard/analytics`, `/dashboard/promos`, `/dashboard/content`, `/dashboard/inbox`.

---

## Task 1: Единый компонент `StatCard`

**Files:**
- Create: `components/dashboard/StatCard.tsx`

**Interfaces:**
- Produces: default `StatCard` с пропсами `{ icon: IconName; iconTone?: StatTone; value: string; label: string; delta?: string; deltaTone?: DeltaTone; hint?: string; hintTone?: "muted" | "warning" }`. Экспортирует типы `StatTone`, `DeltaTone`.

- [ ] **Step 1: Создать компонент**

```tsx
import Icon from "./ui/Icon";
import type { IconName } from "@/lib/icons/solar";

export type StatTone = "brand" | "purple" | "pink" | "orange" | "success";
export type DeltaTone = StatTone | "warning" | "muted";

const ICON_BG: Record<StatTone, string> = {
  brand: "bg-brand/12 text-brand",
  purple: "bg-brand-purple/15 text-brand-purple",
  pink: "bg-brand-pink/15 text-brand-pink",
  orange: "bg-brand-orange/15 text-brand-orange",
  success: "bg-success/15 text-success",
};

const TEXT_TONE: Record<DeltaTone, string> = {
  brand: "text-brand",
  purple: "text-brand-purple",
  pink: "text-brand-pink",
  orange: "text-brand-orange",
  success: "text-success",
  warning: "text-brand-orange",
  muted: "text-ink-muted",
};

export default function StatCard({
  icon,
  iconTone = "brand",
  value,
  label,
  delta,
  deltaTone = "success",
  hint,
  hintTone = "muted",
}: {
  icon: IconName;
  iconTone?: StatTone;
  value: string;
  label: string;
  delta?: string;
  deltaTone?: DeltaTone;
  hint?: string;
  hintTone?: "muted" | "warning";
}) {
  return (
    <div className="rounded-[20px] border border-border bg-card p-4 shadow-soft sm:p-5">
      <span className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl ${ICON_BG[iconTone]}`}>
        <Icon name={icon} size={18} aria-hidden="true" />
      </span>
      <p className="flex items-baseline gap-2">
        <span className="font-display text-2xl font-extrabold text-ink">{value}</span>
        {delta && <span className={`text-xs font-semibold ${TEXT_TONE[deltaTone]}`}>{delta}</span>}
      </p>
      <p className="mt-0.5 text-sm font-medium text-ink">{label}</p>
      {hint && (
        <p className={`text-xs ${hintTone === "warning" ? "font-semibold text-brand-orange" : "text-ink-muted"}`}>
          {hint}
        </p>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 3: Commit**

```bash
git add components/dashboard/StatCard.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(dashboard): unified StatCard component"
```

---

## Task 2: Обзор → StatCard + янтарный статус отзывов (10.1, 10.3)

**Files:**
- Modify: `lib/dashboard/types.ts` (интерфейс `Stat` — добавить `hintTone?`)
- Modify: `lib/dashboard/mock.ts` (reviews-стат → `hintTone: "warning"`)
- Modify: `components/dashboard/overview/StatCards.tsx` (рендер через `StatCard`)

**Interfaces:**
- Consumes: `StatCard`, `StatTone` из Task 1.
- Produces: `Stat.hintTone?: "warning"` — читается `StatCards`.

- [ ] **Step 1: Добавить `hintTone` в тип `Stat`**

В `lib/dashboard/types.ts`, в интерфейс `Stat` добавить поле (после `color`):

```ts
export interface Stat {
  id: string;
  label: string;
  value: string;
  hint: string;
  delta?: string;
  icon: StatIcon;
  color: AccentColor;
  hintTone?: "warning";
}
```

- [ ] **Step 2: Пометить карточку отзывов срочной**

В `lib/dashboard/mock.ts` заменить строку reviews-стата:

```ts
      { id: "reviews", label: "Отзывы", value: "47", hint: "Требуют внимания", icon: "reviews", color: "orange" },
```

на:

```ts
      { id: "reviews", label: "Отзывы", value: "47", hint: "Требуют внимания", icon: "reviews", color: "orange", hintTone: "warning" },
```

- [ ] **Step 3: Переписать StatCards через StatCard**

Заменить всё содержимое `components/dashboard/overview/StatCards.tsx`:

```tsx
import StatCard from "../StatCard";
import type { IconName } from "@/lib/icons/solar";
import type { Stat, StatIcon } from "@/lib/dashboard/types";

const ICONS: Record<StatIcon, IconName> = {
  views: "eye",
  engagement: "trending",
  subscribers: "user-plus",
  reviews: "message",
};

export default function StatCards({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
      {stats.map((s) => (
        <StatCard
          key={s.id}
          icon={ICONS[s.icon]}
          iconTone={s.color}
          value={s.value}
          label={s.label}
          delta={s.delta}
          hint={s.hint}
          hintTone={s.hintTone}
        />
      ))}
    </div>
  );
}
```

- [ ] **Step 4: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 5: Визуальная проверка**

Playwright: демо-вход → `/dashboard`. Подтвердить: 4 карточки статов через новый StatCard (иконка → число → лейбл), карточка «Отзывы» имеет подпись «Требуют внимания» янтарным (brand-orange), остальные — нейтральные. Светлая/тёмная.

- [ ] **Step 6: Commit**

```bash
git add lib/dashboard/types.ts lib/dashboard/mock.ts components/dashboard/overview/StatCards.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(dashboard): overview stats via StatCard + warning tone for reviews (10.1, 10.3)"
```

---

## Task 3: Аналитика → StatCard (10.1)

**Files:**
- Modify: `lib/dashboard/analytics.ts` (интерфейс `MetricCard` + данные — добавить `icon`)
- Modify: `components/dashboard/analytics/AnalyticsView.tsx` (метрики через `StatCard`)

**Interfaces:**
- Consumes: `StatCard`.
- Produces: `MetricCard.icon: IconName`.

- [ ] **Step 1: Добавить `icon` в `MetricCard` и данные**

В `lib/dashboard/analytics.ts`:

Изменить интерфейс:

```ts
import type { IconName } from "@/lib/icons/solar";

export interface MetricCard {
  id: string;
  label: string;
  value: string;
  delta: string;
  color: AccentColor;
  icon: IconName;
}
```

Изменить массив `METRICS`:

```ts
export const METRICS: MetricCard[] = [
  { id: "reach", label: "Охват", value: "48.2K", delta: "+22%", color: "brand", icon: "eye" },
  { id: "engagement", label: "Вовлечённость", value: "6.4%", delta: "+1.3 п.п.", color: "success", icon: "trending" },
  { id: "subscribers", label: "Подписчики", value: "3 412", delta: "+127", color: "purple", icon: "user-plus" },
  { id: "clicks", label: "Клики", value: "1 980", delta: "+18%", color: "orange", icon: "cursor" },
];
```

> Если иконки `cursor` нет в `lib/icons/solar.ts`, использовать `trending` для clicks. Проверить перед сохранением: `grep -oE '"cursor"' lib/icons/solar.ts`.

- [ ] **Step 2: Метрики через StatCard**

В `components/dashboard/analytics/AnalyticsView.tsx`:

Добавить импорт (рядом с другими):

```tsx
import StatCard from "@/components/dashboard/StatCard";
```

Удалить локальную карту `DELTA_TINT` (строки 16-22) — больше не нужна. Заодно удалить теперь-неиспользуемый импорт `import type { AccentColor } from "@/lib/dashboard/types";` (строка 6), иначе tsc/eslint ругнётся на unused. Импорт `ReachChart` и остальные оставить.

Заменить блок «Метрики» (сетка METRICS, ~строки 52-61) на:

```tsx
      {/* Метрики */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
        {METRICS.map((m) => (
          <StatCard
            key={m.id}
            icon={m.icon}
            iconTone={m.color}
            value={m.value}
            label={m.label}
            delta={m.delta}
            deltaTone={m.color}
          />
        ))}
      </div>
```

- [ ] **Step 3: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 4: Визуальная проверка**

Playwright: `/dashboard/analytics`. Подтвердить: карточки метрик теперь с иконками (как на Обзоре), дельта окрашена по тону метрики. Консистентно с Обзором.

- [ ] **Step 5: Commit**

```bash
git add lib/dashboard/analytics.ts components/dashboard/analytics/AnalyticsView.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(dashboard): analytics metrics via StatCard (10.1)"
```

---

## Task 4: Акции → StatCard + унификация метрики (10.2, 10.8)

**Files:**
- Modify: `lib/dashboard/promos.ts` (pr3 — единый лейбл метрики)
- Modify: `components/dashboard/promos/PromosView.tsx` (плашки через `StatCard`)

**Interfaces:**
- Consumes: `StatCard`, `StatTone`.
- Produces: нет новых.

- [ ] **Step 1: Унифицировать метрику запланированной акции (10.8)**

В `lib/dashboard/promos.ts`, объект `pr3`, заменить:

```ts
    metricLabel: "Охват анонса",
    metricValue: "—",
```

на:

```ts
    metricLabel: "Использований",
    metricValue: "—",
```

(Лейбл теперь единый во всех карточках; `—` читается как «ещё нет данных», а не другая метрика.)

- [ ] **Step 2: Плашки статусов через StatCard**

В `components/dashboard/promos/PromosView.tsx`:

Добавить импорт:

```tsx
import StatCard from "@/components/dashboard/StatCard";
import type { StatTone } from "@/components/dashboard/StatCard";
```

Заменить блок трёх плашек (сетка `grid-cols-3`, ~строки 40-51) на:

```tsx
      <div className="grid grid-cols-3 gap-3 sm:gap-4">
        {([
          { label: "Активные", value: counts.active, tone: "success", icon: "check-bold" },
          { label: "Запланированные", value: counts.scheduled, tone: "brand", icon: "calendar" },
          { label: "Завершённые", value: counts.finished, tone: "orange", icon: "check" },
        ] as { label: string; value: number; tone: StatTone; icon: IconName }[]).map((s) => (
          <StatCard key={s.label} icon={s.icon} iconTone={s.tone} value={String(s.value)} label={s.label} />
        ))}
      </div>
```

Добавить импорт типа иконки, если ещё нет:

```tsx
import type { IconName } from "@/lib/icons/solar";
```

- [ ] **Step 3: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 4: Визуальная проверка**

Playwright: `/dashboard/promos`. Подтвердить: три плашки статусов теперь с иконками (единый StatCard), карточка «День рождения кофейни» показывает лейбл «Использований» с `—` (как остальные). Консистентно.

- [ ] **Step 5: Commit**

```bash
git add lib/dashboard/promos.ts components/dashboard/promos/PromosView.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(dashboard): promo stat tiles via StatCard + unified metric label (10.2, 10.8)"
```

---

## Task 5: Ось Y на графике (10.9)

**Files:**
- Modify: `components/dashboard/overview/ReachChart.tsx` (подписи значений у линий сетки)

**Interfaces:**
- Consumes: существующие `fmt`, геометрия (`padL`, `padT`, `plotH`, `top`).
- Produces: нет новых.

- [ ] **Step 1: Добавить числовые подписи к линиям сетки**

В `components/dashboard/overview/ReachChart.tsx`, блок «Горизонтальные линии сетки» (`{[0, 0.5, 1].map((g) => { ... })}`) заменить на версию с подписью значения слева от каждой линии:

```tsx
        {/* Горизонтальные линии сетки + подписи значений оси Y */}
        {[0, 0.5, 1].map((g) => {
          const y = padT + g * plotH;
          const val = top * (1 - g); // g=0 → верх (max), g=1 → низ (0)
          return (
            <g key={g}>
              <line
                x1={padL}
                x2={padL + plotW}
                y1={y}
                y2={y}
                stroke="var(--border)"
                strokeWidth="1"
                strokeDasharray={g === 1 ? "0" : "3 5"}
              />
              <text x={padL} y={y - 4} fontSize="10" fill="var(--ink-muted)">
                {fmt(val)}
              </text>
            </g>
          );
        })}
```

> Подпись ставится над линией у левого края (`x=padL`), не мешает данным. `fmt(val)` даёт «0 / 5K / 10K»-подобные значения.

- [ ] **Step 2: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 3: Визуальная проверка**

Playwright: `/dashboard` (график в Обзоре) и `/dashboard/analytics` (большой график — тот же компонент). Подтвердить: у линий сетки видны опорные значения (низ ≈ 0, верх ≈ пик), не перегружает график, читается в обеих темах.

- [ ] **Step 4: Commit**

```bash
git add components/dashboard/overview/ReachChart.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(dashboard): Y-axis value labels on reach chart (10.9)"
```

---

## Task 6: Легенда статусов в grid-виде + лёгкий пустой слот (10.5, 10.6)

**Files:**
- Modify: `components/dashboard/content/ContentView.tsx` (легенда в grid-виде; высота `EmptyDayCard`)

**Interfaces:**
- Consumes: существующие `STATUS_DOT`, `STATUS_LABEL`.
- Produces: нет новых.

- [ ] **Step 1: Добавить легенду статусов в grid-вид (10.5)**

В `ContentView.tsx`, отрисовка grid — сейчас `{view === "grid" && <FeedGrid ... />}`. Заменить на обёртку с легендой над сеткой:

```tsx
      {view === "grid" && (
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-success" /> Опубликован</span>
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-brand" /> Запланирован</span>
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-ink-muted" /> Черновик</span>
          </div>
          <FeedGrid byDay={byDay} onOpen={setEditing} passes={passes} />
        </div>
      )}
```

(Легенда идентична той, что уже есть в календарном виде — статусные точки теперь пояснены и в сетке.)

- [ ] **Step 2: Облегчить пустой слот (10.6)**

В `ContentView.tsx`, компонент `EmptyDayCard` — уменьшить фиксированную высоту `min-h-[220px]` до компактной и убрать «раздутость». Заменить его `<Link>` className:

```tsx
      className="group flex h-full min-h-[140px] flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-border bg-surface-soft/40 p-4 text-center transition hover:border-brand hover:bg-brand/5"
```

И уменьшить внутренние размеры иконки-кнопки (следующий `<span>`):

```tsx
      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand/10 text-brand transition group-hover:scale-105 group-hover:bg-brand/15">
        <Icon name="plus" size={18} aria-hidden="true" />
      </span>
```

> Пустой слот станет заметно ниже и легче; в CSS-grid он всё ещё выровняется по высоте ряда, но перестанет выглядеть «переразмеренным» с большим пустым центром.

- [ ] **Step 3: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 4: Визуальная проверка**

Playwright: `/dashboard/content`. В виде «Сетка»: над карточками видна легенда статусов; пустые слоты «Запланировать» компактнее и не выглядят раздутыми. Переключить на «Месяц» — легенда там осталась.

- [ ] **Step 5: Commit**

```bash
git add components/dashboard/content/ContentView.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(dashboard): status legend in grid view + lighter empty slot (10.5, 10.6)"
```

---

## Task 7: Название проекта + рейтинг во Входящих (10.4, 10.7)

**Files:**
- Modify: `components/dashboard/ProjectSwitcher.tsx` (шире триггер)
- Modify: `components/dashboard/inbox/InboxView.tsx` (усилить звёзды у отзывов)

**Interfaces:**
- Consumes: существующие.
- Produces: нет новых.

- [ ] **Step 1: Расширить триггер переключателя проекта (10.4)**

В `components/dashboard/ProjectSwitcher.tsx`, у кнопки-триггера заменить классы ширины:

```tsx
        className="flex min-w-0 max-w-[220px] items-center gap-2 rounded-full border border-border bg-surface-soft px-2.5 py-1.5 text-left sm:max-w-[240px] sm:px-3"
```

на:

```tsx
        className="flex min-w-0 max-w-[240px] items-center gap-2 rounded-full border border-border bg-surface-soft px-2.5 py-1.5 text-left sm:max-w-[300px] sm:px-3"
```

(Больше места под название до обрезки; `truncate` остаётся страховкой для очень длинных имён.)

- [ ] **Step 2: Усилить рейтинг у отзывов в списке Входящих (10.7)**

В `components/dashboard/inbox/InboxView.tsx`, компонент `Stars` — увеличить размер и добавить опцию заметности. Заменить `Stars`:

```tsx
function Stars({ rating, size = 12 }: { rating: number; size?: number }) {
  return (
    <span className="inline-flex items-center gap-0.5" aria-label={`${rating} из 5`}>
      {Array.from({ length: 5 }, (_, i) => (
        <Icon key={i} name={i < rating ? "star-bold" : "star"} size={size} className={i < rating ? "text-brand-orange" : "text-ink-muted/40"} aria-hidden="true" />
      ))}
    </span>
  );
}
```

В карточке списка (строка с `SourceBadge` + `KIND_LABEL` + `Stars`), для отзывов вынести рейтинг на отдельную заметную строку. Заменить блок мета-ряда:

```tsx
                    <div className="mt-1 flex items-center gap-2">
                      <SourceBadge item={i} />
                      <span className="rounded-full bg-surface-soft px-1.5 py-0.5 text-[10px] text-ink-muted">{KIND_LABEL[i.kind]}</span>
                      {i.rating != null && <Stars rating={i.rating} />}
                    </div>
```

на:

```tsx
                    <div className="mt-1 flex items-center gap-2">
                      <SourceBadge item={i} />
                      <span className="rounded-full bg-surface-soft px-1.5 py-0.5 text-[10px] text-ink-muted">{KIND_LABEL[i.kind]}</span>
                    </div>
                    {i.rating != null && (
                      <div className="mt-1.5 flex items-center gap-1.5">
                        <Stars rating={i.rating} size={15} />
                        <span className="text-xs font-semibold text-brand-orange">{i.rating}.0</span>
                      </div>
                    )}
```

(Рейтинг теперь на своей строке, крупнее (15px) + числовой акцент — отзыв визуально отличается от диалогового сообщения.)

- [ ] **Step 3: Тип-чек**

Run: `npx tsc --noEmit`
Expected: без ошибок.

- [ ] **Step 4: Визуальная проверка**

Playwright: открыть переключатель проекта в шапке — длинное название («Кофейня "Тёплый день"») помещается без «…» (или обрезается заметно меньше). `/dashboard/inbox`, фильтр «Отзывы»: у отзывов рейтинг-звёзды крупнее и с числом, отзыв заметно отличается от сообщения.

- [ ] **Step 5: Commit**

```bash
git add components/dashboard/ProjectSwitcher.tsx components/dashboard/inbox/InboxView.tsx
git -c user.name="UCust" -c user.email="dev@ucust.online" commit -m "feat(dashboard): wider project name + prominent review rating (10.4, 10.7)"
```

---

## Финальная верификация (после всех задач)

- [ ] `npx tsc --noEmit` — чисто.
- [ ] Playwright обход (демо-вход, светлая/тёмная, 1440 и 375): единый StatCard на Обзоре/Аналитике/Акциях; янтарный «Требуют внимания»; ось Y на графике; легенда статусов в сетке Контента; компактные пустые слоты; название проекта не обрезано; рейтинг отзывов заметен.
- [ ] Не деплоить. Не запускать `npm run build` при активном dev-сервере.
- [ ] `SectionStub.tsx` можно удалить, если после Фазы A он всё ещё неиспользуем (проверить `grep -r SectionStub components/`), — опционально, не в этой фазе.
```
